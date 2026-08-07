from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DNSServerCreate(BaseModel):
    name: str
    hostname: str
    port: int = 953
    rndc_key: Optional[str] = None
    is_active: bool = True


class DNSServerUpdate(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[int] = None
    rndc_key: Optional[str] = None
    is_active: Optional[bool] = None


class DNSServerResponse(BaseModel):
    id: int
    name: str
    hostname: str
    port: int
    rndc_key: Optional[str] = None
    is_active: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
