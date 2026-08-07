from fastapi import APIRouter, Depends, HTTPException

from app.core.current_user import get_current_user
from app.core.dependencies import DBSession
from app.models.user import User
from app.models.website import Website
from app.schemas.scan import ScanHistoryResponse
from app.services.scan.history import ScanHistoryService
from app.services.scanner.full_scan import FullScanService

router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)


@router.post("/scan/{website_id}")
def scan(
    website_id: int,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):

    website = (
        db.query(Website)
        .filter(
            Website.id == website_id,
            Website.user_id == current_user.id,
        )
        .first()
    )

    if not website:
        raise HTTPException(
            status_code=404,
            detail="Website not found.",
        )

    return FullScanService.execute(
        website=website,
        db=db,
    )


@router.get(
    "/history",
    response_model=list[ScanHistoryResponse],
)
def history(
    db: DBSession,
    current_user: User = Depends(get_current_user),
):

    return ScanHistoryService.execute(
        db=db,
        user=current_user,
    )