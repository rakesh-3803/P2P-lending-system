from pydantic import BaseModel


class LoanCreate(BaseModel):

    amount: float

    interest_rate: float

    tenure_months: int

    purpose: str