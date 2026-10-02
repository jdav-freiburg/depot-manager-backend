from typing import Optional
from uuid import UUID
from datetime import date

from pydantic import BaseModel, Field

from depot_server.db2.models.common import ReservationImportance, ReservationType

class APIReservationMeta(BaseModel):
    name: Optional[str] = None
    start: date
    end: date
    type: ReservationType = Field(default=ReservationType.BORROW)
    importance: ReservationImportance = Field(default=ReservationImportance.TEAM)
    team_id: Optional[UUID] = None
    contact: str
    #active: bool = Field(default=True)
    user_notes: Optional[str] = None

class APIReservationContent(BaseModel):
    items: dict[UUID, int] = Field(default_factory=dict)
    composite_items: dict[UUID, int] = Field(default_factory=dict)

class APIReservationPending(APIReservationMeta, APIReservationContent):
    pass

class APIReservation(APIReservationPending):
    id: UUID = Field(...)
    user_id: UUID
    links: list[dict] = Field(default_factory=list)
