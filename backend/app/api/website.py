
print("✅ Website router loaded")
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.current_user import get_current_user
from app.core.dependencies import DBSession
from app.models.user import User
from app.models.website import Website
from app.schemas.website import (
    CreateWebsiteRequest,
    WebsiteResponse,
)
from app.services.website.create import (
    CreateWebsiteService,
)

router = APIRouter(
    prefix="/websites",
    tags=["Websites"],
)

@router.get(
    "",
    response_model=list[WebsiteResponse],
)
def get_websites(
    db: DBSession,
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Website)
        .filter(Website.user_id == current_user.id)
        .all()
    )

@router.post(
    "",
    response_model=WebsiteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_website(
    website: CreateWebsiteRequest,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):
    try:
        return CreateWebsiteService.execute(
            website,
            current_user,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )