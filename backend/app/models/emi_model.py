from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class EMI(Base):

    __tablename__ = "emis"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    borrower_id = Column(Integer, ForeignKey("users.id"))

    emi_number = Column(Integer)

    amount = Column(Float)

    due_date = Column(DateTime(timezone=True))

    paid_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String, default="PENDING")

    created_at = Column(DateTime(timezone=True), default=get_ist_time)

    updated_at = Column(
        DateTime(timezone=True),
        default=get_ist_time,
        onupdate=get_ist_time
    )