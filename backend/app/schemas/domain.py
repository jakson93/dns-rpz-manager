from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models.domain import DomainOrigin, DomainStatus


class DomainCreate(BaseModel):
    domain: str
    motivo: Optional[str] = None


class DomainResponse(BaseModel):
    id: int
    domain: str
    origin: DomainOrigin
    source_file: Optional[str] = None
    import_id: Optional[int] = None
    status: DomainStatus
    added_by_user_id: Optional[int] = None
    motivo: Optional[str] = None
    imported_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DomainListResponse(BaseModel):
    items: List[DomainResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DomainStats(BaseModel):
    total_active: int
    total_removed: int
    total_domains: int
    today_added: int
    today_removed: int
