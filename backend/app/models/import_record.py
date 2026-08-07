import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class ImportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    error = "error"


class ImportRecord(Base):
    __tablename__ = "import_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    total_domains: Mapped[int] = mapped_column(Integer, default=0)
    new_domains: Mapped[int] = mapped_column(Integer, default=0)
    removed_domains: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus), default=ImportStatus.pending)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="imports")
    domains = relationship("Domain", back_populates="import_record")
