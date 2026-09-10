from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.models.item.item_group import ItemGroup as DbItemGroup
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.logic.item_group import item_group_from_orm, ItemGroupService
from .models.item_group import ItemGroup, ItemGroupBase
from ..db2.repository.base import ItemNotFound

router = APIRouter()
item_group_service = ItemGroupService()

@router.get("/item_group")
async def get_item_groups() -> list[ItemGroup]:
    """Retrieve all item_groups"""
    db_item_groups = await ItemGroupRepo.get_all()
    return [item_group_from_orm(item_group) for item_group in db_item_groups]


@router.get("/item_group/{item_group_id}")
async def get_item_group(item_group_id: UUID) -> ItemGroup:
    """Retrieve a single item_group by id"""
    db_item_group = await ItemGroupRepo.get_by_id(item_group_id)
    if not db_item_group:
        raise HTTPException(status_code=404, detail="ItemGroup not found")
    return item_group_from_orm(db_item_group)


@router.post("/item_group")
async def create_item_group(item_group: ItemGroupBase) -> ItemGroup:
    """Create a new item_group"""
    try:
        db_item_group = await ItemGroupRepo.create(
            **item_group.model_dump())
        return item_group_from_orm(db_item_group)
    except ItemNotFound as ex:
        raise HTTPException(status_code=422, detail=str(ex))


@router.put("/item_group/{item_group_id}")
async def update_item_group(item_group_id: UUID, item_group: ItemGroupBase) -> ItemGroup:
    """Update an existing item_group"""
    try:
        db_item_group = await ItemGroupRepo.update_item_group(item_group_id, **item_group.model_dump())
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    if not db_item_group:
        raise HTTPException(status_code=404, detail="ItemGroup not found")
    return item_group_from_orm(db_item_group)


@router.delete("/item_group/{item_group_id}")
async def delete_item_group(item_group_id: UUID) -> None:
    """Delete an item_group"""
    try:
        await ItemGroupRepo.delete_by_id(item_group_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/item_group/{item_group_id}/children")
async def get_item_group_children(item_group_id: UUID) -> list[ItemGroup]:
    """Retrieve the children of an item_group"""
    children = await ItemGroupRepo.get_children_by_parent_id(item_group_id)
    if children is None:
        raise HTTPException(status_code=404, detail="ItemGroup not found")
    return [item_group_from_orm(child) for child in children]
