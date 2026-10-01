from dataclasses import dataclass
from datetime import date
from uuid import UUID

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
    condition: str | None
    condition_comment: str | None = None
    purpose: UUID | None = None
 