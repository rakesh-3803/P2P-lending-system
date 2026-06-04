from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.database.database import Base


class BankAccount(Base):

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    account_holder = Column(String, nullable=False)

    account_number = Column(String, nullable=False)

    ifsc_code = Column(String, nullable=False)

    bank_name = Column(String, nullable=False)

    balance = Column(Float, default=0)