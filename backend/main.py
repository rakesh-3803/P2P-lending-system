from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base

from app.models.user_model import User
from app.models.loan_model import Loan
from app.models.borrower_profile_model import BorrowerProfile
from app.models.investment_model import Investment
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.lender_rejection_model import LenderRejection
from app.models.emi_model import EMI
from app.models.password_reset_model import PasswordReset

from app.routes.auth_route import router as auth_router
from app.routes.loan_route import router as loan_router
from app.routes.investment_route import router as investment_router
from app.routes.admin_route import router as admin_router
from app.routes.wallet_route import router as wallet_router
from app.routes.transaction_route import router as transaction_router
from app.models.notification_model import Notification
from app.routes.notification_route import router as notification_router
from app.models.bank_account_model import BankAccount
from app.routes.bank_account_route import router as bank_account_router
from app.routes.borrower_profile_route import router as borrower_profile_router
from app.routes.lender_rejection_route import router as lender_rejection_router
from app.routes.ai_agent_route import router as ai_agent_router
from app.routes.password_reset_route import router as password_reset_router

# =========================================
# CREATE DATABASE TABLES
# =========================================

Base.metadata.create_all(bind=engine)

# =========================================
# FASTAPI APP
# =========================================

app = FastAPI()

# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROUTES
# =========================================

app.include_router(auth_router)
app.include_router(loan_router)
app.include_router(investment_router)
app.include_router(admin_router)
app.include_router(wallet_router)
app.include_router(transaction_router)
app.include_router(notification_router)
app.include_router(bank_account_router)
app.include_router(borrower_profile_router)
app.include_router(lender_rejection_router)
app.include_router(ai_agent_router)
app.include_router(password_reset_router)

# =========================================
# HOME ROUTE
# =========================================

@app.get("/")
def home():

    return {
        "message": "P2P Lending System API Running"
    }