from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.db_dependency import get_db
from app.models.bank_account_model import BankAccount
from app.auth.auth_bearer import verify_token

router = APIRouter()


class BankAccountCreate(BaseModel):
    account_holder: str
    account_number: str
    ifsc_code: str
    bank_name: str


@router.post("/bank-account")
def create_bank_account(
    request: BankAccountCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    existing_account = db.query(BankAccount).filter(
        BankAccount.user_id == user["user_id"]
    ).first()

    if existing_account:
        raise HTTPException(
            status_code=400,
            detail="Bank account already linked"
        )

    bank_account = BankAccount(
        user_id=user["user_id"],
        account_holder=request.account_holder,
        account_number=request.account_number,
        ifsc_code=request.ifsc_code,
        bank_name=request.bank_name,
        balance=0
    )

    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)

    return {
        "message": "Bank account linked successfully",
        "bank_account": bank_account
    }


@router.get("/bank-account")
def get_bank_account(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    bank_account = db.query(BankAccount).filter(
        BankAccount.user_id == user["user_id"]
    ).first()

    if not bank_account:
        raise HTTPException(
            status_code=404,
            detail="Bank account not linked"
        )

    return bank_account