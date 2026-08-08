from datetime import datetime

from pydantic import BaseModel


class ScanResultResponse(BaseModel):

    id: int
    scan_id: int

    # -----------------------------
    # OWASP ZAP Data
    # -----------------------------
    name: str
    risk: str

    confidence: str | None = None
    description: str | None = None
    solution: str | None = None
    reference: str | None = None

    url: str | None = None
    param: str | None = None
    attack: str | None = None
    evidence: str | None = None

    cwe_id: int | None = None
    wasc_id: int | None = None

    # -----------------------------
    # Gemini AI Data
    # -----------------------------
    ai_explanation: str | None = None
    business_impact: str | None = None
    technical_impact: str | None = None
    remediation_steps: str | None = None
    secure_coding_tip: str | None = None
    priority: str | None = None
    estimated_fix_time: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True


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


class ScanDetailResponse(BaseModel):

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
    completed_at: datetime | None = None

    results: list[ScanResultResponse] = []