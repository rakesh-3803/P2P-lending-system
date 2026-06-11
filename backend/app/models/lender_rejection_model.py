from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime
from datetime import datetime

from app.database.database import Base


class LenderRejection(Base):

    __tablename__ = "lender_rejections"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    lender_id = Column(Integer, ForeignKey("users.id"))

    reason = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )