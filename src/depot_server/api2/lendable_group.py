from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.item.repo_lendable_group import LendableGroupRepo

from .models.lendable_group import APILendableGroup, APILendableGroupBase
from depot_server.logic.lendable_group import LendableGroupService
from depot_server.logic.contracts.lendable import CreateLendableGroup, UpdateLendableGroupData
from ..db2.repository.base import ItemNotFound

router = APIRouter(tags=["V2_LendableGroup"], prefix="/lendable_group")

# CRUD operations

@router.post("/")
async def create_item_group(item_group: APILendableGroupBase) -> APILendableGroup:
    """Create a new lendable group"""
    lendable_group = await LendableGroupService.create(
        CreateLendableGroup(
            name=item_group.name,
            description=item_group.description,
            parent=item_group.parent_id,
        )
    )
    return APILendableGroup.from_logic(lendable_group)

@router.get("/")
async def get_item_groups() -> list[APILendableGroup]:
    """Retrieve all lendable groups"""
    lendable_groups = await LendableGroupService.get_all()
    return [APILendableGroup.from_logic(group) for group in lendable_groups]

@router.get("/{lendable_group_id}")
async def get_item_group(lendable_group_id: UUID) -> APILendableGroup:
    """Retrieve a single lendable group by id"""
    try:
        lendable_group = await LendableGroupService.get_by_id(lendable_group_id)
        return APILendableGroup.from_logic(lendable_group)
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemGroup not found")

@router.put("/{lendable_group_id}")
async def update_item_group(lendable_group_id: UUID, item_group: APILendableGroupBase) -> APILendableGroup:
    """Update an existing lendable group"""
    try:
        lendable_group = await LendableGroupService.update_lendable_group(
            lendable_group_id,
            UpdateLendableGroupData(
                name=item_group.name,
                description=item_group.description,
                parent=item_group.parent_id,
            ),
        )
        return APILendableGroup.from_logic(lendable_group)
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemGroup not found")

@router.delete("/{lendable_group_id}")
async def delete_item_group(lendable_group_id: UUID) -> None:
    """Delete a lendable group"""
    try:
        await LendableGroupService.delete_by_id(lendable_group_id)
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemGroup not found")

# Additional endpoints

@router.get("/{lendable_group_id}/children")
async def get_item_group_children(lendable_group_id: UUID) -> list[APILendableGroup]:
    """Retrieve the children of a lendable group"""
    try:
        children = await LendableGroupRepo.get_children_by_parent_id(lendable_group_id)
        return [APILendableGroup.from_logic(child) for child in children]
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemGroup not found")

    
