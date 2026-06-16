from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.database.db_dependency import get_db

from app.models.user_model import User
from app.models.password_reset_model import PasswordReset
from app.utils.time_utils import get_ist_time


from app.schemas.password_reset_schema import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)




router = APIRouter()


@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with this email not found"
        )

    reset_token = str(uuid.uuid4())

    password_reset = PasswordReset(
        user_id=user.id,
        reset_token=reset_token
    )

    db.add(password_reset)
    db.commit()

    return {
        "message": "Password reset token generated successfully",
        "reset_token": reset_token,
        "note": "Use this token in /reset-password. Later this can be sent via email."
    }


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    reset_record = db.query(PasswordReset).filter(
        PasswordReset.reset_token == request.reset_token,
        PasswordReset.status == "ACTIVE"
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    if reset_record.expires_at < get_ist_time():

        reset_record.status = "EXPIRED"

        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Reset token expired"
    )

    user = db.query(User).filter(
        User.id == reset_record.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password = request.new_password
    reset_record.status = "USED"

    db.commit()

    return {
        "message": "Password reset successfully"
    }