from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta

from app.database.db_dependency import get_db

from app.models.user_model import User
from app.models.loan_model import Loan
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.investment_model import Investment
from app.models.notification_model import Notification
from app.models.borrower_profile_model import BorrowerProfile
from app.models.emi_model import EMI

from app.utils.time_utils import get_ist_time

from app.schemas.loan_schema import LoanCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role


router = APIRouter()


# =========================================
# ADMIN WALLET HELPER
# =========================================

def get_admin_wallet(db: Session):

    admin_user = db.query(User).filter(
        User.role.ilike("admin")
    ).first()

    if not admin_user:
        raise HTTPException(
            status_code=404,
            detail="Admin user not found"
        )

    admin_wallet = db.query(Wallet).filter(
        Wallet.user_id == admin_user.id
    ).first()

    if not admin_wallet:
        raise HTTPException(
            status_code=404,
            detail="Admin wallet not found"
        )

    return admin_user, admin_wallet


# =========================================
# PAYMENT SPLIT HELPER
# Borrower pays interest + 2%
# Lender receives interest - 2%
# Admin receives 4%
# =========================================

def split_payment_amount(loan: Loan, paid_amount: float):

    borrower_rate = loan.interest_rate + 2
    admin_rate = 4

    total_borrower_payable = (
        loan.amount +
        (loan.amount * borrower_rate / 100)
    )

    total_admin_fee = (
        loan.amount * admin_rate / 100
    )

    admin_share = round(
        paid_amount * total_admin_fee / total_borrower_payable,
        2
    )

    lender_share = round(
        paid_amount - admin_share,
        2
    )

    return lender_share, admin_share


# =========================================
# APPLY LOAN
# =========================================

@router.post("/apply-loan")
def apply_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Complete borrower profile before applying for loan"
        )

    if not profile.profile_completed:
        raise HTTPException(
            status_code=400,
            detail="Borrower profile not completed"
        )

    new_loan = Loan(
        borrower_id=user["user_id"],
        amount=loan.amount,
        interest_rate=loan.interest_rate,
        tenure_months=loan.tenure_months,
        purpose=loan.purpose,
        status="PENDING"
    )

    db.add(new_loan)

    notification = Notification(
        user_id=user["user_id"],
        message="Loan application submitted successfully"
    )

    db.add(notification)

    db.commit()
    db.refresh(new_loan)

    return {
        "message": "Loan applied successfully",
        "loan_id": new_loan.id
    }


# =========================================
# MY LOANS
# =========================================

@router.get("/my-loans")
def my_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    loans = db.query(Loan).filter(
        Loan.borrower_id == user["user_id"]
    ).all()

    return loans


# =========================================
# APPROVED LOANS
# =========================================

@router.get("/approved-loans")
def approved_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    loans = db.query(Loan).filter(
        Loan.status == "APPROVED"
    ).all()

    return loans


# =========================================
# MY EMIS
# =========================================

@router.get("/my-emis")
def my_emis(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    emis = db.query(EMI).filter(
        EMI.borrower_id == user["user_id"]
    ).all()

    return emis


# =========================================
# PAY EMI
# =========================================

@router.put("/pay-emi/{emi_id}")
def pay_emi(
    emi_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    emi = db.query(EMI).filter(
        EMI.id == emi_id,
        EMI.borrower_id == user["user_id"]
    ).first()

    if not emi:
        raise HTTPException(
            status_code=404,
            detail="EMI not found"
        )

    if emi.status == "PAID":
        raise HTTPException(
            status_code=400,
            detail="EMI already paid"
        )

    loan = db.query(Loan).filter(
        Loan.id == emi.loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "FUNDED":
        raise HTTPException(
            status_code=400,
            detail="Loan is not active"
        )

    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not borrower_wallet:
        raise HTTPException(
            status_code=404,
            detail="Borrower wallet not found"
        )

    if borrower_wallet.balance < emi.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    investment = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).first()

    if not investment:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    lender_wallet = db.query(Wallet).filter(
        Wallet.user_id == investment.lender_id
    ).first()

    if not lender_wallet:
        raise HTTPException(
            status_code=404,
            detail="Lender wallet not found"
        )

    admin_user, admin_wallet = get_admin_wallet(db)

    lender_share, admin_share = split_payment_amount(
        loan,
        emi.amount
    )

    payment_time = get_ist_time()

    borrower_wallet.balance -= emi.amount
    lender_wallet.balance += lender_share
    admin_wallet.balance += admin_share

    emi.status = "PAID"
    emi.paid_at = payment_time

    borrower_transaction = Transaction(
        user_id=user["user_id"],
        amount=emi.amount,
        transaction_type="DEBIT",
        description=f"EMI {emi.emi_number} payment"
    )

    lender_transaction = Transaction(
        user_id=investment.lender_id,
        amount=lender_share,
        transaction_type="CREDIT",
        description=f"EMI {emi.emi_number} received after platform fee"
    )

    admin_transaction = Transaction(
        user_id=admin_user.id,
        amount=admin_share,
        transaction_type="CREDIT",
        description=f"Platform fee from EMI {emi.emi_number}"
    )

    db.add(borrower_transaction)
    db.add(lender_transaction)
    db.add(admin_transaction)

    borrower_profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    updated_credit_score = None
    reward_message = ""

    if borrower_profile:

        borrower_profile.credit_score += 5

        if emi.due_date and payment_time <= emi.due_date:

            borrower_profile.credit_score += 2

            reward_message = (
                " Great job! You paid this EMI on time, "
                "so your credit score increased by an extra 2 points."
            )

        if borrower_profile.credit_score > 900:
            borrower_profile.credit_score = 900

        updated_credit_score = borrower_profile.credit_score

        db.add(borrower_profile)

    borrower_notification = Notification(
        user_id=user["user_id"],
        message=(
            f"EMI {emi.emi_number} paid successfully."
            f"{reward_message}"
            f" Current Credit Score: {updated_credit_score}."
        )
    )

    lender_notification = Notification(
        user_id=investment.lender_id,
        message=(
            f"EMI {emi.emi_number} received. "
            f"₹{lender_share} credited after platform fee."
        )
    )

    admin_notification = Notification(
        user_id=admin_user.id,
        message=f"₹{admin_share} platform fee received from EMI {emi.emi_number}"
    )

    db.add(borrower_notification)
    db.add(lender_notification)
    db.add(admin_notification)

    pending_emis = db.query(EMI).filter(
        EMI.loan_id == loan.id,
        EMI.status.in_(["PENDING", "OVERDUE"])
    ).count()

    if pending_emis == 0:
        loan.status = "COMPLETED"

        completion_notification = Notification(
            user_id=user["user_id"],
            message="All EMIs paid. Loan completed successfully."
        )

        db.add(completion_notification)

    db.commit()

    return {
        "message": "EMI paid successfully",
        "emi_id": emi.id,
        "emi_number": emi.emi_number,
        "amount_paid": emi.amount,
        "lender_received": lender_share,
        "admin_platform_fee": admin_share,
        "paid_at": emi.paid_at,
        "loan_status": loan.status,
        "updated_credit_score": updated_credit_score
    }


# =========================================
# FULL LOAN SETTLEMENT
# =========================================

@router.put("/repay-loan/{loan_id}")
def repay_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.borrower_id != user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    if loan.status != "FUNDED":
        raise HTTPException(
            status_code=400,
            detail="Loan is not active"
        )

    borrower_wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    if not borrower_wallet:
        raise HTTPException(
            status_code=404,
            detail="Borrower wallet not found"
        )

    investment = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).first()

    if not investment:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    lender_wallet = db.query(Wallet).filter(
        Wallet.user_id == investment.lender_id
    ).first()

    if not lender_wallet:
        raise HTTPException(
            status_code=404,
            detail="Lender wallet not found"
        )

    pending_emis = db.query(EMI).filter(
        EMI.loan_id == loan.id,
        EMI.status.in_(["PENDING", "OVERDUE"])
    ).all()

    remaining_amount = sum(
        emi.amount for emi in pending_emis
    )

    if remaining_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Loan already fully repaid"
        )

    if borrower_wallet.balance < remaining_amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance"
        )

    admin_user, admin_wallet = get_admin_wallet(db)

    lender_share, admin_share = split_payment_amount(
        loan,
        remaining_amount
    )

    borrower_wallet.balance -= remaining_amount
    lender_wallet.balance += lender_share
    admin_wallet.balance += admin_share

    settlement_time = get_ist_time()

    for emi in pending_emis:
        emi.status = "PAID"
        emi.paid_at = settlement_time

    loan.status = "COMPLETED"

    borrower_profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    updated_credit_score = None

    if borrower_profile:
        borrower_profile.credit_score += 20

        if borrower_profile.credit_score > 900:
            borrower_profile.credit_score = 900

        updated_credit_score = borrower_profile.credit_score

        db.add(borrower_profile)

    borrower_transaction = Transaction(
        user_id=user["user_id"],
        amount=remaining_amount,
        transaction_type="DEBIT",
        description="Full loan settlement"
    )

    lender_transaction = Transaction(
        user_id=investment.lender_id,
        amount=lender_share,
        transaction_type="CREDIT",
        description="Early loan settlement received after platform fee"
    )

    admin_transaction = Transaction(
        user_id=admin_user.id,
        amount=admin_share,
        transaction_type="CREDIT",
        description="Platform fee from full loan settlement"
    )

    db.add(borrower_transaction)
    db.add(lender_transaction)
    db.add(admin_transaction)

    borrower_notification = Notification(
        user_id=user["user_id"],
        message="Loan settled successfully. All pending EMIs have been closed."
    )

    lender_notification = Notification(
        user_id=investment.lender_id,
        message=f"₹{lender_share} received as full loan settlement after platform fee."
    )

    admin_notification = Notification(
        user_id=admin_user.id,
        message=f"₹{admin_share} platform fee received from full loan settlement"
    )

    db.add(borrower_notification)
    db.add(lender_notification)
    db.add(admin_notification)

    db.commit()

    return {
        "message": "Loan settled successfully",
        "remaining_amount_paid": remaining_amount,
        "lender_received": lender_share,
        "admin_platform_fee": admin_share,
        "loan_status": loan.status,
        "updated_credit_score": updated_credit_score
    }


# =========================================
# EMI DUE REMINDER
# =========================================

@router.post("/emi/send-due-reminders")
def send_due_emi_reminders(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    today = get_ist_time().date()

    due_emis = db.query(EMI).filter(
        func.date(EMI.due_date) == today,
        EMI.status == "PENDING"
    ).all()

    for emi in due_emis:

        notification = Notification(
            user_id=emi.borrower_id,
            message=(
                f"Reminder: EMI {emi.emi_number} of ₹{emi.amount} "
                f"is due today. Please pay before the end of the day."
            )
        )

        db.add(notification)

    db.commit()

    return {
        "message": "Due EMI reminders sent successfully",
        "reminders_sent": len(due_emis)
    }


# =========================================
# CHECK OVERDUE EMI
# =========================================

@router.post("/emi/check-overdue")
def check_overdue_emis(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    today = get_ist_time()

    overdue_emis = db.query(EMI).filter(
        EMI.due_date < today,
        EMI.status == "PENDING"
    ).all()

    for emi in overdue_emis:

        emi.status = "OVERDUE"

        borrower_profile = db.query(BorrowerProfile).filter(
            BorrowerProfile.user_id == emi.borrower_id
        ).first()

        updated_credit_score = None

        if borrower_profile:

            borrower_profile.credit_score -= 10

            if borrower_profile.credit_score < 300:
                borrower_profile.credit_score = 300

            updated_credit_score = borrower_profile.credit_score

            db.add(borrower_profile)

        notification = Notification(
            user_id=emi.borrower_id,
            message=(
                f"EMI {emi.emi_number} of ₹{emi.amount} is overdue. "
                f"Your credit score has been reduced by 10 points. "
                f"Current Credit Score: {updated_credit_score}. "
                "Please pay immediately."
            )
        )

        db.add(notification)

    db.commit()

    return {
        "message": "Overdue EMI check completed",
        "overdue_count": len(overdue_emis)
    }


# =========================================
# UPCOMING EMI REMINDER
# =========================================

@router.post("/emi/send-upcoming-reminders")
def send_upcoming_emi_reminders(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    today = get_ist_time().date()

    reminder_date = today + timedelta(days=3)

    upcoming_emis = db.query(EMI).filter(
        func.date(EMI.due_date) == reminder_date,
        EMI.status == "PENDING"
    ).all()

    for emi in upcoming_emis:

        notification = Notification(
            user_id=emi.borrower_id,
            message=(
                f"Upcoming EMI Reminder: EMI {emi.emi_number} "
                f"of ₹{emi.amount} is due in 3 days. "
                "Please keep enough wallet balance."
            )
        )

        db.add(notification)

    db.commit()

    return {
        "message": "Upcoming EMI reminders sent successfully",
        "reminders_sent": len(upcoming_emis)
    }


# =========================================
# CHECK EXPIRED LOANS
# =========================================

@router.post("/loan/check-expired")
def check_expired_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    today = get_ist_time()

    expiry_limit = today - timedelta(days=7)

    expired_loans = db.query(Loan).filter(
        Loan.status == "APPROVED",
        Loan.updated_at < expiry_limit
    ).all()

    for loan in expired_loans:

        loan.status = "EXPIRED"

        notification = Notification(
            user_id=loan.borrower_id,
            message=(
                "Your approved loan request has expired because "
                "no lender funded it within 7 days."
            )
        )

        db.add(notification)

    db.commit()

    return {
        "message": "Expired loan check completed",
        "expired_count": len(expired_loans)
    }


# =========================================
# BORROWER DASHBOARD SUMMARY
# =========================================

@router.get("/borrower/dashboard-summary")
def borrower_dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    loans = db.query(Loan).filter(
        Loan.borrower_id == user["user_id"]
    ).all()

    emis = db.query(EMI).filter(
        EMI.borrower_id == user["user_id"]
    ).all()

    pending_emis = [
        emi for emi in emis
        if emi.status in ["PENDING", "OVERDUE"]
    ]

    paid_emis = [
        emi for emi in emis
        if emi.status == "PAID"
    ]

    total_pending_amount = sum(
        emi.amount for emi in pending_emis
    )

    next_emi = None

    if pending_emis:
        next_emi = sorted(
            pending_emis,
            key=lambda emi: emi.due_date
        )[0]

    return {
        "wallet_balance": wallet.balance if wallet else 0,
        "credit_score": profile.credit_score if profile else None,
        "total_loans": len(loans),
        "active_loans": len([
            loan for loan in loans
            if loan.status == "FUNDED"
        ]),
        "pending_emis": len(pending_emis),
        "paid_emis": len(paid_emis),
        "total_pending_emi_amount": total_pending_amount,
        "next_emi": {
            "emi_id": next_emi.id,
            "emi_number": next_emi.emi_number,
            "amount": next_emi.amount,
            "due_date": next_emi.due_date,
            "status": next_emi.status
        } if next_emi else None
    }


# =========================================
# LENDER DASHBOARD SUMMARY
# =========================================

@router.get("/lender/dashboard-summary")
def lender_dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    wallet = db.query(Wallet).filter(
        Wallet.user_id == user["user_id"]
    ).first()

    investments = db.query(Investment).filter(
        Investment.lender_id == user["user_id"]
    ).all()

    total_invested = sum(
        investment.amount for investment in investments
    )

    expected_returns = 0

    active_investments = 0

    for investment in investments:

        loan = db.query(Loan).filter(
            Loan.id == investment.loan_id
        ).first()

        if loan:

            expected_returns += (
                investment.amount +
                (
                    investment.amount *
                    max(loan.interest_rate - 2, 0) / 100
                )
            )

            if loan.status == "FUNDED":
                active_investments += 1

    available_loans = db.query(Loan).filter(
        Loan.status == "APPROVED"
    ).count()

    return {
        "wallet_balance": wallet.balance if wallet else 0,
        "total_invested": total_invested,
        "expected_returns": expected_returns,
        "active_investments": active_investments,
        "available_loans": available_loans
    }


# =========================================
# BORROWER TRANSACTION SUMMARY
# =========================================

@router.get("/borrower/transaction-summary")
def borrower_transaction_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    transactions = db.query(Transaction).filter(
        Transaction.user_id == user["user_id"]
    ).all()

    total_credit = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "CREDIT"
    )

    total_debit = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "DEBIT"
    )

    emi_payments = [
        transaction for transaction in transactions
        if "EMI" in transaction.description
    ]

    withdrawals = [
        transaction for transaction in transactions
        if "withdraw" in transaction.description.lower()
    ]

    wallet_topups = [
        transaction for transaction in transactions
        if "top-up" in transaction.description.lower()
        or "wallet" in transaction.description.lower()
    ]

    recent_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.created_at,
        reverse=True
    )[:5]

    return {
        "total_credit": total_credit,
        "total_debit": total_debit,
        "emi_payments_count": len(emi_payments),
        "withdrawals_count": len(withdrawals),
        "wallet_topups_count": len(wallet_topups),
        "recent_transactions": recent_transactions
    }