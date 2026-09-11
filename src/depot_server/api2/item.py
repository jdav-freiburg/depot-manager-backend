from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.logic.item import ItemService
from .models.item import Item, ItemPending, ItemBase, ItemInstance, FullItem, FullItemRaw

itemservice = ItemService()

router = APIRouter()

@router.get("/item")
async def get_items() -> list[Item]:
    db_items = await ItemService.get_all_items()
    return [Item.model_validate(item, from_attributes=True) for item in db_items]

@router.get("/item/{item_id}")
async def get_item(item_id: UUID) -> Item:
    db_item = await ItemService.get_item(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item.model_validate(db_item, from_attributes=True)

@router.post("/item")
async def create_item(item: FullItemRaw) -> FullItem:
    full_item = await itemservice.create_item(item)
    return FullItem.model_validate(full_item, from_attributes=True)

@router.put("/item/{item_id}")
async def update_item(item_id: UUID, item: ItemPending) -> Item:
    db_item = await ItemService.update_item(item_id, item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item.model_validate(db_item, from_attributes=True)

@router.delete("/item/{item_id}")
async def delete_item(item_id: UUID) -> None:
    try:
        await ItemRepo.delete_item(item_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex

@router.get("/item/{item_id}/instances")
async def get_item_instances(item_id: UUID) -> list[ItemInstance]:
    item_instances = await ItemInstanceRepo.get_item_instances_by_item_id(item_id)
    return [ItemInstance.model_validate(item_instance, from_attributes=True) for item_instance in item_instances]