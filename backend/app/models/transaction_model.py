from sqlalchemy import Column, Integer, Float, String, ForeignKey

from app.database.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    amount = Column(Float)

    transaction_type = Column(String)

    description = Column(String)