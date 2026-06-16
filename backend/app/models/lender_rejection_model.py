from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class LenderRejection(Base):

    __tablename__ = "lender_rejections"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    loan_id = Column(
        Integer,
        ForeignKey("loans.id")
    )

    lender_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    reason = Column(
        String
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