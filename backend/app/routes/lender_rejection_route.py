from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter

from app.database.db_dependency import get_db

from app.models.loan_model import Loan
from app.models.user_model import User
from app.models.notification_model import Notification
from app.models.lender_rejection_model import LenderRejection

from app.schemas.lender_rejection_schema import LenderRejectCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


@router.post("/loan/{loan_id}/reject-by-lender")
def reject_loan_by_lender(
    loan_id: int,
    request: LenderRejectCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["LENDER"])

    loan = db.query(Loan).filter(
        Loan.id == loan_id
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Loan is not available for rejection"
        )

    existing_rejection = db.query(
        LenderRejection
    ).filter(
        LenderRejection.loan_id == loan_id,
        LenderRejection.lender_id == user["user_id"]
    ).first()

    if existing_rejection:
        raise HTTPException(
            status_code=400,
            detail="You already rejected this loan"
        )

    rejection = LenderRejection(
        loan_id=loan_id,
        lender_id=user["user_id"],
        reason=request.reason
    )

    db.add(rejection)
    db.commit()

    total_lenders = db.query(User).filter(
        func.upper(User.role) == "LENDER"
    ).count()

    total_rejections = db.query(
        LenderRejection
    ).filter(
        LenderRejection.loan_id == loan_id
    ).count()

    # ALL LENDERS REJECTED
    if total_rejections >= total_lenders:

        all_rejections = db.query(
            LenderRejection
        ).filter(
            LenderRejection.loan_id == loan_id
        ).all()

        reasons = [
            item.reason.strip()
            for item in all_rejections
            if item.reason
        ]

        reason_counts = Counter(reasons)

        summary_lines = []

        for reason, count in reason_counts.most_common():

            lender_word = (
                "lender"
                if count == 1
                else "lenders"
            )

            summary_lines.append(
                f"{reason} ({count} {lender_word})"
            )

        formatted_reasons = "\n".join(
            [
                f"• {reason}"
                for reason in summary_lines
            ]
        )

        loan.status = "REJECTED_BY_LENDERS"

        notification_message = (
            "Loan Rejected by Lenders\n\n"
            "Reasons:\n\n"
            f"{formatted_reasons}\n\n"
            "Please review these concerns before applying again."
        )

        notification = Notification(
            user_id=loan.borrower_id,
            message=notification_message
        )

        db.add(loan)
        db.add(notification)

        db.commit()

        db.refresh(notification)

        print("NOTIFICATION CREATED")
        print("BORROWER ID:", loan.borrower_id)
        print("NOTIFICATION ID:", notification.id)

        return {
            "message": "Loan rejected successfully"
        }

    return {
        "message": "Loan rejected successfully"
    }