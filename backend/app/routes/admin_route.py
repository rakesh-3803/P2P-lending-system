from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.user_model import User
from app.models.loan_model import Loan
from app.models.notification_model import Notification
from app.models.borrower_profile_model import BorrowerProfile

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