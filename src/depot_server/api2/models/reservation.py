from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from depot_server.db2.models.common import ReservationImportance, UserIdField, ReservationType

class ReservationMeta(BaseModel):
    importance: ReservationImportance
    name: Optional[str]
    start: datetime
    end: datetime
    user_id: UserIdField
    type: ReservationType = Field(default=ReservationType.BORROW)
    team_id: Optional[UUID]
    contact: Optional[str]
    active: bool = Field(default=True)
    user_notes: Optional[str]

class ReservationContent(BaseModel):
    item_groups: dict[UUID, int] = {}
    composite_items: dict[UUID, int] = {}

class ReservationPending(ReservationMeta, ReservationContent):
    pass

class Reservation(ReservationPending):
    id: UUID = Field(...)
