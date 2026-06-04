from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.db_dependency import get_db

from app.models.user_model import User
from app.models.wallet_model import Wallet

from app.schemas.user_schema import UserCreate
from app.schemas.user_schema import UserLogin

from app.auth.jwt_handler import create_access_token

router = APIRouter()


# =====================================
# REGISTER
# =====================================

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # CHECK EMAIL EXISTS
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # CREATE USER
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=user.password,
        role=user.role
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    # CREATE WALLET
    wallet = Wallet(
        user_id=new_user.id,
        balance=0
    )

    db.add(wallet)

    db.commit()

    return {
        "message": "User registered successfully"
    }


# =====================================
# LOGIN
# =====================================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # FIND USER
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=404,
            detail="Invalid email"
        )

    # CHECK PASSWORD
    if existing_user.password != user.password:

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    # CREATE TOKEN
    token = create_access_token(
        {
            "user_id": existing_user.id,
            "role": existing_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": existing_user.role,
        "user_id": existing_user.id
    }