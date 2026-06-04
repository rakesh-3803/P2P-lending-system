from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.notification_model import Notification

from app.auth.auth_bearer import verify_token

router = APIRouter()


@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    notifications = db.query(Notification).filter(
        Notification.user_id == user["user_id"]
    ).all()

    return notifications