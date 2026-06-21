from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.auth.security import hash_password
from app.schemas.user import UserLogin, Token
from app.auth.security import verify_password
from app.auth.security import create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
def get_me(
        current_user: User = Depends(get_current_user)
):
    return current_user


@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role="student"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post(
    "/login",
    response_model=Token
)
def login_user(
        user: UserLogin,
        db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        return {"error": "User not found"}

    if not verify_password(
            user.password,
            db_user.password_hash
    ):
        return {"error": "Wrong password"}

    token = create_access_token(
        {"sub": db_user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout():
    return {
        "message": "User logged out successfully"
    }
