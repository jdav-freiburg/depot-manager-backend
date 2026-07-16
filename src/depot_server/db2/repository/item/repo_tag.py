from uuid import UUID

from depot_server.db2.models import Tag
from depot_server.db2.repository.base import BaseRepo, ItemNotFound


class TagRepo(BaseRepo):
    Db_type = Tag

    @classmethod
    async def get_all_tags(cls) -> list[Tag]:
        tags = await cls.Db_type.all()
        return tags

    @classmethod
    async def get_tag_by_id(cls, tag_id: UUID) -> Tag | None:
        item = await cls.get_by_id(tag_id)
        return item

    @classmethod
    async def create_tag(cls, **kwargs) -> Tag:
        tag = await cls.create(**kwargs)
        return tag

    @classmethod
    async def update_tag(cls, tag_id: UUID, **kwargs) -> Tag:
        tag = await cls.get_tag_by_id(tag_id)
        if not tag:
            raise ItemNotFound(f"Tag with id {tag_id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(tag, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(tag, key, value)
        # save the instance
        await tag.save()
        return tag

    @classmethod
    async def delete_tag(cls, tag_id: UUID) -> None:
        await cls.delete_by_id(tag_id)
