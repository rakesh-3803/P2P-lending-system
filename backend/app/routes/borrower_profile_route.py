from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.borrower_profile_model import BorrowerProfile

from app.schemas.borrower_profile_schema import BorrowerProfileCreate

from app.auth.auth_bearer import verify_token
from app.auth.role_checker import check_role

router = APIRouter()


# =========================================
# CREATE BORROWER PROFILE
# =========================================

@router.post("/borrower-profile")
def create_profile(
    profile: BorrowerProfileCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    existing_profile = db.query(
        BorrowerProfile
    ).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    if existing_profile:

        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    new_profile = BorrowerProfile(

        user_id=user["user_id"],

        aadhaar_number=profile.aadhaar_number,

        pan_number=profile.pan_number,

        annual_income=profile.annual_income,

        occupation=profile.occupation,

        company_name=profile.company_name,

        credit_score=700,

        profile_completed=True
    )

    db.add(new_profile)

    db.commit()

    db.refresh(new_profile)

    return {
        "message": "Profile created successfully",
        "credit_score": 700
    }


# =========================================
# GET PROFILE
# =========================================

@router.get("/borrower-profile")
def get_profile(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):

    check_role(user, ["BORROWER"])

    profile = db.query(
        BorrowerProfile
    ).filter(
        BorrowerProfile.user_id == user["user_id"]
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile