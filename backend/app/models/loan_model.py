from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class Loan(Base):

    __tablename__ = "loans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    borrower_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    amount = Column(
        Float,
        nullable=False
    )

    interest_rate = Column(
        Float,
        nullable=False
    )

    tenure_months = Column(
        Integer,
        nullable=False
    )

    purpose = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="PENDING"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=get_ist_time
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=get_ist_time,
        onupdate=get_ist_time
    )