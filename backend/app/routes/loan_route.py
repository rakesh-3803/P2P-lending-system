from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.investment_model import Investment
from app.models.notification_model import Notification
from app.models.borrower_profile_model import BorrowerProfile
from app.models.emi_model import EMI

from app.schemas.loan_schema import LoanCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role


router = APIRouter()


@router.post("/apply-loan")
def apply_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Complete borrower profile before applying for loan"
        )

    if not profile.profile_completed:
        raise HTTPException(
            status_code=400,
            detail="Borrower profile not completed"
        )

    new_loan = Loan(
        borrower_id=user["user_id"],
        amount=loan.amount,
        interest_rate=loan.interest_rate,
        tenure_months=loan.tenure_months,
        purpose=loan.purpose,
        status="PENDING"
    )

    db.add(new_loan)

    notification = Notification(
        user_id=user["user_id"],
        message="Loan application submitted successfully"
    )

    db.add(notification)

    db.commit()
    db.refresh(new_loan)

    return {
        "message": "Loan applied successfully",
        "loan_id": new_loan.id
    }


@router.get("/my-loans")
def my_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    loans = db.query(Loan).filter(
        Loan.borrower_id == user["user_id"]
    ).all()

    return loans


@router.get("/approved-loans")
def approved_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    loans = db.query(Loan).filter(
        Loan.status == "APPROVED"
    ).all()

    return loans


@router.get("/my-emis")
def my_emis(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    emis = db.query(EMI).filter(
        EMI.borrower_id == user["user_id"]
    ).all()

    return emis


@router.put("/pay-emi/{emi_id}")
def pay_emi(
    emi_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    emi = db.query(EMI).filter(
        EMI.id == emi_id,
        EMI.borrower_id == user["user_id"]
    ).first()

    if not emi:
        raise HTTPException(
            status_code=404,
            detail="EMI not found"
        )

    if emi.status == "PAID":
        raise HTTPException(
            status_code=400,
            detail="EMI already paid"
        )

    loan = db.query(Loan).filter(
        Loan.id == emi.loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "FUNDED":
        raise HTTPException(
            status_code=400,
            detail="Loan is not active"
        )

    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not borrower_wallet:
        raise HTTPException(
            status_code=404,
            detail="Borrower wallet not found"
        )

    if borrower_wallet.balance < emi.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    investment = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).first()

    if not investment:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    lender_wallet = db.query(Wallet).filter(
        Wallet.user_id == investment.lender_id
    ).first()

    if not lender_wallet:
        raise HTTPException(
            status_code=404,
            detail="Lender wallet not found"
        )

    borrower_wallet.balance -= emi.amount
    lender_wallet.balance += emi.amount

    emi.status = "PAID"

    borrower_transaction = Transaction(
        user_id=user["user_id"],
        amount=emi.amount,
        transaction_type="DEBIT",
        description=f"EMI {emi.emi_number} payment"
    )

    lender_transaction = Transaction(
        user_id=investment.lender_id,
        amount=emi.amount,
        transaction_type="CREDIT",
        description=f"EMI {emi.emi_number} received"
    )

    db.add(borrower_transaction)
    db.add(lender_transaction)

    borrower_notification = Notification(
        user_id=user["user_id"],
        message=f"EMI {emi.emi_number} paid successfully"
    )

    lender_notification = Notification(
        user_id=investment.lender_id,
        message=f"EMI {emi.emi_number} amount ₹{emi.amount} received"
    )

    db.add(borrower_notification)
    db.add(lender_notification)

    borrower_profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    updated_credit_score = None

    if borrower_profile:
        borrower_profile.credit_score += 5

        if borrower_profile.credit_score > 900:
            borrower_profile.credit_score = 900

        updated_credit_score = borrower_profile.credit_score

        db.add(borrower_profile)

    pending_emis = db.query(EMI).filter(
        EMI.loan_id == loan.id,
        EMI.status == "PENDING"
    ).count()

    if pending_emis == 0:
        loan.status = "COMPLETED"

        completion_notification = Notification(
            user_id=user["user_id"],
            message="All EMIs paid. Loan completed successfully."
        )

        db.add(completion_notification)

    db.commit()

    return {
        "message": "EMI paid successfully",
        "emi_id": emi.id,
        "emi_number": emi.emi_number,
        "amount_paid": emi.amount,
        "loan_status": loan.status,
        "updated_credit_score": updated_credit_score
    }


@router.put("/repay-loan/{loan_id}")
def repay_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.borrower_id != user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    if loan.status != "FUNDED":
        raise HTTPException(
            status_code=400,
            detail="Loan is not active"
        )

    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not borrower_wallet:
        raise HTTPException(
            status_code=404,
            detail="Borrower wallet not found"
        )

    investment = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).first()

    if not investment:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    lender_wallet = db.query(Wallet).filter(
        Wallet.user_id == investment.lender_id
    ).first()

    if not lender_wallet:
        raise HTTPException(
            status_code=404,
            detail="Lender wallet not found"
        )

    pending_emis = db.query(EMI).filter(
        EMI.loan_id == loan.id,
        EMI.status == "PENDING"
    ).all()

    remaining_amount = sum(
        emi.amount for emi in pending_emis
    )

    if remaining_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Loan already fully repaid"
        )

    if borrower_wallet.balance < remaining_amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    borrower_wallet.balance -= remaining_amount
    lender_wallet.balance += remaining_amount

    for emi in pending_emis:
        emi.status = "PAID"

    loan.status = "COMPLETED"

    borrower_profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    updated_credit_score = None

    if borrower_profile:
        borrower_profile.credit_score += 20

        if borrower_profile.credit_score > 900:
            borrower_profile.credit_score = 900

        updated_credit_score = borrower_profile.credit_score

        db.add(borrower_profile)

    borrower_transaction = Transaction(
        user_id=user["user_id"],
        amount=remaining_amount,
        transaction_type="DEBIT",
        description="Full loan settlement"
    )

    lender_transaction = Transaction(
        user_id=investment.lender_id,
        amount=remaining_amount,
        transaction_type="CREDIT",
        description="Early loan settlement received"
    )

    db.add(borrower_transaction)
    db.add(lender_transaction)

    borrower_notification = Notification(
        user_id=user["user_id"],
        message="Loan settled successfully. All pending EMIs have been closed."
    )

    lender_notification = Notification(
        user_id=investment.lender_id,
        message=f"₹{remaining_amount} received as full loan settlement."
    )

    db.add(borrower_notification)
    db.add(lender_notification)

    db.commit()

    return {
        "message": "Loan settled successfully",
        "remaining_amount_paid": remaining_amount,
        "loan_status": loan.status,
        "updated_credit_score": updated_credit_score
    }