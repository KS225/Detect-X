from fastapi import APIRouter, Depends, HTTPException, status

from app.core.current_user import get_current_user
from app.core.dependencies import DBSession

from app.models.user import User

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse

from app.services.auth.register import RegisterService
from app.services.auth.login import LoginService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# -------------------------
# Register
# -------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: RegisterRequest,
    db: DBSession,
):
    try:
        return RegisterService.execute(
            user,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# -------------------------
# Login
# -------------------------
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user: LoginRequest,
    db: DBSession,
):
    try:
        return LoginService.execute(
            user,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# -------------------------
# Current Logged-in User
# -------------------------
@router.get(
    "/me",
    response_model=UserResponse,
)
def current_user(
    user: User = Depends(get_current_user),
):
    return user