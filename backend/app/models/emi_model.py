from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy import DateTime
from datetime import datetime

from app.database.database import Base


class EMI(Base):

    __tablename__ = "emis"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    borrower_id = Column(Integer, ForeignKey("users.id"))

    emi_number = Column(Integer)

    amount = Column(Float)

    status = Column(String, default="PENDING")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )