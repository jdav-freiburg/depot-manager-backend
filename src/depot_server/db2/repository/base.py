
from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Generic
from uuid import UUID

from tortoise.models import Model

T = TypeVar("T", bound=Model)


class ItemNotFound(Exception):
    pass

class RepoInterface(Generic[T], ABC):
    """
    Interface for the database repository functions.
    Implement this interface for creating or fetching objects from the underlying DB.
    """

    @classmethod
    @abstractmethod
    async def create(cls, **kwargs) -> T:
        """
        Create one object using the given parameters and store it in the DB,
        the object is returned on success.
        :param kwargs: arguments passed to the constructor
        :return: The created object
        """
        ...

    @classmethod
    @abstractmethod
    async def get_by_id(cls, id: UUID) -> Optional[T]:
        """
        Fetches the object with the given id from the DB.
        returns None if the object does not exist.
        :param id: The UUID of the object
        :return: the requested object, None if the object does not exist.
        """
        ...

    @classmethod
    @abstractmethod
    async def save(cls, obj: T) -> T:
        """
        Saves the given object to the database.
        :param obj: The object to save
        :return: The saved object
        """
        ...

    @classmethod
    @abstractmethod
    async def delete_by_id(cls, id: UUID) -> None:
        ...

class BaseRepo(RepoInterface[T]):
    Db_type: type[T]

    @classmethod
    async def create(cls, **kwargs) -> T:
        obj = cls.Db_type(**kwargs)
        await obj.save()
        return obj

    @classmethod
    async def get_all(cls) -> list[T]:
        return await cls.Db_type.all()

    @classmethod
    async def get_by_id(cls, id: UUID) -> Optional[T]:
        return await cls.Db_type.get_or_none(pk=id)

    @classmethod
    async def get_by_ids(cls, ids: list[UUID]) -> list[T]:
        return await cls.Db_type.filter(pk__in=ids).all()

    @classmethod
    async def save(cls, obj: T) -> T:
        await obj.save()
        return obj

    @classmethod
    async def update(cls, id: UUID, **kwargs) -> Optional[T]:
        obj = await cls.get_by_id(id)
        if not obj:
            raise ItemNotFound(f"Item {id} not found")
        for key, value in kwargs.items():
            if key == obj._meta.pk_attr:
                raise ValueError("Cannot update primary key")
            setattr(obj, key, value)
        await obj.save()
        return obj

    @classmethod
    async def delete_by_id(cls, id: UUID) -> None:
        item = await cls.get_by_id(id)
        if not item:
            raise ItemNotFound(f"Item {id} not found")
        await item.delete()
