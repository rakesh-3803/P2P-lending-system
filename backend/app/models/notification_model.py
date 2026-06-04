from sqlalchemy import Column, Integer, String
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