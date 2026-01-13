from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import User, get_db
from schemas.auth import LoginRequest, LoginResponse
from services.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Find user by username
    user = db.query(User).filter(User.username == payload.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Verify password
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create and return token
    access_token = create_access_token(user.id, user.username)

    return LoginResponse(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
    )
