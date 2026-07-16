from uuid import UUID

from depot_server.db2.models.news import NewsEntry
from depot_server.db2.repository.base import BaseRepo, ItemNotFound


class NewsRepo(BaseRepo):
    Db_type = NewsEntry

    @classmethod
    async def get_all_announcements(cls) -> list[NewsEntry]:
        """Retrieve all announcements"""
        announcements = await cls.Db_type.all()
        return announcements

    @classmethod
    async def get_announcement_by_id(cls, announcement_id: UUID) -> NewsEntry | None:
        """Retrieve a single announcement by id"""
        announcement = await cls.get_by_id(announcement_id)
        return announcement

    @classmethod
    async def create_announcement(cls, **kwargs) -> NewsEntry:
        """Create a new announcement"""
        announcement = await cls.create(**kwargs)
        return announcement

    @classmethod
    async def update_announcement(cls, announcement_id: UUID, **kwargs) -> NewsEntry:
        """Update an existing announcement"""
        announcement = await cls.get_announcement_by_id(announcement_id)
        if not announcement:
            raise ItemNotFound(f"Announcement with id {announcement_id} not found")

        # Prevent updating the id field
        if "id" in kwargs:
            raise ValueError("Cannot update the id field")

        for key, value in kwargs.items():
            # ensure the attribute exists on the model instance
            if not hasattr(announcement, key):
                raise ValueError(f"Field name {key} is not valid for type {cls.Db_type}")
            setattr(announcement, key, value)
        # save the instance
        await announcement.save()
        return announcement

    @classmethod
    async def delete_announcement(cls, announcement_id: UUID) -> None:
        """Delete an announcement"""
        await cls.delete_by_id(announcement_id)
