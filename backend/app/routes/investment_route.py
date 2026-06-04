from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.investment_model import Investment
from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.notification_model import Notification

from app.schemas.investment_schema import InvestmentCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


# =========================================
# INVEST IN LOAN
# =========================================

@router.post("/invest")
def invest_in_loan(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    # FIND LOAN
    loan = db.query(Loan).filter(
        Loan.id == investment.loan_id
    ).first()

    if not loan:

        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    # ONLY APPROVED LOANS
    if loan.status != "APPROVED":

        raise HTTPException(
            status_code=400,
            detail="Loan not approved"
        )

    # LENDER WALLET
    lender_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not lender_wallet:

        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    # CHECK BALANCE
    if lender_wallet.balance < investment.amount:

        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    # CREATE INVESTMENT
    new_investment = Investment(
        lender_id=user["user_id"],
        loan_id=investment.loan_id,
        amount=investment.amount
    )

    db.add(new_investment)

    # DEDUCT LENDER MONEY
    lender_wallet.balance -= investment.amount

    # CREDIT BORROWER
    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == loan.borrower_id
    ).first()

    if borrower_wallet:

        borrower_wallet.balance += investment.amount

    # TRANSACTION
    transaction = Transaction(
        user_id=user["user_id"],
        amount=investment.amount,
        transaction_type="DEBIT",
        description="Loan investment"
    )

    db.add(transaction)

    # NOTIFICATION
    notification = Notification(
        user_id=loan.borrower_id,
        message=f"₹{investment.amount} invested in your loan"
    )

    db.add(notification)

    # VERY IMPORTANT
    db.commit()

    db.refresh(new_investment)

    return {
        "message": "Investment successful",
        "investment_id": new_investment.id,
        "remaining_balance": lender_wallet.balance
    }