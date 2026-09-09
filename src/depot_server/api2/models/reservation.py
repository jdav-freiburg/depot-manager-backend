from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from depot_server.db2.models.common import ReservationImportance, ReservationType

class ReservationMeta(BaseModel):
    name: Optional[str]
    start: datetime
    end: datetime
    type: ReservationType = Field(default=ReservationType.BORROW)
    importance: ReservationImportance = Field(default=ReservationImportance.TEAM)
    team_id: Optional[UUID] = None
    contact: str
    #active: bool = Field(default=True)
    user_notes: Optional[str] = None

class ReservationContent(BaseModel):
    item_groups: dict[UUID, int] = {}
    composite_items: dict[UUID, int] = {}

class ReservationPending(ReservationMeta, ReservationContent):
    pass

class Reservation(ReservationPending):
    id: UUID = Field(...)
    user_id: UUID
