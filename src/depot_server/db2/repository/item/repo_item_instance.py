from uuid import UUID

from tortoise.expressions import Q

from depot_server.db2.models import ItemInstance
from depot_server.db2.repository.audit import AuditableRepo
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory

class ItemInstanceRepo(AuditableRepo):
    Db_type = ItemInstance

    @classmethod
    async def get_all_item_instances(cls) -> list[ItemInstance]:
        item_instances = await cls.Db_type.all()
        return item_instances

    @classmethod
    async def get_item_instance_by_id(cls, item_instance_id: UUID) -> ItemInstance | None:
        item_instance = await cls.Db_type.get_or_none(id=item_instance_id)
        return item_instance

    @classmethod
    async def get_item_instances_by_item_id(cls, item_id: UUID) -> list[ItemInstance]:
        item_instances = await cls.Db_type.filter(item_id=item_id)
        return item_instances

    @classmethod
    async def get_amount_by_item(cls, item_id: UUID) -> int:
        count = await cls.Db_type.filter(item_id=item_id, condition__in=[Condition.GOOD, Condition.MONITOR]).count()
        return count

    @classmethod
    async def get_amount_by_purpose(cls, purpose_id: UUID) -> int:
        count = await cls.Db_type.filter(purpose_id=purpose_id, condition__in=[Condition.GOOD, Condition.MONITOR]).count()
        return count

    @classmethod
    async def get_item_instances_needing_inspection(cls, psa_category: PsaCategory) -> list[ItemInstance]:
        raise NotImplementedError("This method is not yet implemented")
        item_instances = await cls.Db_type.filter(psa_category=psa_category).prefetch_related("reports").filter(reports__isnull=True).all()
        return item_instances

    @classmethod
    async def get_full_items(cls, **kwargs):
        item_instances = await cls.Db_type.filter(**kwargs).prefetch_related("item").all()
        return item_instances

    @classmethod
    async def get_full_item(cls, item_instance_id: UUID) -> ItemInstance | None:
        item_instances = await cls.get_full_items(id=item_instance_id)
        if not item_instances:
            raise ItemNotFound(f"Item instance with id {item_instance_id} not found")
        return item_instances[0]

    @classmethod
    async def delete_item_instance(cls, item_instance_id: UUID) -> None:
        await cls.delete_by_id(item_instance_id)

    @classmethod
    async def update_item_instance(cls, item_instance_id: UUID, **kwargs) -> ItemInstance:
        item_instance = await cls.get_item_instance_by_id(item_instance_id)
        if not item_instance:
            raise ItemNotFound(f"Item instance with id {item_instance_id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(item_instance, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(item_instance, key, value)
        # save the instance
        await item_instance.save()
        return item_instance

    @classmethod
    async def has_colliding_unique(cls, item_id: UUID, serial_number: str,
                                   external_id: str | None = None, exclude_id: UUID | None = None) -> bool:
        if external_id is None:
            query = Q(item_id=item_id) & Q(serial_number=serial_number)
        else:
            query = Q(item_id=item_id) & (Q(serial_number=serial_number) | Q(external_id=external_id))
        if exclude_id is not None:
            query = query & ~Q(id=exclude_id)
        existing_instance = await cls.Db_type.filter(query).first()
        return existing_instance is not None