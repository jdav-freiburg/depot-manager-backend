from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from src.depot_server.db2.models.item.item import Item as DbItem
from src.depot_server.db2.repository.item.repo_item import ItemRepo
from .models.item import Item, ItemPending, ItemBase


router = APIRouter()

@router.get("/item")
async def get_items() -> list[Item]:
    db_items = await ItemRepo.get_all_items()
    return [Item.model_validate(item, from_attributes=True) for item in db_items]

@router.get("/item/{item_id}")
async def get_item(item_id: UUID) -> Item:
    db_item = await ItemRepo.get_item_by_id(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item.model_validate(db_item, from_attributes=True)

@router.post("/item")
async def create_item(item: ItemBase) -> Item:
    db_item = await ItemRepo.create_item(**item.model_dump(), item_id=uuid4())
    return Item.model_validate(db_item, from_attributes=True)

@router.put("/item/{item_id}")
async def update_item(item_id: UUID, item: ItemPending) -> Item:
    db_item: DbItem = await ItemRepo.update_item(item_id, **item.model_dump())
    return Item.model_validate(db_item, from_attributes=True)

@router.delete("/item/{item_id}")
async def delete_item(item_id: UUID) -> None:
    await ItemRepo.delete_item(item_id)