from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.core.current_user import get_current_user
from app.core.dependencies import DBSession

from app.models.user import User
from app.models.website import Website

from app.schemas.scan import (
    ScanDetailResponse,
    ScanHistoryResponse,
)

from app.services.scan.detail import ScanDetailService
from app.services.scan.history import ScanHistoryService
from app.services.scanner.full_scan import FullScanService


router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)


# ============================================================
# RUN NEW SCAN
# ============================================================

@router.post("/scan/{website_id}")
def scan(
    website_id: int,
    background_tasks: BackgroundTasks,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):

    # --------------------------------------------------------
    # Find website belonging to current user
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create the Scan record first
    # --------------------------------------------------------

    scan = FullScanService.create_scan(
        website=website,
        db=db,
    )

    # --------------------------------------------------------
    # Get database engine before request session closes
    # --------------------------------------------------------

    engine = db.get_bind()

    # --------------------------------------------------------
    # Start scan in background
    # --------------------------------------------------------

    background_tasks.add_task(
        FullScanService.execute,
        website=website,
        scan_id=scan.id,
        engine=engine,
    )

    # --------------------------------------------------------
    # Return immediately
    # --------------------------------------------------------

    return {
        "scan_id": scan.id,
        "website": website.url,
        "status": "Running",
        "message": "Scan started successfully.",
    }


# ============================================================
# STOP SCAN
# ============================================================

@router.post("/stop/{scan_id}")
def stop_scan(
    scan_id: int,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):

    # --------------------------------------------------------
    # Verify scan belongs to current user
    # --------------------------------------------------------

    scan = FullScanService.get_user_scan(
        db=db,
        scan_id=scan_id,
        user_id=current_user.id,
    )

    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found.",
        )

    # --------------------------------------------------------
    # Check current status
    # --------------------------------------------------------

    if scan.status != "Running":
        raise HTTPException(
            status_code=400,
            detail=f"Scan cannot be stopped because its status is '{scan.status}'.",
        )

    # --------------------------------------------------------
    # Request scan cancellation
    # --------------------------------------------------------

    stopped = FullScanService.stop_scan(
        scan_id=scan_id,
    )

    if not stopped:
        raise HTTPException(
            status_code=404,
            detail="Running scan not found.",
        )

    return {
        "scan_id": scan_id,
        "status": "Stopping",
        "message": "Stop request sent successfully.",
    }


# ============================================================
# SCAN HISTORY
# ============================================================

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


# ============================================================
# GET ONE SCAN BY ID
# ============================================================

@router.get(
    "/{scan_id}",
    response_model=ScanDetailResponse,
)
def get_scan(
    scan_id: int,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):

    scan = ScanDetailService.execute(
        db=db,
        user=current_user,
        scan_id=scan_id,
    )

    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found.",
        )

    return scan