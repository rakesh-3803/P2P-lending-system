from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.notification_model import Notification

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


# =========================================
# REPAY LOAN
# =========================================

@router.post("/repay-loan/{loan_id}")
def repay_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    # Only borrower
    check_role(user, ["BORROWER"])

    # Find loan
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.borrower_id == user["user_id"]
    ).first()

    if not loan:

        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    # Only approved loans
    if loan.status != "APPROVED":

        raise HTTPException(
            status_code=400,
            detail="Loan is not approved"
        )

    # Calculate repayment
    interest_amount = (
        loan.amount * loan.interest_rate
    ) / 100

    total_repayment = (
        loan.amount + interest_amount
    )

    # Get borrower wallet
    wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not wallet:

        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    # Check balance
    if wallet.balance < total_repayment:

        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    # Deduct amount
    wallet.balance -= total_repayment

    # Mark loan completed
    loan.status = "COMPLETED"

    # Transaction entry
    transaction = Transaction(
        user_id=user["user_id"],
        amount=total_repayment,
        transaction_type="DEBIT",
        description="Loan repayment"
    )

    db.add(transaction)

    # Notification
    notification = Notification(
        user_id=user["user_id"],
        message="Loan repayment successful"
    )

    db.add(notification)

    db.commit()

    return {
        "message": "Loan repaid successfully",
        "amount_paid": total_repayment,
        "remaining_balance": wallet.balance
    }