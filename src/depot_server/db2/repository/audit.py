import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from tortoise.fields import Field
from tortoise.transactions import in_transaction

from depot_server.db2.models import Item
from depot_server.db2.repository.base import BaseRepo, T as BASE_T
from depot_server.db2.repository.repo_auditlog import AuditLogRepo


@dataclass(frozen=True)
class AuditInfo:
    user_id: UUID
    comment: str


class AuditableRepo(BaseRepo[BASE_T]):
    _logger = logging.getLogger("audit")

    @classmethod
    async def create(cls, **kwargs) -> BASE_T:
        obj = cls.Db_type(**kwargs)
        await obj.save()
        return obj

    @classmethod
    async def model_diff(cls, old_obj, new_obj) -> tuple[dict[str, Any], dict[str, Any]]:
        # Determine changed fields
        partial_old: dict[str, Any] = {}  # holds partial object before the change (original values)
        partial_new: dict[str, Any] = {}  # holds partial object after the change (new values)

        fields: dict = old_obj.describe()

        for data_field_name in map(lambda field: field.get("name"), fields.get('data_fields')):

            old_value: Field = getattr(old_obj, data_field_name, None)
            new_value: Field = getattr(new_obj, data_field_name, None)

            if old_value != new_value:
                partial_old[data_field_name] = old_value
                partial_new[data_field_name] = new_value

        return partial_old, partial_new

    @classmethod
    async def save(cls, obj: BASE_T, info: AuditInfo) -> BASE_T:
        old: Item = await obj.get(pk=obj.pk)
        diff_old, diff_new = await cls.model_diff(old, obj)
        if diff_old == {} and diff_new == {}:
            # we have nothing to do here, as the objects are identical
            return obj
        cls._logger.info("Changing %s object %s. Old: %s | New: %s", obj.__class__.__name__, obj.pk, old, diff_old)

        async with in_transaction():  # If something fails we still have consistent data
            t = str(type(obj))
            await AuditLogRepo.create(
                type_=t,
                type_id=obj.pk,
                user_id=info.user_id,
                comment=info.comment,
                old=diff_old,
                new=diff_new,
            )
            await obj.save()

        return obj
