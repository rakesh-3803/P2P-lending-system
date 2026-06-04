from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.db_dependency import get_db

from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction

from app.auth.auth_bearer import verify_token

router = APIRouter()


# =========================================
# REQUEST MODEL
# =========================================

class AddMoneyRequest(BaseModel):

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