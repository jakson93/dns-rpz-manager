import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class DomainOrigin(str, enum.Enum):
    excel = "excel"
    manual = "manual"


class DomainStatus(str, enum.Enum):
    active = "active"
    removed = "removed"


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    origin: Mapped[DomainOrigin] = mapped_column(Enum(DomainOrigin), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    import_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("import_records.id"), nullable=True)
    status: Mapped[DomainStatus] = mapped_column(Enum(DomainStatus), default=DomainStatus.active)
    added_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    imported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    added_by_user = relationship("User", back_populates="domains")
    import_record = relationship("ImportRecord", back_populates="domains")
