from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import DBSession
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth.register import RegisterService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


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
        return RegisterService.execute(user, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )