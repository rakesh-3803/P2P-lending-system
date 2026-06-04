from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.investment_model import Investment
from app.models.notification_model import Notification

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

    # ONLY BORROWER
    check_role(user, ["BORROWER"])

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

    # NOTIFICATION
    notification = Notification(
        user_id=user["user_id"],
        message="Loan application submitted"
    )

    db.add(notification)

    db.commit()

    db.refresh(new_loan)

    return {
        "message": "Loan applied successfully",
        "loan_id": new_loan.id
    }


# =========================================
# MY LOANS
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
# REPAY LOAN
# =========================================

@router.put("/repay-loan/{loan_id}")
def repay_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    # FIND LOAN
    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:

        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    # CHECK STATUS
    if loan.status != "APPROVED":

        raise HTTPException(
            status_code=400,
            detail="Loan already repaid or invalid"
        )

    # TOTAL REPAYMENT
    total_repayment = (
        loan.amount +
        (loan.amount * loan.interest_rate / 100)
    )

    # BORROWER WALLET
    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not borrower_wallet:

        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    # CHECK BALANCE
    if borrower_wallet.balance < total_repayment:

        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    # DEDUCT BORROWER MONEY
    borrower_wallet.balance -= total_repayment

    # FIND INVESTMENTS
    investments = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).all()

    # DISTRIBUTE MONEY TO LENDERS
    for investment in investments:

        lender_wallet = db.query(Wallet).filter(
            Wallet.user_id == investment.lender_id
        ).first()

        if lender_wallet:

            lender_return = (
                investment.amount +
                (
                    investment.amount *
                    loan.interest_rate / 100
                )
            )

            lender_wallet.balance += lender_return

            db.add(lender_wallet)

            # TRANSACTION
            lender_transaction = Transaction(
                user_id=investment.lender_id,
                amount=lender_return,
                transaction_type="CREDIT",
                description="Loan repayment received"
            )

            db.add(lender_transaction)

            # NOTIFICATION
            lender_notification = Notification(
                user_id=investment.lender_id,
                message=f"₹{lender_return} repayment received"
            )

            db.add(lender_notification)

    # MARK COMPLETED
    loan.status = "COMPLETED"

    # BORROWER TRANSACTION
    borrower_transaction = Transaction(
        user_id=user["user_id"],
        amount=total_repayment,
        transaction_type="DEBIT",
        description="Loan repayment"
    )

    db.add(borrower_transaction)

    # BORROWER NOTIFICATION
    borrower_notification = Notification(
        user_id=user["user_id"],
        message="Loan repaid successfully"
    )

    db.add(borrower_notification)

    db.commit()

    return {
        "message": "Loan repaid successfully",
        "total_paid": total_repayment
    }
# =========================================
# GET APPROVED LOANS FOR LENDERS
# =========================================

@router.get("/approved-loans")
def get_approved_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    loans = db.query(Loan).filter(
        Loan.status == "APPROVED"
    ).all()

    return loans