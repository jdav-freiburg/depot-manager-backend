from uuid import UUID

from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_lendable import LinkLendablePurposeRepo
from depot_server.db2.models.item import ItemInstance as ItemInstanceDB
from depot_server.logic.contracts.item import CreateItemInstance, UpdateItemInstanceData


class ItemInstanceUniqueConflict(ValueError):
    """Raised when an item instance violates its per-item unique values."""

class ItemInstanceService:
    @classmethod
    async def create(cls, contract: CreateItemInstance) -> ItemInstanceDB:
        if await ItemInstanceRepo.has_colliding_unique(contract.item_id, contract.serial_number, contract.external_id):
            raise ItemInstanceUniqueConflict(
                f"Can't create Item instance for Item {contract.item_id}. "
                "Serial number or external id already exists."
            )
        db_instance = await ItemInstanceRepo.create(**contract.all_to_kwargs())
        return db_instance

    @classmethod
    async def update(cls, id: UUID, contract: UpdateItemInstanceData) -> ItemInstanceDB | None:
        current_instance = await ItemInstanceRepo.get_by_id(id)
        if not current_instance:
            raise ItemNotFound(f"Item instance with id {id} not found")
        item_id = contract.to_kwargs("item_id").get("item_id", current_instance.item_id)
        serial_number = contract.to_kwargs("serial_number").get("serial_number", current_instance.serial_number)
        external_id = contract.to_kwargs("external_id").get("external_id", current_instance.external_id)
        
        if await ItemInstanceRepo.has_colliding_unique(item_id, serial_number, external_id, exclude_id=id):
            raise ItemInstanceUniqueConflict(
                f"Can't update Item instance {id}. "
                "Serial number or external id already exists."
            )
        db_instance = await ItemInstanceRepo.update(id, **contract.all_to_kwargs())
        return db_instance

    @classmethod
    async def get_full_item(cls, item_instance_id: UUID) -> ItemInstanceDB | None:
        return await ItemInstanceRepo.get_full_item(item_instance_id)

    @classmethod
    async def get_expired_item_instances(cls) -> list[ItemInstanceDB]:
        expired_item_instances = await ItemInstanceRepo.get_all()
        return [inst for inst in expired_item_instances if inst.is_too_old]


    @classmethod
    async def is_in_lendable(cls, item_id: UUID, lendable_id: UUID) -> bool:
        """Check if the item belongs to the given lendable."""
        purposes = await ItemInstanceRepo.get_purposes_by_item_id(item_id)
        return await LinkLendablePurposeRepo.has_purpose(lendable_id, list(purposes.keys()))

    @classmethod
    async def get_linking_purpose(cls, item_id: UUID, lendable_id: UUID) -> UUID | None:
        """Get the purpose that links the item to the lendable."""
        purposes = await ItemInstanceRepo.get_purposes_by_item_id(item_id)
        for purpose_id in purposes.keys():
            if await LinkLendablePurposeRepo.has_purpose(lendable_id, [purpose_id]):
                return purpose_id
        return None