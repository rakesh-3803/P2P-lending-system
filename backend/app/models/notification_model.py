from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from datetime import datetime
from app.database.database import Base


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(Integer)

    message = Column(String)

    status = Column(
        String,
        default="UNREAD"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )