from pydantic import BaseModel


class InvestmentCreate(BaseModel):

    loan_id: int
    amount: float