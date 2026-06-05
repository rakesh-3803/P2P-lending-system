from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.investment_model import Investment
from app.models.notification_model import Notification
from app.models.borrower_profile_model import BorrowerProfile

from app.schemas.loan_schema import LoanCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role


router = APIRouter()


# =========================================
# APPLY LOAN
# =========================================

@router.post("/apply-loan")
def apply_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    # CHECK PROFILE
    profile = db.query(
        BorrowerProfile
    ).filter(
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

    # CREATE LOAN
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

# =========================================
# BORROWER LOANS
# =========================================

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


# =========================================
# APPROVED LOANS FOR LENDERS
# =========================================

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


# =========================================
# REPAY LOAN
# =========================================

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

    # MUST BE FUNDED BEFORE REPAYMENT
    if loan.status != "FUNDED":

        raise HTTPException(
            status_code=400,
            detail="Loan is not funded or already repaid"
        )

    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not borrower_wallet:

        raise HTTPException(
            status_code=404,
            detail="Borrower wallet not found"
        )

    total_repayment = (
        loan.amount +
        (loan.amount * loan.interest_rate / 100)
    )

    if borrower_wallet.balance < total_repayment:

        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    borrower_wallet.balance -= total_repayment

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

    lender_return = (
        investment.amount +
        (
            investment.amount *
            loan.interest_rate / 100
        )
    )

    lender_wallet.balance += lender_return

    # TRANSACTIONS

    borrower_transaction = Transaction(
        user_id=user["user_id"],
        amount=total_repayment,
        transaction_type="DEBIT",
        description="Loan repayment"
    )

    lender_transaction = Transaction(
        user_id=investment.lender_id,
        amount=lender_return,
        transaction_type="CREDIT",
        description="Loan repayment received"
    )

    db.add(borrower_transaction)
    db.add(lender_transaction)

    # NOTIFICATIONS

    borrower_notification = Notification(
        user_id=user["user_id"],
        message="Loan repaid successfully"
    )

    lender_notification = Notification(
        user_id=investment.lender_id,
        message=f"₹{lender_return} credited from borrower repayment"
    )

    db.add(borrower_notification)
    db.add(lender_notification)

    # MARK COMPLETED

    loan.status = "COMPLETED"

    db.commit()

    return {
        "message": "Loan repaid successfully",
        "total_paid": total_repayment,
        "lender_received": lender_return
    }