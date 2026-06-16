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


class AddMoneyRequest(BaseModel):
    amount: float


class WithdrawRequest(BaseModel):
    amount: float


class WalletUpdateRequest(BaseModel):
    amount: float
    action: str   # ADD or WITHDRAW


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


@router.put("/wallet/update-balance")
def update_wallet_balance(
    request: WalletUpdateRequest,
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

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than 0"
        )

    action = request.action.upper()

    if action not in ["ADD", "WITHDRAW"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Use ADD or WITHDRAW"
        )

    if action == "ADD":

        wallet.balance += request.amount

        transaction = Transaction(
            user_id=user["user_id"],
            amount=request.amount,
            transaction_type="CREDIT",
            description="Wallet top-up"
        )

        notification = Notification(
            user_id=user["user_id"],
            message=f"₹{request.amount} added to wallet successfully"
        )

        db.add(transaction)
        db.add(notification)

        db.commit()

        return {
            "message": "Money added successfully",
            "action": "ADD",
            "amount": request.amount,
            "wallet_balance": wallet.balance
        }

    if action == "WITHDRAW":

        bank_account = db.query(BankAccount).filter(
            BankAccount.user_id == user["user_id"]
        ).first()

        if not bank_account:
            raise HTTPException(
                status_code=404,
                detail="Please link your bank account first"
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

        notification = Notification(
            user_id=user["user_id"],
            message=f"₹{request.amount} withdrawn to bank account"
        )

        db.add(transaction)
        db.add(notification)

        db.commit()

        return {
            "message": "Withdrawal successful",
            "action": "WITHDRAW",
            "amount": request.amount,
            "wallet_balance": wallet.balance,
            "bank_balance": bank_account.balance
        }


@router.post("/wallet/add-money")
def add_money(
    request: AddMoneyRequest,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    return update_wallet_balance(
        WalletUpdateRequest(
            amount=request.amount,
            action="ADD"
        ),
        db,
        user
    )


@router.post("/wallet/withdraw")
def withdraw_money(
    request: WithdrawRequest,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    return update_wallet_balance(
        WalletUpdateRequest(
            amount=request.amount,
            action="WITHDRAW"
        ),
        db,
        user
    )