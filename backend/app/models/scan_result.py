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

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    risk: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    solution: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    reference: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    param: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    attack: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    evidence: Mapped[str] = mapped_column(
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    scan = relationship(
        "Scan",
        back_populates="results",
    )