from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    website_id: Mapped[int] = mapped_column(
        ForeignKey("websites.id"),
        nullable=False,
    )

    # -----------------------------
    # Scan Status
    # -----------------------------

    status: Mapped[str] = mapped_column(
        String(20),
        default="Running",
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    scan_stage: Mapped[str] = mapped_column(
        String(50),
        default="Initializing",
    )

    # -----------------------------
    # Security Results
    # -----------------------------

    security_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    total_alerts: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    high_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    medium_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    low_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    info_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # -----------------------------
    # Timestamps
    # -----------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    user = relationship(
        "User",
        back_populates="scans",
    )

    website = relationship(
        "Website",
        back_populates="scans",
    )

    results = relationship(
        "ScanResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )