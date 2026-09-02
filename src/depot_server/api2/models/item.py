
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field
from datetime import datetime

from ...db2.models.common import Condition, TotalReportState


class ItemBase(BaseModel):
    external_id: Optional[str] = None
    report_profile_id: Optional[UUID] = None
    group_id: UUID
    name: str = Field(...)
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacture_date: Optional[datetime] = None
    purchase_date: Optional[datetime] = None
    first_use_date: Optional[datetime] = None
    lendable: bool = True
    condition: Condition = Field(...)
    condition_comment: Optional[str] = None
    storage_location_id: Optional[UUID] = None
    composite_item_id: Optional[UUID] = None
    created_by: UUID

class ItemPending(ItemBase):
    change_comment: str = Field(...)


class Item(ItemBase):
    id: UUID = Field(...)
    #total_report_state: Optional[TotalReportState] = Field(...)