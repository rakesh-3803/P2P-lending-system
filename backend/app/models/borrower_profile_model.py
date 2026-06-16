from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime
)

from app.database.database import Base
from app.utils.time_utils import get_ist_time


class BorrowerProfile(Base):

    __tablename__ = "borrower_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    aadhaar_number = Column(
        String
    )

    pan_number = Column(
        String
    )

    annual_income = Column(
        Float
    )

    occupation = Column(
        String
    )

    company_name = Column(
        String
    )

    credit_score = Column(
        Integer,
        default=700
    )

    profile_completed = Column(
        Boolean,
        default=True
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