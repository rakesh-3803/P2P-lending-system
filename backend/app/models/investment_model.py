from sqlalchemy import Column, Integer, Float, ForeignKey

from app.database.database import Base


class Investment(Base):

    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)

    lender_id = Column(Integer, ForeignKey("users.id"))

    loan_id = Column(Integer, ForeignKey("loans.id"))

    amount = Column(Float, nullable=False)