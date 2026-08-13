from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.user import User


class ScanDetailService:

    @staticmethod
    def execute(
        db: Session,
        user: User,
        scan_id: int,
    ):

        # -----------------------------
        # Find scan belonging to user
        # -----------------------------

        scan = (
            db.query(Scan)
            .filter(
                Scan.id == scan_id,
                Scan.user_id == user.id,
            )
            .first()
        )

        if not scan:
            return None

        # -----------------------------
        # Return complete scan details
        # -----------------------------

        return {
            "id": scan.id,

            "website": scan.website.url,

            # -------------------------
            # Scan Progress
            # -------------------------

            "status": scan.status,

            "progress": scan.progress,

            "scan_stage": scan.scan_stage,

            # -------------------------
            # Security Summary
            # -------------------------

            "security_score": scan.security_score,

            "total_alerts": scan.total_alerts,

            "high": scan.high_count,

            "medium": scan.medium_count,

            "low": scan.low_count,

            "info": scan.info_count,

            # -------------------------
            # Timestamps
            # -------------------------

            "created_at": scan.created_at,

            "completed_at": scan.completed_at,

            # -------------------------
            # Vulnerability Results
            # -------------------------

            "results": scan.results,
        }