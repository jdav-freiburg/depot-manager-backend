from uuid import UUID
from depot_server.db2.models import ItemInstance
from depot_server.db2.repository.audit import AuditableRepo
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.models.common import Condition

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
    async def create_item_instance(cls, **kwargs) -> ItemInstance:
        item_instance = await cls.create(**kwargs)
        return item_instance

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
    async def get_item_instances_by_item_id(cls, item_id: UUID) -> list[ItemInstance]:
        item_instances = await cls.Db_type.filter(item_id=item_id)
        return item_instances

    @classmethod
    async def get_instance_amount(cls, item_group_id: UUID) -> int:
        count = await cls.Db_type.filter(item__group_id=item_group_id, condition__in=[Condition.GOOD, Condition.MONITOR]).count()
        return count