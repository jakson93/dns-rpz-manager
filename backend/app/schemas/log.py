from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class LogCreate(BaseModel):
    event: str
    description: str
    details: Optional[Any] = None
    user_id: Optional[int] = None


class LogResponse(BaseModel):
    id: int
    event: str
    description: str
    details: Optional[Any] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
