from uuid import UUID

from depot_server.db2.models import ItemGroup
from depot_server.db2.repository.base import BaseRepo, ItemNotFound, T


class ItemGroupRepo(BaseRepo):
    Db_type = ItemGroup

    @classmethod
    async def create(cls, **kwargs) -> T:
        if "parent" in kwargs and kwargs["parent"] is not None:
            parent = await ItemGroupRepo.get_by_id(kwargs["parent"])
            if parent is None:
                raise ItemNotFound(f"Parent item with id {kwargs['parent']} not found")
            kwargs['parent'] = parent
        return await super().create(**kwargs)

    @classmethod
    async def update_item_group(cls, item_group_id: UUID, **kwargs) -> ItemGroup:
        group = await cls.get_by_id(item_group_id)
        if not group:
            raise ItemNotFound(f"ItemGroup with id {item_group_id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(group, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(group, key, value)
        # save the instance
        await group.save()
        return group

    @classmethod
    async def get_children_by_parent_id(cls, parent_id: UUID) -> list[ItemGroup]:
        children = await cls.Db_type.filter(parent_id=parent_id)
        return children