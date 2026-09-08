from datetime import timedelta
from typing import Optional, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from depot_server.db2.models.item.item import PsaCategory


class ItemGroupBase(BaseModel):
    name: str
    description: str
    #data: Optional[dict[Any, Any]] = Field(default=None)
    lendable: bool
    parent: Optional[UUID] = Field(default=None)


class ItemGroup(ItemGroupBase):
    id: UUID
    #group_children: list[UUID] | Literal["NotRequested"] = Field(default="NotRequested")


class ItemGroupAmount(BaseModel):
    item_group_id: UUID
    total: int
    available: int
