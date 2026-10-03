from uuid import UUID

from depot_server.db2.models import LendableGroup
from depot_server.db2.repository.base import BaseRepo, ItemNotFound, T


class LendableGroupRepo(BaseRepo):
    Db_type = LendableGroup

    @classmethod
    async def create(cls, **kwargs) -> T:
        if "parent" in kwargs and kwargs["parent"] is not None:
            parent = await LendableGroup.get_or_none(pk=kwargs["parent"])
            if parent is None:
                raise ItemNotFound(f"Parent item with id {kwargs['parent']} not found")
            if await cls.is_single_lendable_group(parent.id):
                raise ValueError("Cannot create a child group under a single lendable group")
            kwargs['parent'] = parent
        return await super().create(**kwargs)

    @classmethod
    async def update(cls, id: UUID, **kwargs) -> LendableGroup:
        group = await cls.get_by_id(id)
        if not group:
            raise ItemNotFound(f"ItemGroup with id {id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        if "parent" in kwargs and kwargs["parent"] is not None:
            parent = await LendableGroup.get_or_none(pk=kwargs["parent"])
            if parent is None:
                raise ItemNotFound(f"Parent item with id {kwargs['parent']} not found")
            if await cls.is_single_lendable_group(parent.id):
                raise ValueError("Cannot create a child group under a single lendable group")
            kwargs['parent'] = parent

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(group, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(group, key, value)
        # save the instance
        await group.save()
        return group

    @classmethod
    async def get_children_by_parent_id(cls, parent_id: UUID) -> list[LendableGroup]:
        children = await cls.Db_type.filter(parent_id=parent_id)
        return children

    @classmethod
    async def is_single_lendable_group(cls, lendable_group_id: UUID) -> bool:
        """
        Check if the given lendable group is the group representing a single lendable type.
        """
        lendable_group = await cls.get_by_id(lendable_group_id)
        if not lendable_group:
            raise ItemNotFound(f"LendableGroup with id {lendable_group_id} not found")
        if await lendable_group.children.all():
            return False
        return await lendable_group.lendable.all().count() == 1