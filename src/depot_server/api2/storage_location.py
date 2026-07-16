from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.item.repo_storage_location import StorageLocationRepo, \
	StorageLocation as DbStorageLocation
from .models.storage_location import StorageLocation, StorageLocationPending

router = APIRouter()


def storage_location_from_orm(entry: DbStorageLocation) -> StorageLocation:
    """Convert a storage location ORM object to API model."""
    return StorageLocation(
        id=entry.pk,
        name=entry.name,
        description=entry.description,
        map_item=getattr(entry, "map_asset_id", None),
        is_subject_to_issuance=getattr(entry, "is_ausgabepflichtig", False),
    )


@router.get("/storage_location")
async def get_storage_locations() -> list[StorageLocation]:
    db_locations = await StorageLocationRepo.Db_type.all()
    return [storage_location_from_orm(loc) for loc in db_locations]


@router.get("/storage_location/{location_id}")
async def get_storage_location(location_id: UUID) -> StorageLocation:
    db_loc = await StorageLocationRepo.get_by_id(location_id)
    if not db_loc:
        raise HTTPException(status_code=404, detail="Storage location not found")
    return storage_location_from_orm(db_loc)


@router.post("/storage_location")
async def create_storage_location(loc: StorageLocationPending) -> StorageLocation:
    db_loc = await StorageLocationRepo.create(**loc.model_dump())
    return storage_location_from_orm(db_loc)


@router.put("/storage_location/{location_id}")
async def update_storage_location(location_id: UUID, payload: StorageLocationPending) -> StorageLocation:
    # fetch
    db_loc = await StorageLocationRepo.get_by_id(location_id)
    if not db_loc:
        raise HTTPException(status_code=404, detail="Storage location not found")

    # apply updates
    if payload.name is not None:
        db_loc.name = payload.name
    db_loc.description = payload.description
    # map_item may be None
    db_loc.map_asset_id = payload.map_item
    db_loc.is_ausgabepflichtig = payload.is_subject_to_issuance

    await StorageLocationRepo.save(db_loc)
    return storage_location_from_orm(db_loc)


@router.delete("/storage_location/{location_id}")
async def delete_storage_location(location_id: UUID) -> None:
    await StorageLocationRepo.delete_by_id(location_id)
