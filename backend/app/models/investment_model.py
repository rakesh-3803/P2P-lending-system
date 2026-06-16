from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class Investment(Base):

    __tablename__ = "investments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    lender_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    loan_id = Column(
        Integer,
        ForeignKey("loans.id")
    )

    amount = Column(
        Float,
        nullable=False
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