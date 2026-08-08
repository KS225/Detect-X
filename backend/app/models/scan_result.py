from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    scan_id: Mapped[int] = mapped_column(
        ForeignKey("scans.id"),
        nullable=False,
    )

    # -----------------------------
    # OWASP ZAP Data
    # -----------------------------

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    risk: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    solution: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reference: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    param: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    attack: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cwe_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    wasc_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # -----------------------------
    # AI Generated Fields
    # -----------------------------

    ai_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    business_impact: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    technical_impact: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    remediation_steps: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    secure_coding_tip: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    priority: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    estimated_fix_time: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # -----------------------------
    # Timestamp
    # -----------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # -----------------------------
    # Relationship
    # -----------------------------

    scan = relationship(
        "Scan",
        back_populates="results",
    )