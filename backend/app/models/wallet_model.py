from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class Wallet(Base):

    __tablename__ = "wallets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
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