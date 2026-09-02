
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from ...db2.models.common import Condition, TotalReportState
from ...db2.models.item.item import PsaCategory
from .item_group import ItemGroup


class ItemRaw(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    report_profile_id: Optional[UUID] = None
    max_lifespan: Optional[timedelta] = None
    max_usage_lifespan: Optional[timedelta] = None
    psa_category: PsaCategory = Field(...)
    storage_location_id: Optional[UUID] = None
    
class ItemBase(ItemRaw):
    group_id: UUID
    lendable: bool = Field(...)

class Item(ItemBase):
    id: UUID = Field(...)
    #total_report_state: Optional[TotalReportState] = Field(...)

class ItemPending(ItemBase):
    change_comment: str = Field(...)


class ItemInstanceRaw(BaseModel):
    external_id: Optional[str] = None
    serial_number: str = Field(...)
    manufacture_date: datetime = Field(...)
    purchase_date: datetime = Field(...)
    first_use_date: datetime = Field(...)
    condition: Condition = Field(...)
    condition_comment: Optional[str] = None
    # created_by: UUID

class ItemInstanceBase(ItemInstanceRaw):
    item_id: UUID

class ItemInstancePending(ItemInstanceBase):
    change_comment: str = Field(...)

class ItemInstance(ItemInstanceBase):
    id: UUID = Field(...)
    created_at: datetime = Field(...)


class FullItemRaw(ItemRaw, ItemInstanceRaw):
    lendable: bool = Field(...)

class FullItem(FullItemRaw):
    id: UUID = Field(description="The unique identifier of the item type")
    group_id: UUID = Field(description="ID of the group that contains only this item type")
    instance_id: UUID = Field(description="ID of the instance of this item")