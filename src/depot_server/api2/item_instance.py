from uuid import UUID

from fastapi import APIRouter, HTTPException

from ..db2.repository.item.repo_item_instance import ItemInstanceRepo
from ..db2.repository.base import ItemNotFound
from ..logic.item_instance import ItemInstanceService, ItemInstanceUniqueConflict

from .models.item import ItemInstance, ItemInstanceBase, ItemInstancePending

router = APIRouter()

@router.get("/item_instance")
async def get_item_instances() -> list[ItemInstance]:
    db_item_instances = await ItemInstanceRepo.get_all_item_instances()
    return [ItemInstance.model_validate(item_instance, from_attributes=True) for item_instance in db_item_instances]

@router.get("/item_instance/{item_instance_id}")
async def get_item_instance(item_instance_id: UUID) -> ItemInstance:
    db_item_instance = await ItemInstanceRepo.get_item_instance_by_id(item_instance_id)
    if not db_item_instance:
        raise HTTPException(status_code=404, detail="ItemInstance not found")
    return ItemInstance.model_validate(db_item_instance, from_attributes=True)

@router.post("/item_instance")
async def create_item_instance(item_instance: ItemInstanceBase) -> ItemInstance:
    try:
        db_item_instance = await ItemInstanceService.create_item_instance(item_instance)
    except ItemInstanceUniqueConflict as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    return ItemInstance.model_validate(db_item_instance, from_attributes=True)

@router.put("/item_instance/{item_instance_id}")
async def update_item_instance(item_instance_id: UUID, item_instance: ItemInstancePending) -> ItemInstance:
    try:
        db_item_instance = await ItemInstanceService.update_item_instance(item_instance_id, item_instance)
    except ItemInstanceUniqueConflict as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    if not db_item_instance:
        raise HTTPException(status_code=404, detail="ItemInstance not found")
    return ItemInstance.model_validate(db_item_instance, from_attributes=True)

@router.delete("/item_instance/{item_instance_id}")
async def delete_item_instance(item_instance_id: UUID) -> None:
    try:
        await ItemInstanceRepo.delete_item_instance(item_instance_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
