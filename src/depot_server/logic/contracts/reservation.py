from dataclasses import dataclass
from datetime import date
from uuid import UUID

from depot_server.db2.models.common import ReservationImportance, ReservationType
from depot_server.logic.contracts.base import BaseContract, _Unset


@dataclass(frozen=True)
class CreateReservation(BaseContract):
    name: str | None
    start: date
    end: date
    user: UUID
    team: UUID | None
    contact: str
    user_notes: str | None
    reservation_importance: ReservationImportance
    reservation_type: ReservationType
    lendables: dict[UUID, int]  # lendable_id -> amount

@dataclass(frozen=True)
class CollectReservation(BaseContract):
    reservation_id: UUID
    collector: str
    links: dict[UUID, "CollectLendable"]  # link_reservation_lendable_id -> CollectLendable

@dataclass(frozen=True)
class CollectLendable(BaseContract):
    borrowed: date
    borrowed_message: str | None
    picked_up_amount: int
    missing_amount: int
    # Add a default value for the missing_amount field

@dataclass(frozen=True)
class ReturnReservation(BaseContract):
    reservation_id: UUID
    returned: date
    links: dict[UUID, "ReturnLendable"]  # link_reservation_lendable_id -> ReturnLendable

@dataclass(frozen=True)
class ReturnLendable(BaseContract):
    returned_amount: int
    returned_message: str | None

# Update contracts

@dataclass(frozen=True)
class UpdateReservationLinkData(BaseContract):
    amount: int
    borrowed: date | None | _Unset = _Unset()
    borrowed_message: str | None | _Unset = _Unset()
    returned: date | None | _Unset = _Unset()
    returned_message: str | None | _Unset = _Unset()
    returned_amount: int | None | _Unset = _Unset()
    missing_amount: int | None | _Unset = _Unset()

@dataclass(frozen=True)
class UpdateReservationData(BaseContract):
    name: str | None | _Unset = _Unset()
    user: UUID | None | _Unset = _Unset()
    user_notes: str | None | _Unset = _Unset()
    contact: str | None | _Unset = _Unset()
    start: date | _Unset = _Unset()
    end: date | _Unset = _Unset()
    team: UUID | None | _Unset = _Unset()
    reservation_type: ReservationType | _Unset = _Unset()
    reservation_importance: ReservationImportance | _Unset = _Unset()
    links: dict[UUID, UpdateReservationLinkData] | _Unset = _Unset()  # link_reservation_lendable_id -> UpdateReservationLinkData



    
