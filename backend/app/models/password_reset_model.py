from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from datetime import timedelta

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class PasswordReset(Base):

    __tablename__ = "password_resets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    reset_token = Column(
        String,
        unique=True,
        index=True
    )

    expires_at = Column(
        DateTime(timezone=True),
        default=lambda: get_ist_time() + timedelta(minutes=15)
    )

    status = Column(
        String,
        default="ACTIVE"
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