from uuid import UUID
from dataclasses import dataclass

from depot_server.logic.contracts.base import _Unset, BaseContract


@dataclass(frozen=True)
class CreateLendable(BaseContract):
    name: str
    purposes: dict[UUID, int]  # how many of each purpose belong to one lendable
    description: str | None = None
    parent: UUID | None = None  # UUID of the parent lendable group if it exists
    ausgabepflichtig: bool = False 
    storage_location: UUID | None = None

@dataclass(frozen=True)
class CreateLendableGroup(BaseContract):
    name: str
    description: str | None = None
    parent: UUID | None = None  # UUID of the parent lendable group if it exists


# Update contracts

@dataclass(frozen=True)
class UpdateLendableData(BaseContract):
    name: str | _Unset = _Unset()
    description: str | None | _Unset = _Unset()
    ausgabepflichtig: bool | _Unset = _Unset() 
    storage_location: UUID | None | _Unset = _Unset()
    parent: UUID | None | _Unset = _Unset()  # UUID of the parent lendable group if it exists
    in_limbus: int | _Unset = _Unset()  # 0 or 1, if the lendable is in limbus or not
    purposes: dict[UUID, int] | _Unset = _Unset()  # how many of each purpose belong to one lendable

@dataclass(frozen=True)
class UpdateLendableGroup(BaseContract):
    name: str | _Unset = _Unset()
    description: str | None | _Unset = _Unset()
    parent: UUID | None | _Unset = _Unset()


@dataclass(frozen=True)
class UpdateLendableGroupData(BaseContract):
    name: str | _Unset = _Unset()
    description: str | None | _Unset = _Unset()
    parent: UUID | None | _Unset = _Unset()
    ausgabepflichtig: bool | _Unset = _Unset() 
    storage_location: UUID | None | _Unset = _Unset()