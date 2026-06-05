from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey
)

from app.database.database import Base


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

    aadhaar_number = Column(String)

    pan_number = Column(String)

    annual_income = Column(Float)

    occupation = Column(String)

    company_name = Column(String)

    credit_score = Column(
        Integer,
        default=700
    )

    profile_completed = Column(
        Boolean,
        default=True
    )