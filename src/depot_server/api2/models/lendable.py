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
    available: int = Field(description="How many could be reserved. Is smaller if some are already reserved.")
    operational: int = Field(description="The amount of lendables that should exist if all things that are not broken are there")
    in_limbus: int = Field(description="How many lendables nobody knows where they are. They are lost but could reappear")

    @classmethod
    def from_logic(cls, logic_lendable: LogicLendable, available: int, operational: int) -> "APILendable":
        return cls(
            id=logic_lendable.id,
            name=logic_lendable.name,
            description=logic_lendable.description,
            storage_location=logic_lendable.storage_location,
            ausgabepflichtig=logic_lendable.ausgabepflichtig,
            items={link.purpose_id: link.amount for link in logic_lendable.purposes},
            in_limbus=logic_lendable.in_limbus,
            available=available,
            operational=operational
        )