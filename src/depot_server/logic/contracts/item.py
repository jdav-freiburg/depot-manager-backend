from dataclasses import dataclass
from datetime import date
from uuid import UUID

from depot_server.logic.contracts.base import _Unset, BaseContract

@dataclass(frozen=True)
class CreateItem(BaseContract):
    name: str
    description: str | None
    manufacturer: str | None
    model: str | None
    report_profile_id: UUID | None
    max_lifespan: int | None
    max_usage_lifespan: int | None
    psa_category: str | None

@dataclass(frozen=True)
class CreateItemInstance(BaseContract):
    item_id: UUID
    serial_number: str
    manufacture_date: date
    purchase_date: date
    first_use_date: date
    condition: str | None
    condition_comment: str | None = None
    external_id: str | None = None
    purpose: UUID | None = None

@dataclass(frozen=True)
class UpdateItemData(BaseContract):
    name: str | None | _Unset = _Unset()
    description: str | None | _Unset = _Unset()
    manufacturer: str | None | _Unset = _Unset()
    model: str | None | _Unset = _Unset()
    report_profile_id: UUID | None | _Unset = _Unset()
    max_lifespan: int | None | _Unset = _Unset()
    max_usage_lifespan: int | None | _Unset = _Unset()
    psa_category: str | None | _Unset = _Unset()

@dataclass(frozen=True)
class UpdateItemInstanceData(BaseContract):
    item_id: UUID | None | _Unset = _Unset()
    serial_number: str | None | _Unset = _Unset()
    manufacture_date: date | None | _Unset = _Unset()
    purchase_date: date | None | _Unset = _Unset()
    first_use_date: date | None | _Unset = _Unset()
    condition: str | None | _Unset = _Unset()
    condition_comment: str | None | _Unset = _Unset()
    external_id: str | None | _Unset = _Unset()
    purpose: UUID | None | _Unset = _Unset()