from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.transaction_model import Transaction

from app.auth.auth_bearer import verify_token

router = APIRouter()


@router.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    transactions = db.query(Transaction).filter(
        Transaction.user_id == user["user_id"]
    ).all()

    return transactions