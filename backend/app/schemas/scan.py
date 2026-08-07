from datetime import datetime

from pydantic import BaseModel


class ScanHistoryResponse(BaseModel):

    id: int

    website: str

    security_score: int

    total_alerts: int

    high: int

    medium: int

    low: int

    info: int

    status: str

    created_at: datetime

    class Config:
        from_attributes = True