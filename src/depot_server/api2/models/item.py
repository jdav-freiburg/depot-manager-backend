
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_core import MISSING
from datetime import timedelta

from ...db2.models.item.item import PsaCategory
from depot_server.logic.results.item import LogicItem

class APIItemBase(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    report_profile_id: Optional[UUID] = None
    max_lifespan: Optional[timedelta] = None
    max_usage_lifespan: Optional[timedelta] = None
    psa_category: PsaCategory = Field(...)

class OptionalCreateLendable(BaseModel):
    ausgabepflichtig: bool
    storage_location: Optional[UUID] = None
    parent: Optional[UUID] = None  # UUID of the parent lendable group if it exists

class APICreateItem(APIItemBase):
    single_lendable: OptionalCreateLendable | None = Field(default=None, description="If a lendable containing only this item should also be created")
    
class APIItem(APIItemBase):
    id: UUID = Field(...)
    lendables: List[UUID] = Field(default_factory=list)
    storage_locations: List[UUID] = Field(default_factory=list)

    @classmethod
    def from_logic(cls, logic_item: LogicItem, lendables: List[UUID], storage_locations: List[UUID]) -> "APIItem":
        return cls(**logic_item.all_to_kwargs(), lendables=lendables, storage_locations=storage_locations)
            

class APIUpdateItem(BaseModel):
    name: str | None | MISSING = MISSING
    description: str | None | MISSING = MISSING
    manufacturer: str | None | MISSING = MISSING
    model: str | None | MISSING = MISSING
    report_profile_id: UUID | None | MISSING = MISSING
    max_lifespan: timedelta | None | MISSING = MISSING
    max_usage_lifespan: timedelta | None | MISSING = MISSING
    psa_category: PsaCategory | None | MISSING = MISSING
