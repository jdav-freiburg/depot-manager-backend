from uuid import UUID
from datetime import date

from pydantic import BaseModel, Field
from pydantic_core import MISSING
from typing import List, Optional

from depot_server.api2.models.item import APIItemBase
from depot_server.logic.results.item import LogicItemInstance
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item_instance import ItemInstance

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
    lendable_id: Optional[UUID] = None

class APICreateSimilarItemInstance(BaseModel):
    serial_number: str = Field(...)
    external_id: str | None = None
    manufacture_date: date | MISSING = MISSING
    purchase_date: date | MISSING = MISSING
    first_use_date: date | MISSING = MISSING
    condition: Condition | MISSING = MISSING
    condition_comment: str | None | MISSING = MISSING

class APIAddItemInstance(BaseModel):
    external_id: Optional[str] = None
    serial_number: str = Field(...)
    manufacture_date: date = Field(...)
    purchase_date: date = Field(...)
    first_use_date: date = Field(...)
    condition: Condition
    condition_comment: Optional[str] = None

class APIUpdateItemInstance(BaseModel):
    item_id: UUID | MISSING = MISSING
    external_id: str | None | MISSING = MISSING
    serial_number: str | MISSING = MISSING
    manufacture_date: date | None | MISSING = MISSING
    purchase_date: date | None | MISSING = MISSING
    first_use_date: date | None | MISSING = MISSING
    condition: Condition | MISSING = MISSING
    condition_comment: str | None | MISSING = MISSING
    lendable_id: UUID | None | MISSING = MISSING

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

class APICreateFullItem(APIItemBase, APICreateItemInstance):
    pass

class APIFullItem(APICreateFullItem):
    id: UUID = Field(description="The unique identifier of the item type")
    item_id: UUID = Field(description="ID of the instance of this item")
    group_id: Optional[UUID] = None
    lendable_id: Optional[UUID] = Field(description="ID of the lendable this item is linked to")
    storage_location_id: Optional[UUID] = Field(description="ID of the storage location this item is linked to")
    too_old: bool = Field(description="Whether the item instance is too old")
    requires_inspection: bool = Field(description="Whether the item instance requires inspection")

    @classmethod
    async def from_db(cls, db_item_instance: ItemInstance, lendable_id: UUID | None = None, storage_location_id: UUID | None = None) -> "APIFullItem":
        
        return cls(id=db_item_instance.id,
                    item_id=db_item_instance.item.id,
                    name=db_item_instance.item.name,
                    description=db_item_instance.item.description,
                    manufacturer=db_item_instance.item.manufacturer,
                    model=db_item_instance.item.model,
                    report_profile_id=db_item_instance.item.report_profile_id,
                    max_lifespan=db_item_instance.item.max_lifespan,
                    max_usage_lifespan=db_item_instance.item.max_usage_lifespan,
                    psa_category=db_item_instance.item.psa_category,
                    external_id=db_item_instance.external_id,
                    serial_number=db_item_instance.serial_number,
                    manufacture_date=db_item_instance.manufacture_date,
                    purchase_date=db_item_instance.purchase_date,
                    first_use_date=db_item_instance.first_use_date,
                    condition=db_item_instance.condition,
                    condition_comment=db_item_instance.condition_comment,
                    lendable_id=lendable_id,
                    storage_location_id=storage_location_id,
                    too_old=db_item_instance.is_too_old,
                    requires_inspection=await db_item_instance.requires_inspection(),
                )