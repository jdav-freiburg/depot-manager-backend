
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta

from depot_server.logic.results.item import LogicItemInstance

from ...db2.models.common import Condition, TotalReportState
from ...db2.models.item.item import PsaCategory


# Models for Item

class APIItemBase(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    report_profile_id: Optional[UUID] = None
    max_lifespan: Optional[timedelta] = None
    max_usage_lifespan: Optional[timedelta] = None
    psa_category: PsaCategory = Field(...)

class APICreateItem(APIItemBase):
    create_single_lendable: bool = Field(..., description="Whether a lendable containing only this item should also be created")
    
class APIItem(APIItemBase):
    id: UUID = Field(...)
    lendables: List[UUID] = Field(default_factory=list)
    storage_locations: List[UUID] = Field(default_factory=list)

# Models for ItemInstance

class APIItemInstanceBase(BaseModel):
    item_id: UUID = Field(...)
    external_id: Optional[str] = None
    serial_number: str = Field(...)
    manufacture_date: date = Field(...)
    purchase_date: date = Field(...)
    first_use_date: date = Field(...)
    condition: Optional[Condition] = None
    condition_comment: Optional[str] = None
    # created_by: UUID

class APICreateItemInstance(APIItemInstanceBase):
    lendable: Optional[UUID] = None

class APIAddItemInstance(BaseModel):
    external_id: Optional[str] = None
    serial_number: str = Field(...)
    manufacture_date: date = Field(...)
    purchase_date: date = Field(...)
    first_use_date: date = Field(...)
    condition: Optional[Condition] = None
    condition_comment: Optional[str] = None

class APIItemInstance(APIItemInstanceBase):
    id: UUID = Field(...)
    #created_at: datetime = Field(...)

    @classmethod
    def from_logic(cls, item_instance: LogicItemInstance) -> "APIItemInstance":
        return cls(
            id=item_instance.id,
            item_id=item_instance.item_id,
            external_id=item_instance.external_id,
            serial_number=item_instance.serial_number,
            manufacture_date=item_instance.manufacture_date,
            purchase_date=item_instance.purchase_date,
            first_use_date=item_instance.first_use_date,
            condition=item_instance.condition,
            condition_comment=item_instance.condition_comment,
        )


# Models to instantly create a lendable from nothing

class APICreateFullItem(APICreateItem, APICreateItemInstance):
    pass

class APIFullItem(APICreateFullItem):
    id: UUID = Field(description="The unique identifier of the item type")
    item_id: UUID = Field(description="ID of the instance of this item")
    group_id: Optional[UUID] = None
    lendable_id: Optional[UUID] = Field(description="ID of the lendable this item is linked to")
    storage_location_id: Optional[UUID] = Field(description="ID of the storage location this item is linked to")
    too_old: bool = Field(description="Whether the item instance is too old")
    requires_inspection: bool = Field(description="Whether the item instance requires inspection")