from fastapi import APIRouter, Depends, HTTPException
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


@router.put("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user["user_id"]
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.status = "READ"

    db.commit()

    return {
        "message": "Notification marked as read"
    }


@router.put("/notifications/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    notifications = db.query(Notification).filter(
        Notification.user_id == user["user_id"],
        Notification.status == "UNREAD"
    ).all()

    for notification in notifications:
        notification.status = "READ"

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications)
    }
@router.get("/notifications/unread-count")
def unread_notification_count(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    unread_count = db.query(Notification).filter(
        Notification.user_id == user["user_id"],
        Notification.status == "UNREAD"
    ).count()

    return {
        "unread_count": unread_count
    }