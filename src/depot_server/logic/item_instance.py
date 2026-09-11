from uuid import UUID

from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.models.item import ItemInstance as ItemInstanceDB
from depot_server.api2.models.item import ItemInstance, ItemInstanceBase, ItemInstancePending


class ItemInstanceUniqueConflict(ValueError):
    """Raised when an item instance violates its per-item unique values."""

class ItemInstanceService:
    @classmethod
    async def create_item_instance(cls, item_instance: ItemInstanceBase) -> ItemInstanceDB:
        if await ItemInstanceRepo.has_colliding_unique(item_instance.item_id, item_instance.serial_number, item_instance.external_id):
            raise ItemInstanceUniqueConflict(
                f"Can't create Item instance for Item {item_instance.item_id}. "
                "Serial number or external id already exists."
            )
        db_instance = await ItemInstanceRepo.create(**item_instance.model_dump())
        return db_instance

    @classmethod
    async def update_item_instance(cls, item_instance_id: UUID, item_instance: ItemInstancePending) -> ItemInstanceDB | None:
        if await ItemInstanceRepo.has_colliding_unique(item_instance.item_id, item_instance.serial_number, item_instance.external_id, exclude_id=item_instance_id):
            raise ItemInstanceUniqueConflict(
                f"Can't update Item instance {item_instance_id}. "
                "Serial number or external id already exists."
            )
        db_instance = await ItemInstanceRepo.update(item_instance_id, **item_instance.model_dump())
        return db_instance

