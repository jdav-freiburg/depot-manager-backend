from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Generic, Any
from uuid import UUID

from tortoise.models import Model

T = TypeVar("T", bound=Model)


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


class BaseRepo(RepoInterface[T]):
    Db_type: type[T]

    @classmethod
    async def create(cls, **kwargs) -> T:
        obj = cls.Db_type(**kwargs)
        await obj.save()
        return obj

    @classmethod
    async def get_by_id(cls, id: UUID) -> Optional[T]:
        return await cls.Db_type.get_or_none(pk=id)

    @classmethod
    async def save(cls, obj: T) -> T:
        await obj.save()
        return obj


class AuditableRepo(BaseRepo[T]):
    @classmethod
    async def create(cls, **kwargs) -> T:
        obj = cls.Db_type(**kwargs)
        await obj.save()
        return obj

    @classmethod
    def _calculate_diff(cls, old: T, new: T) -> tuple[dict[str, Any], dict[str, Any]]:
        # Determine changed fields
        old_changes: dict[str, Any] = {}
        new_changes: dict[str, Any] = {}

        field_names = cls.Db_type._meta.fields_map.keys()
        for name in field_names:
            # if the currently checked field is a FK or m2m field, only
            # check if the UUID has changed
            changed_foreign_relation: bool = False
            if name in old._meta.fk_fields:
                old_val = getattr(old, f"{name}_id")
                new_val = getattr(new, f"{name}_id")
                changed_foreign_relation = True
            else:
                old_val = getattr(old, name)
                new_val = getattr(new, name)

            if old_val != new_val:
                if changed_foreign_relation:
                    raise NotImplementedError("Can't diff relations yet")
                old_changes[name] = old_val
                new_changes[name] = new_val

        return old_changes, new_changes


