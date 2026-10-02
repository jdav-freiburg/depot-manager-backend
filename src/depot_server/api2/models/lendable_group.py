from datetime import timedelta
from typing import Optional, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from depot_server.db2.models.item.lendable_group import LendableGroup
from depot_server.logic.results.lendable import LogicLendableGroup


class APILendableGroupBase(BaseModel):
    name: str
    description: str | None = None
    #data: Optional[dict[Any, Any]] = Field(default=None)
    parent_id: Optional[UUID] = Field(default=None)


class APILendableGroup(APILendableGroupBase):
    id: UUID
    #group_children: list[UUID] | Literal["NotRequested"] = Field(default="NotRequested")

    @classmethod
    def from_logic(cls, group: LogicLendableGroup | LendableGroup) -> "APILendableGroup":
        return cls(
            id=group.id,
            name=group.name,
            description=group.description,
            parent_id=group.parent,
        )

