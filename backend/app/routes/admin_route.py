from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.database.db_dependency import get_db

from app.models.user_model import User
from app.models.loan_model import Loan
from app.models.notification_model import Notification
from app.models.borrower_profile_model import BorrowerProfile
from app.models.investment_model import Investment
from app.models.wallet_model import Wallet
from app.models.transaction_model import Transaction
from app.models.bank_account_model import BankAccount
from app.models.borrower_profile_model import BorrowerProfile
from app.models.emi_model import EMI

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


@router.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    users = db.query(User).all()

    return users


@router.get("/admin/loans")
def get_all_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loans = db.query(Loan).all()

    result = []

    for loan in loans:

        borrower = db.query(User).filter(
            User.id == loan.borrower_id
        ).first()

        profile = db.query(BorrowerProfile).filter(
            BorrowerProfile.user_id == loan.borrower_id
        ).first()

        result.append({
            "loan_id": loan.id,
            "borrower_id": loan.borrower_id,
            "borrower_name": borrower.full_name if borrower else None,
            "borrower_email": borrower.email if borrower else None,

            "aadhaar_number": profile.aadhaar_number if profile else None,
            "pan_number": profile.pan_number if profile else None,
            "annual_income": profile.annual_income if profile else None,
            "occupation": profile.occupation if profile else None,
            "company_name": profile.company_name if profile else None,
            "credit_score": profile.credit_score if profile else None,

            "loan_amount": loan.amount,
            "interest_rate": loan.interest_rate,
            "tenure_months": loan.tenure_months,
            "purpose": loan.purpose,
            "status": loan.status
        })

    return result


@router.get("/admin/pending-loans")
def get_pending_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loans = db.query(Loan).filter(
        Loan.status == "PENDING"
    ).all()

    result = []

    for loan in loans:

        borrower = db.query(User).filter(
            User.id == loan.borrower_id
        ).first()

        profile = db.query(BorrowerProfile).filter(
            BorrowerProfile.user_id == loan.borrower_id
        ).first()

        result.append({
            "loan_id": loan.id,
            "borrower_id": loan.borrower_id,
            "borrower_name": borrower.full_name if borrower else None,
            "borrower_email": borrower.email if borrower else None,

            "aadhaar_number": profile.aadhaar_number if profile else None,
            "pan_number": profile.pan_number if profile else None,
            "annual_income": profile.annual_income if profile else None,
            "occupation": profile.occupation if profile else None,
            "company_name": profile.company_name if profile else None,
            "credit_score": profile.credit_score if profile else None,

            "loan_amount": loan.amount,
            "interest_rate": loan.interest_rate,
            "tenure_months": loan.tenure_months,
            "purpose": loan.purpose,
            "status": loan.status
        })

    return result


@router.put("/admin/loan/{loan_id}/approve")
def approve_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:

        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    loan.status = "APPROVED"
    

    notification = Notification(
        user_id=loan.borrower_id,
        message="Your loan has been approved"
    )

    db.add(notification)
    db.commit()

    return {
        "message": "Loan approved"
    }


@router.put("/admin/loan/{loan_id}/reject")
def reject_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:

        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    loan.status = "REJECTED"

    notification = Notification(
        user_id=loan.borrower_id,
        message="Your loan has been rejected"
    )

    db.add(notification)
    db.commit()

    return {
        "message": "Loan rejected"
    }


@router.put("/admin/block-user/{user_id}")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    target_user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not target_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    target_user.is_blocked = True

    db.commit()

    return {
        "message": "User blocked successfully"
    }

@router.get("/admin/analytics")
def admin_analytics(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    total_users = db.query(User).count()

    total_borrowers = db.query(User).filter(
        User.role.ilike("borrower")
    ).count()

    total_lenders = db.query(User).filter(
        User.role.ilike("lender")
    ).count()

    total_loans = db.query(Loan).count()

    pending_loans = db.query(Loan).filter(
        Loan.status == "PENDING"
    ).count()

    approved_loans = db.query(Loan).filter(
        Loan.status == "APPROVED"
    ).count()

    funded_loans = db.query(Loan).filter(
        Loan.status == "FUNDED"
    ).count()

    completed_loans = db.query(Loan).filter(
        Loan.status == "COMPLETED"
    ).count()

    rejected_loans = db.query(Loan).filter(
        Loan.status.in_([
            "REJECTED",
            "REJECTED_BY_LENDERS"
        ])
    ).count()

    total_loan_amount = sum(
        loan.amount for loan in db.query(Loan).all()
    )

    total_invested_amount = sum(
        investment.amount
        for investment in db.query(Investment).all()
    )

    total_wallet_balance = sum(
        wallet.balance
        for wallet in db.query(Wallet).all()
    )

    total_bank_balance = sum(
        bank.balance
        for bank in db.query(BankAccount).all()
    )

    total_transactions = db.query(Transaction).count()

    completed_profiles = db.query(BorrowerProfile).filter(
        BorrowerProfile.profile_completed == True
    ).count()

    return {
        "users": {
            "total_users": total_users,
            "borrowers": total_borrowers,
            "lenders": total_lenders
        },
        "loans": {
            "total_loans": total_loans,
            "pending_loans": pending_loans,
            "approved_loans": approved_loans,
            "funded_loans": funded_loans,
            "completed_loans": completed_loans,
            "rejected_loans": rejected_loans,
            "total_loan_amount": total_loan_amount
        },
        "investments": {
            "total_invested_amount": total_invested_amount
        },
        "wallets": {
            "total_wallet_balance": total_wallet_balance,
            "total_bank_balance": total_bank_balance
        },
        "transactions": {
            "total_transactions": total_transactions
        },
        "borrower_profiles": {
            "completed_profiles": completed_profiles
        }
    }

@router.get("/admin/loan/{loan_id}/details")
def get_loan_details(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    borrower = db.query(User).filter(
        User.id == loan.borrower_id
    ).first()

    profile = db.query(BorrowerProfile).filter(
        BorrowerProfile.user_id == loan.borrower_id
    ).first()

    investment = db.query(Investment).filter(
        Investment.loan_id == loan.id
    ).first()

    emis = db.query(EMI).filter(
        EMI.loan_id == loan.id
    ).all()

    transactions = db.query(Transaction).filter(
        Transaction.description.ilike(f"%loan%")
    ).all()

    return {
        "loan": loan,
        "borrower": {
            "id": borrower.id if borrower else None,
            "name": borrower.full_name if borrower else None,
            "email": borrower.email if borrower else None
        },
        "borrower_profile": profile,
        "investment": investment,
        "emis": emis,
        "transactions": transactions
    }
@router.get("/admin/dashboard-summary")
def admin_dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    total_users = db.query(User).count()

    total_borrowers = db.query(User).filter(
        User.role.ilike("borrower")
    ).count()

    total_lenders = db.query(User).filter(
        User.role.ilike("lender")
    ).count()

    total_loans = db.query(Loan).count()

    pending_loans = db.query(Loan).filter(
        Loan.status == "PENDING"
    ).count()

    approved_loans = db.query(Loan).filter(
        Loan.status == "APPROVED"
    ).count()

    funded_loans = db.query(Loan).filter(
        Loan.status == "FUNDED"
    ).count()

    completed_loans = db.query(Loan).filter(
        Loan.status == "COMPLETED"
    ).count()

    rejected_loans = db.query(Loan).filter(
        Loan.status.in_([
            "REJECTED",
            "REJECTED_BY_LENDERS",
            "EXPIRED"
        ])
    ).count()

    investments = db.query(Investment).all()

    total_invested_amount = sum(
        investment.amount for investment in investments
    )

    return {
        "users": {
            "total_users": total_users,
            "borrowers": total_borrowers,
            "lenders": total_lenders
        },
        "loans": {
            "total_loans": total_loans,
            "pending_loans": pending_loans,
            "approved_loans": approved_loans,
            "funded_loans": funded_loans,
            "completed_loans": completed_loans,
            "rejected_loans": rejected_loans
        },
        "investments": {
            "total_invested_amount": total_invested_amount
        }
    }

@router.get("/admin/export-loans")
def export_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loans = db.query(Loan).all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Loan ID",
        "Borrower ID",
        "Amount",
        "Interest Rate",
        "Tenure",
        "Purpose",
        "Status",
        "Created At"
    ])

    for loan in loans:

        writer.writerow([
            loan.id,
            loan.borrower_id,
            loan.amount,
            loan.interest_rate,
            loan.tenure_months,
            loan.purpose,
            loan.status,
            loan.created_at
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=loan_report.csv"
        }
    )