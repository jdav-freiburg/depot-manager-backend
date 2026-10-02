from dataclasses import dataclass
from datetime import date
from uuid import UUID

from depot_server.db2.models.common import Condition

@dataclass(frozen=True)
class LogicItem:
    id: UUID
    name: str
    description: str | None
    manufacturer: str | None
    model: str | None
    report_profile_id: UUID | None
    max_lifespan: int | None
    max_usage_lifespan: int | None
    psa_category: str | None

@dataclass(frozen=True)
class LogicItemInstance:
    id: UUID
    item_id: UUID
    external_id: str | None
    serial_number: str
    manufacture_date: date
    purchase_date: date
    first_use_date: date
    condition: Condition | None
    condition_comment: str | None = None
    purpose: UUID | None = None

@dataclass(frozen=True)
class LogicFullItem:
    id: UUID  # item instance id
    item_id: UUID
    # item fields
    name: str
    description: str | None
    manufacturer: str | None
    model: str | None
    report_profile_id: UUID | None
    max_lifespan: int | None
    max_usage_lifespan: int | None
    psa_category: str | None
    # item instance fields
    external_id: str | None
    serial_number: str
    manufacture_date: date
    purchase_date: date
    first_use_date: date
    condition: Condition | None
    condition_comment: str | None
    # infered fields
    lendable_id: UUID | None
    storage_location_id: UUID | None
    too_old: bool
    requires_inspection: bool