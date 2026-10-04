from uuid import UUID
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException

from depot_server.api2.models.lendable import APICreateLendable, APIUpdateLendable, APILendable
from depot_server.logic.lendable import LendableService
from depot_server.logic.contracts.lendable import CreateLendable, UpdateLendableData
from depot_server.logic.reservation import ReservationService
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_lendable import LendableRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_lendable_group import LendableGroupRepo
from depot_server.db2.repository.base import ItemNotFound

router = APIRouter(tags=["V2_Lendable"], prefix="/lendable")

@router.post("/")
async def create_lendable(lendable: APICreateLendable) -> APILendable:
    """Creates a new lendable
    Also creates a new purpose for each item in the lendable and assigns all item_instances without purpose to this lendable.
    """
    # Chech if all items exist
    for item_id in lendable.items.keys():
        if await ItemRepo.get_by_id(item_id) is None:
            raise HTTPException(status_code=404, detail=f"Item {item_id} does not exist")
    purposes = {}
    for item, amount in lendable.items.items():
        purpose = await ItemPurposeRepo.create(description=f"{item} for {lendable.name}")
        purposes[purpose.id] = amount
        await ItemInstanceRepo.assign_unassigned_to_purpose(item, purpose)
    db_lendable = await LendableService.create(CreateLendable(
        name=lendable.name,
        purposes=purposes,
        description=lendable.description,
        parent=lendable.parent,
        ausgabepflichtig=lendable.ausgabepflichtig,
        storage_location=lendable.storage_location
    ))
    reserved = await ReservationService.get_reserved_lendable_amount(db_lendable.id,
                                                                     start_time=datetime.now(ZoneInfo("Europe/Berlin")),
                                                                     end_time=datetime.now(ZoneInfo("Europe/Berlin")))
    operational = await LendableService.get_operational_amount(db_lendable.id)
    available = operational - reserved
    return APILendable.from_logic(db_lendable, available, operational)

@router.get("/")
async def get_lendables() -> list[APILendable]:
    db_lendables = await LendableService.get_all()
    return [APILendable.model_validate(lendable, from_attributes=True) for lendable in db_lendables]

@router.get("/{lendable_id}")
async def get_lendable(lendable_id: UUID) -> APILendable:
    db_lendable = await LendableService.get_by_id(lendable_id)
    reserved = await ReservationService.get_reserved_lendable_amount(db_lendable.id,
                                                                        start_time=datetime.now(ZoneInfo("Europe/Berlin")),
                                                                        end_time=datetime.now(ZoneInfo("Europe/Berlin")))
    operational = await LendableService.get_operational_amount(db_lendable.id)
    available = operational - reserved
    return APILendable.from_logic(db_lendable, available, operational)

@router.put("/{lendable_id}")
async def update_lendable(lendable_id: UUID, lendable: APIUpdateLendable) -> APILendable:
    update_data = lendable.model_dump(exclude_unset=True, exclude={"items"})
    if lendable.items:
        purposes = {}
        for item, amount in lendable.items.items():
            purpose = await ItemPurposeRepo.create(description=f"{item} for {lendable.name}")
            purposes[purpose.id] = amount
            await ItemInstanceRepo.assign_unassigned_to_purpose(item, purpose)
        db_lendable = await LendableService.update(lendable_id, UpdateLendableData(
                **update_data, purposes=purposes))
    else:
        db_lendable = await LendableService.update(lendable_id, UpdateLendableData(
                **update_data))
    return APILendable.model_validate(db_lendable, from_attributes=True)

@router.delete("/{lendable_id}")
async def delete_lendable(lendable_id: UUID) -> None:
    try:
        await LendableRepo.delete_by_id(lendable_id)
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="Lendable not found")