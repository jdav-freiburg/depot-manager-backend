from datetime import timedelta
from typing import Optional, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from depot_server.db2.models.item.item_group import PsaCategory


class ItemGroupPending(BaseModel):
    name: str
    description: str
    manufacturer: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    enforce_exact_item: bool = Field(default=False)
    id_prefix: Optional[str] = Field(default=None)
    max_lifespan: Optional[timedelta] = Field(default=None)
    max_usage_span: Optional[timedelta] = Field(default=None)
    psa_category: PsaCategory = Field(default=PsaCategory.NONE)
    data: Optional[dict[Any, Any]] = Field(default=None)
    parent: Optional[UUID] = Field(default=None)


class ItemGroup(ItemGroupPending):
    id: UUID
    group_children: list[UUID] | Literal["NotRequested"] = Field(default="NotRequested")
