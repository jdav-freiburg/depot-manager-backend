from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.api2.models.item_composite import ItemComposite, ItemCompositeBase
from depot_server.logic.item_composite import ItemCompositeService
from depot_server.db2.repository.base import ItemNotFound

router = APIRouter()

@router.get("/item_composite")
async def get_item_composites() -> list[ItemComposite]:
    """Retrieve all item_composites"""
    composites = await ItemCompositeService.get_all()
    return [ItemComposite.model_validate(composite, from_attributes=True) for composite in composites]

@router.get("/item_composite/{item_composite_id}")
async def get_item_composite(item_composite_id: UUID) -> ItemComposite:
    """Retrieve a specific item_composite by ID"""
    try:
        composite = await ItemCompositeService.get_by_id(item_composite_id)
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=f"ItemComposite with id {item_composite_id} not found")
    if not composite:
        raise HTTPException(status_code=404, detail="ItemComposite not found")
    return ItemComposite.model_validate(composite, from_attributes=True)

@router.post("/item_composite")
async def create_item_composite(item_composite: ItemCompositeBase) -> ItemComposite:
    """Create a new item_composite"""
    composite = await ItemCompositeService.create(item_composite)
    return ItemComposite.model_validate(composite, from_attributes=True)

@router.put("/item_composite/{item_composite_id}")
async def update_item_composite(item_composite_id: UUID, item_composite: ItemCompositeBase) -> ItemComposite:
    """Update an existing item_composite"""
    composite = await ItemCompositeService.update(item_composite_id, item_composite)
    if not composite:
        raise HTTPException(status_code=404, detail="ItemComposite not found")
    return ItemComposite.model_validate(composite, from_attributes=True)

@router.delete("/item_composite/{item_composite_id}")
async def delete_item_composite(item_composite_id: UUID) -> None:
    """Delete an existing item_composite"""
    try:
        await ItemCompositeService.delete(item_composite_id)
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=f"ItemComposite with id {item_composite_id} not found")