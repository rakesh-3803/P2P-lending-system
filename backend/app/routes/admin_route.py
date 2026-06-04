from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.user_model import User
from app.models.loan_model import Loan
from app.models.notification_model import Notification

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


# =====================================
# VIEW ALL USERS
# =====================================

@router.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    users = db.query(User).all()

    return users


# =====================================
# VIEW ALL LOANS
# =====================================

@router.get("/admin/loans")
def get_all_loans(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["ADMIN"])

    loans = db.query(Loan).all()

    return loans


# =====================================
# APPROVE LOAN
# =====================================

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

    # Update loan status
    loan.status = "APPROVED"

    # Create notification
    notification = Notification(
        user_id=loan.borrower_id,
        message="Your loan has been approved"
    )

    db.add(notification)

    db.commit()

    return {
        "message": "Loan approved"
    }


# =====================================
# REJECT LOAN
# =====================================

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

    # Update loan status
    loan.status = "REJECTED"

    # Create notification
    notification = Notification(
        user_id=loan.borrower_id,
        message="Your loan has been rejected"
    )

    db.add(notification)

    db.commit()

    return {
        "message": "Loan rejected"
    }


# =====================================
# BLOCK USER
# =====================================

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