from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models.import_record import ImportStatus


class ImportResponse(BaseModel):
    id: int
    filename: str
    total_domains: int
    new_domains: int
    removed_domains: int
    status: ImportStatus
    error_message: Optional[str] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ImportListResponse(BaseModel):
    items: List[ImportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImportPreview(BaseModel):
    filename: str
    domains: List[str]
    total_count: int
    new_domains: Optional[int] = None
    existing_domains: Optional[int] = None
