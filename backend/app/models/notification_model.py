from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer
    )

    message = Column(
        String
    )

    status = Column(
        String,
        default="UNREAD"
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