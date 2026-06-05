from sqlalchemy import Column, Integer, String, ForeignKey

from app.database.database import Base


class LenderRejection(Base):

    __tablename__ = "lender_rejections"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    lender_id = Column(Integer, ForeignKey("users.id"))

    reason = Column(String)