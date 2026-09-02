from uuid import UUID
from depot_server.db2.models import Item
from depot_server.db2.repository.audit import AuditableRepo
from depot_server.db2.repository.base import ItemNotFound


class ItemRepo(AuditableRepo):
    Db_type = Item

    @classmethod
    async def get_all_items(cls) -> list[Item]:
        items = await cls.Db_type.all()
        return items

    @classmethod
    async def get_item_by_id(cls, item_id: UUID) -> Item | None:
        item = await cls.Db_type.get_or_none(id=item_id)
        return item

    @classmethod
    async def create_item(cls, **kwargs) -> Item:
        item = await cls.create(**kwargs)
        return item

    @classmethod
    async def delete_item(cls, item_id: UUID) -> None:
        await cls.delete_by_id(item_id)

    @classmethod
    async def update_item(cls, item_id: UUID, **kwargs) -> Item:
        item = await cls.get_item_by_id(item_id)
        if not item:
            raise ItemNotFound(f"Item with id {item_id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(item, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(item, key, value)
        # save the instance
        await item.save()
        return item