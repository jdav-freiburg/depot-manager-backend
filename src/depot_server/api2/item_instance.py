from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.report.repo_inspection_report import InspectionReportRepo
from depot_server.logic.contracts.item import CreateItemInstance, UpdateItemInstanceData

from ..db2.repository.item.repo_item_instance import ItemInstanceRepo
from ..db2.repository.base import ItemNotFound
from ..logic.item_instance import ItemInstanceService, ItemInstanceUniqueConflict

from .models.item import APICreateItem, APICreateItemInstance, APIFullItem, APIItemInstance, APIItemInstanceBase

router = APIRouter(tags=["V2_ItemInstance"], prefix="/item_instance")


# CRUD operations for ItemInstance

@router.post("/")
async def create_item_instance(item_instance: APICreateItemInstance) -> APIItemInstance:
    item_instance_data = item_instance.model_dump(exclude={"lendable"})
    if item_instance.lendable:
        linking_purpose = await ItemInstanceService.get_linking_purpose(item_instance.item_id, item_instance.lendable)
        if linking_purpose is None:
            raise HTTPException(status_code=400, detail=f"Item {item_instance.item_id} is not in lendable {item_instance.lendable}")
        contract = CreateItemInstance(**item_instance_data, purpose=linking_purpose)
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
        return APIFullItem(
            id=db_item_instance.id,
            item_id=db_item_instance.item.id,
            name=db_item_instance.item.name,
            description=db_item_instance.item.description,
            manufacturer=db_item_instance.item.manufacturer,
            model=db_item_instance.item.model,
            report_profile_id=db_item_instance.item.report_profile_id,
            max_lifespan=db_item_instance.item.max_lifespan,
            max_usage_lifespan=db_item_instance.item.max_usage_lifespan,
            psa_category=db_item_instance.item.psa_category,
            external_id=db_item_instance.external_id,
            serial_number=db_item_instance.serial_number,
            manufacture_date=db_item_instance.manufacture_date,
            purchase_date=db_item_instance.purchase_date,
            first_use_date=db_item_instance.first_use_date,
            condition=db_item_instance.condition,
            condition_comment=db_item_instance.condition_comment,
            lendable_id=db_item_instance.purpose.lendable_purpose_link.lendable_id if db_item_instance.purpose else None,
            storage_location_id=db_item_instance.purpose.storage_location_id if db_item_instance.purpose else None,
            too_old=db_item_instance.is_too_old,
            requires_inspection=await db_item_instance.requires_inspection(),
        )
    except ItemNotFound:
        raise HTTPException(status_code=404, detail="ItemInstance not found")
    

@router.put("/{item_instance_id}")
async def update_item_instance(item_instance_id: UUID, item_instance: APIItemInstanceBase) -> APIItemInstance:
    try:
        db_item_instance = await ItemInstanceService.update(item_instance_id, UpdateItemInstanceData(**item_instance.model_dump()))
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

@router.get("/{item_instance_id}/inspection_report")
async def get_inspection_reports(item_instance_id: UUID):
    inspection_reports = await InspectionReportRepo.get_by_item_instance_id(item_instance_id)
    if not inspection_reports:
        raise HTTPException(status_code=404, detail="Inspection reports not found")
    return inspection_reports  # TODO: Create Pydantic model for InspectionReport and enforce type

