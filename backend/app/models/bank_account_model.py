from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class BankAccount(Base):

    __tablename__ = "bank_accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    account_holder = Column(
        String,
        nullable=False
    )

    account_number = Column(
        String,
        nullable=False
    )

    ifsc_code = Column(
        String,
        nullable=False
    )

    bank_name = Column(
        String,
        nullable=False
    )

    balance = Column(
        Float,
        default=0
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