from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class APIAnnouncementPending(BaseModel):
    title: str
    text: str
    expires: Optional[date]
    is_visible: bool = Field(default=False)
    is_pinned: bool = Field(default=False)


class APIAnnouncement(APIAnnouncementPending):
    id: UUID
    author: str
    timestamp: datetime
