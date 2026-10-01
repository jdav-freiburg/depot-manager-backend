from dataclasses import dataclass
from datetime import date
from uuid import UUID

from depot_server.db2.models.common import ReservationType
from depot_server.db2.models.common import ReservationImportance


@dataclass(frozen=True)
class LogicReservationLendableLink:
    id: UUID
    lendable_id: UUID
    amount: int
    missing_amount: int | None
    returned_amount: int | None
    borrowed: date | None
    borrowed_message: str | None
    returned: date | None
    returned_message: str | None

@dataclass(frozen=True)
class LogicFullReservation:
    id: UUID
    user_id: UUID
    name: str | None
    collector: str | None
    user_notes: str | None
    contact: str
    start: date
    end: date
    team_id: UUID | None
    reservation_type: ReservationType
    importance: ReservationImportance
    links: list[LogicReservationLendableLink]
