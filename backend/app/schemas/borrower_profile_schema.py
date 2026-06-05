from pydantic import BaseModel


class BorrowerProfileCreate(BaseModel):

    aadhaar_number: str

    pan_number: str

    annual_income: float

    occupation: str

    company_name: str