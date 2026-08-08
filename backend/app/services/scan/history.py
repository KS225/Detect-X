from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.user import User


class ScanHistoryService:

    @staticmethod
    def execute(
        db: Session,
        user: User,
    ):

        scans = (
            db.query(Scan)
            .filter(
                Scan.user_id == user.id,
            )
            .order_by(
                Scan.created_at.desc()
            )
            .all()
        )

        response = []

        for scan in scans:

            response.append(
                {
                    "id": scan.id,

                    "website": scan.website.url,

                    "security_score": scan.security_score,

                    "total_alerts": scan.total_alerts,

                    "high": scan.high_count,
                    "medium": scan.medium_count,
                    "low": scan.low_count,
                    "info": scan.info_count,

                    "status": scan.status,

                    "created_at": scan.created_at,
                }
            )

        return response