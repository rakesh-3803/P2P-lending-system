from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.db_dependency import get_db

from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.notification_model import Notification
from app.models.bank_account_model import BankAccount

from app.auth.auth_bearer import verify_token

router = APIRouter()


# =========================================
# REQUEST MODEL
# =========================================

class AddMoneyRequest(BaseModel):

    amount: float

class WithdrawRequest(BaseModel):

    amount: float


# =========================================
# GET WALLET
# =========================================

@router.get("/wallet")
def get_wallet(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not wallet:

        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    return wallet


# =========================================
# ADD MONEY
# =========================================

@router.post("/wallet/add-money")
def add_money(
    request: AddMoneyRequest,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not wallet:

        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    # Add balance
    wallet.balance += request.amount

    # Create transaction
    transaction = Transaction(
        user_id=user["user_id"],
        amount=request.amount,
        transaction_type="CREDIT",
        description="Wallet top-up"
    )

    db.add(transaction)

    db.commit()

    return {
        "message": "Money added successfully",
        "updated_balance": wallet.balance
    }
# =========================================
# WITHDRAW MONEY
# =========================================

@router.post("/wallet/withdraw")
def withdraw_money(
    request: WithdrawRequest,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    bank_account = db.query(BankAccount).filter(
        BankAccount.user_id == user["user_id"]
    ).first()

    if not bank_account:
        raise HTTPException(
            status_code=404,
            detail="Please link your bank account first"
        )

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    if wallet.balance < request.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    wallet.balance -= request.amount

    bank_account.balance += request.amount

    transaction = Transaction(
        user_id=user["user_id"],
        amount=request.amount,
        transaction_type="DEBIT",
        description="Wallet withdrawal to bank account"
    )

    db.add(transaction)

    notification = Notification(
        user_id=user["user_id"],
        message=f"₹{request.amount} withdrawn to bank account"
    )

    db.add(notification)

    db.commit()

    return {
        "message": "Withdrawal successful",
        "withdrawn_amount": request.amount,
        "wallet_balance": wallet.balance,
        "bank_balance": bank_account.balance
    }