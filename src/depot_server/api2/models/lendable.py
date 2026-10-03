from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from depot_server.logic.results.lendable import LogicLendable, LogicLendableLink

class APILendableBase(BaseModel):
    name: str
    description: Optional[str] = None
    storage_location: Optional[UUID] = None
    ausgabepflichtig: bool
    items: dict[UUID, int] = Field(default_factory=dict)# item_id -> quantity

class APICreateLendable(APILendableBase):
    parent: Optional[UUID] = None  # UUID of the parent lendable group if it exists
    items: dict[UUID, int] = Field(..., min_length=1)  # item_id -> quantity

class APIUpdateLendable(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    storage_location: Optional[UUID] = None
    ausgabepflichtig: Optional[bool] = None
    items: Optional[dict[UUID, int]] = None
    in_limbus: Optional[int] = None

class APILendable(APILendableBase):
    id: UUID
    in_limbus: int

    @classmethod
    def from_logic(cls, logic_lendable: LogicLendable) -> "APILendable":
        return cls(
            id=logic_lendable.id,
            name=logic_lendable.name,
            description=logic_lendable.description,
            storage_location=logic_lendable.storage_location,
            ausgabepflichtig=logic_lendable.ausgabepflichtig,
            items={link.purpose_id: link.amount for link in logic_lendable.purposes},
            in_limbus=logic_lendable.in_limbus
        )