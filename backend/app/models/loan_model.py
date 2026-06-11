from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy import DateTime
from datetime import datetime

from app.database.database import Base


class Loan(Base):

    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)

    borrower_id = Column(Integer, ForeignKey("users.id"))

    amount = Column(Float, nullable=False)

    interest_rate = Column(Float, nullable=False)

    tenure_months  = Column(Integer, nullable=False)

    purpose = Column(String, nullable=False)

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