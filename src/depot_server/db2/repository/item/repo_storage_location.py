from uuid import UUID

from depot_server.db2.models import StorageLocation
from depot_server.db2.repository.base import BaseRepo, ItemNotFound


class StorageLocationRepo(BaseRepo):
    Db_type = StorageLocation

    @classmethod
    async def get_all_storage_locations(cls) -> list[Db_type]:
        locations = await cls.Db_type.all()
        return locations

    @classmethod
    async def get_storage_location_by_id(cls, loc_id: UUID) -> Db_type | None:
        item = await cls.get_by_id(loc_id)
        return item

    @classmethod
    async def create_storage_location(cls, **kwargs) -> Db_type:
        location = await cls.create(**kwargs)
        return location

    @classmethod
    async def update_storage_location(cls, loc_id: UUID, **kwargs) -> Db_type:
        location = await cls.get_storage_location_by_id(loc_id)
        if not location:
            raise ItemNotFound(f"Storage location with id {loc_id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(location, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(location, key, value)
        # save the instance
        await location.save()
        return location

    @classmethod
    async def delete_storage_location(cls, loc_id: UUID) -> None:
        await cls.delete_by_id(loc_id)
