from uuid import UUID

from pydantic_core import MISSING
from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.db2.repository.report.repo_inspection_report import InspectionReportRepo
from depot_server.logic.contracts.item import CreateItemInstance, UpdateItemInstanceData

from ..db2.repository.item.repo_item_instance import ItemInstanceRepo
from ..db2.repository.item.repo_lendable import LendableRepo
from ..db2.repository.base import ItemNotFound
from ..logic.item_instance import ItemInstanceService, ItemInstanceUniqueConflict

from .models.item_instance import APICreateItemInstance, APICreateSimilarItemInstance, APIFullItem, APIItemInstance, APIUpdateItemInstance

router = APIRouter(tags=["V2_ItemInstance"], prefix="/item_instance")


# CRUD operations for ItemInstance

@router.post("/")
async def create_item_instance(item_instance: APICreateItemInstance) -> APIItemInstance:
    item_instance_data = item_instance.model_dump(exclude={"lendable_id"})
    if item_instance.lendable_id:
        linking_purpose = await ItemPurposeRepo.get_linking_purpose(item_instance.item_id, item_instance.lendable_id)
        if linking_purpose is None:
            raise HTTPException(status_code=400, detail=f"Item {item_instance.item_id} is not in lendable {item_instance.lendable_id}")
        contract = CreateItemInstance(**item_instance_data, purpose_id=linking_purpose)
    else:
        contract = CreateItemInstance(**item_instance_data)
    try:
        db_item_instance = await ItemInstanceService.create(contract)
        return APIItemInstance.model_validate(db_item_instance, from_attributes=True)
    except ItemInstanceUniqueConflict as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    
@router.get("/")
async def get_item_instances() -> list[APIItemInstance]:
    db_item_instances = await ItemInstanceRepo.get_all()
    return [APIItemInstance.model_validate(item_instance, from_attributes=True) for item_instance in db_item_instances]

@router.get("/expired")
async def get_expired_item_instances() -> list[APIItemInstance]:
    expired_item_instances = await ItemInstanceService.get_expired_item_instances()
    return [APIItemInstance.model_validate(item_instance, from_attributes=True) for item_instance in expired_item_instances]

@router.get("/requires_inspection")
async def get_item_instances_requiring_inspection() -> list[APIItemInstance]:
    item_instances = await ItemInstanceService.get_item_instances_requiring_inspection()
    return [APIItemInstance.model_validate(item_instance, from_attributes=True) for item_instance in item_instances]

@router.get("/{item_instance_id}")
async def get_item_instance(item_instance_id: UUID) -> APIFullItem:
    try:
        db_item_instance = await ItemInstanceRepo.get_full_item(item_instance_id)
        if not db_item_instance:
            raise ItemNotFound(f"Item instance with id {item_instance_id} not found")
        if db_item_instance.purpose and db_item_instance.purpose.lendable_purpose_link:
            lendable_id = db_item_instance.purpose.lendable_purpose_link[0].lendable_id
            lendable = await LendableRepo.get_by_id(lendable_id)
            storage_location_id = lendable.storage_location_id if lendable else None
        else:
            lendable_id = None
            storage_location_id = None
        return await APIFullItem.from_db(db_item_instance, lendable_id, storage_location_id)
    
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemInstance not found")
    
@router.put("/{item_instance_id}")
async def update_item_instance(item_instance_id: UUID, item_instance: APIUpdateItemInstance) -> APIItemInstance:
    item_instance_old = await ItemInstanceRepo.get_by_id(item_instance_id)
    if not item_instance_old:
        raise HTTPException(status_code=404, detail="ItemInstance not found")
    try:
        if item_instance.lendable_id != MISSING:
            item_id = item_instance.item_id if item_instance.item_id != MISSING else item_instance_old.item_id
            purpose = await ItemPurposeRepo.get_linking_purpose(item_id, item_instance.lendable_id)
        db_item_instance = await ItemInstanceService.update(item_instance_id,
                                                UpdateItemInstanceData(**item_instance.model_dump(exclude={"lendable_id"})))
    except ItemInstanceUniqueConflict as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemInstance not found")

    return APIItemInstance.model_validate(db_item_instance, from_attributes=True)

@router.delete("/{item_instance_id}")
async def delete_item_instance(item_instance_id: UUID) -> None:
    try:
        await ItemInstanceRepo.delete_by_id(item_instance_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex

@router.post("/{item_instance_id}")
async def create_similar(item_instance_id: UUID, item_instance: APICreateSimilarItemInstance) -> APIItemInstance:
    progenitor_instance = await ItemInstanceRepo.get_by_id(item_instance_id)
    if not progenitor_instance:
        raise HTTPException(status_code=404, detail="ItemInstance not found")
    try:
        created_item_instance = await ItemInstanceService.create(CreateItemInstance(**item_instance.model_dump(),
                                                                                    item_id=progenitor_instance.item_id,
                                                                                    purpose_id=progenitor_instance.purpose_id))
        return APIItemInstance.model_validate(created_item_instance, from_attributes=True)
    except ItemInstanceUniqueConflict:
        raise HTTPException(status_code=409, detail="Serial number or external id already exists.")


@router.get("/{item_instance_id}/inspection_report")
async def get_inspection_reports(item_instance_id: UUID):
    inspection_reports = await InspectionReportRepo.get_by_item_instance_id(item_instance_id)
    if not inspection_reports:
        raise HTTPException(status_code=404, detail="Inspection reports not found")
    return inspection_reports  # TODO: Create Pydantic model for InspectionReport and enforce type

