from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.logic.contracts.item import CreateItem, UpdateItemData, CreateItemInstance
from depot_server.logic.contracts.lendable import CreateLendable
from depot_server.logic.item import ItemService
from depot_server.logic.item_instance import ItemInstanceService, ItemInstanceUniqueConflict
from depot_server.logic.lendable import LendableService
from .models.item import APIItem, APICreateItem, APIItemInstance, APIAddItemInstance


router = APIRouter(tags=["V2_Item"], prefix="/item")

@router.get("/")
async def get_items() -> list[APIItem]:
    db_items = await ItemService.get_all_items()
    return [APIItem.model_validate(item, from_attributes=True) for item in db_items]

@router.get("/{item_id}")
async def get_item(item_id: UUID) -> APIItem:
    db_item = await ItemService.get_item(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return APIItem.model_validate(db_item, from_attributes=True)

@router.post("/")
async def create_item(item: APICreateItem) -> APIItem:
    if item.create_single_lendable:
        purpose = await ItemPurposeRepo.create(description=f"{item.name}")
        await LendableService.create(CreateLendable(name=item.name,
                                                    description=item.description,
                                                    ausgabepflichtig=False,
                                                    purposes={purpose.id: 1},
                                                    storage_location=None,
                                                    parent=None))
    db_item = await ItemService.create_item(CreateItem(**item.model_dump()))
    return APIItem.model_validate(db_item, from_attributes=True)

@router.put("/{item_id}")
async def update_item(item_id: UUID, item: APICreateItem) -> APIItem:
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

@router.post("/{item_id}/instance")
async def create_item_instance(item_id: UUID, item_instance: APIAddItemInstance) -> APIItemInstance:
    # TODO infer purpose ad add to creation
    try:
        db_item_instance = await ItemInstanceService.create(CreateItemInstance(item_id=item_id, **item_instance.model_dump()))
        return APIItemInstance.model_validate(db_item_instance, from_attributes=True)
    except ItemInstanceUniqueConflict as ex:
        raise HTTPException(400, detail=str(ex))