from datetime import datetime
from uuid import UUID
from dataclasses import dataclass

@dataclass(frozen=True)
class LogicLendableLink:
    id: UUID
    lendable_id: UUID
    amount: int
    purpose_id: UUID
    created_at: datetime

@dataclass(frozen=True)
class LogicLendableLinkArchive(LogicLendableLink):
    changed_at: datetime

@dataclass(frozen=True)
class LogicLendable:
    id: UUID
    name: str
    purposes: list[LogicLendableLink]  # how many of each purpose belong to one lendable
    description: str | None
    parent: UUID | None  # UUID of the parent lendable group if it exists
    ausgabepflichtig: bool
    storage_location_id: UUID | None
    in_limbus: int
    changed_at: datetime

@dataclass(frozen=True)
class LogicLendableGroup:
    id: UUID
    name: str
    description: str | None
    parent: UUID | None  # UUID of the parent lendable group if it exists