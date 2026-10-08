from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.db2.repository.item.repo_lendable import LendableRepo
from depot_server.db2.repository.item.repo_storage_location import StorageLocationRepo
from depot_server.logic.contracts.item import CreateItem, UpdateItemData, CreateItemInstance
from depot_server.logic.contracts.lendable import CreateLendable
from depot_server.logic.item import ItemService
from depot_server.logic.item_instance import ItemInstanceService, ItemInstanceUniqueConflict
from depot_server.logic.lendable import LendableService
from .models.item import APIItem, APICreateItem, APIUpdateItem
from .models.item_instance import APIItemInstance, APIAddItemInstance


router = APIRouter(tags=["V2_Item"], prefix="/item")

@router.get("/")
async def get_items() -> list[APIItem]:
    db_items = await ItemService.get_all_items()
    result = []
    for item in db_items:
        lendables = await ItemPurposeRepo.get_lendables_by_item(item.id)
        storage_locations = await LendableRepo.get_storage_locations(lendables)
        result.append(APIItem.from_logic(item, lendables=lendables, storage_locations=storage_locations))
    return result

@router.get("/{item_id}")
async def get_item(item_id: UUID) -> APIItem:
    db_item = await ItemService.get_item(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    lendables = await ItemPurposeRepo.get_lendables_by_item(item_id)
    storage_locations = await LendableRepo.get_storage_locations(lendables)
    return APIItem.from_logic(db_item, lendables=lendables, storage_locations=storage_locations)

@router.post("/")
async def create_item(item: APICreateItem) -> APIItem:
    db_item = await ItemService.create_item(CreateItem(**item.model_dump(exclude={"single_lendable"})))
    if item.single_lendable:
        if item.single_lendable.storage_location:
            storage_location = await StorageLocationRepo.get_by_id(item.single_lendable.storage_location)
            if not storage_location:
                raise HTTPException(status_code=404, detail=f"Storage location with id {item.single_lendable.storage_location} not found")
        purpose = await ItemPurposeRepo.create(item_id=db_item.id)
        await LendableService.create(CreateLendable(name=item.name,
                                                    description=item.description,
                                                    ausgabepflichtig=item.single_lendable.ausgabepflichtig,
                                                    purposes={purpose.id: 1},
                                                    storage_location_id=item.single_lendable.storage_location,
                                                    parent=item.single_lendable.parent))
    return APIItem.model_validate(db_item, from_attributes=True)

@router.put("/{item_id}")
async def update_item(item_id: UUID, item: APIUpdateItem) -> APIItem:
    db_item = await ItemService.update_item(item_id, UpdateItemData(**item.model_dump()))
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return APIItem.model_validate(db_item, from_attributes=True)

@router.delete("/{item_id}")
async def delete_item(item_id: UUID) -> None:
    try:
        await ItemRepo.delete_by_id(item_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex

@router.get("/{item_id}/instance")
async def get_item_instances(item_id: UUID) -> list[APIItemInstance]:
    item_instances = await ItemInstanceRepo.get_item_instances_by_item_id(item_id)
    return [APIItemInstance.model_validate(item_instance, from_attributes=True) for item_instance in item_instances]
