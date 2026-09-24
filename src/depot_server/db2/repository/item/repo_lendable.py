from datetime import datetime

from tortoise.query_utils import Prefetch
from tortoise.transactions import in_transaction

from depot_server.db2.models.item.lendable import Lendable, LinkLendablePurpose
from depot_server.db2.repository.base import BaseRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo


class LendableRepo(BaseRepo):
    Db_type = Lendable

    @classmethod
    async def get_all_current_with_links(cls):
        return await cls.Db_type.all().prefetch_related("depot_link_lendable__purpose")

    @classmethod
    async def get_by_id_with_links(cls, id, timestamp: datetime | None = None) -> Lendable | None:
        """
        Gets the lenable together with its purpose links. Since the composition of a lendable can change over time,
        the timestamp is used to determine if the links should come from the current table or the archive table.
        If the timestamp is before the last change date, the links are fetched from the archive table.
        datetime None means only the current state is relevant, so the links are fetched from the current table.
        """
        change_date = (await cls.Db_type.filter(id=id).first()).changed_at
        if not change_date:
            return None
        if timestamp is None or change_date < timestamp:
            return await cls.Db_type.get_or_none(id=id).prefetch_related("lendable_purpose_link")
        return await cls.Db_type.filter(id=id).prefetch_related(
            Prefetch("lendable_purpose_link_archive",
                     queryset=LinkLendablePurpose.filter(created_at__lt=timestamp, change_date__gt=timestamp))
                ).first()



class LinkLenablePurposeRepo(BaseRepo):
    Db_type = LinkLendablePurpose

    @classmethod
    async def get_all_by_composite_id(cls, composite_id) -> list[LinkLendablePurpose]:
        return await cls.Db_type.filter(item_composite_id=composite_id).all()

    @classmethod
    async def update(cls, id, **kwargs):
        if "created_at" in kwargs:
            raise PermissionError("Cannot update created_at or change_date fields.")
        async with in_transaction():
            archive_entry = await LinkLenablePurposeArchiveRepo.create(**(await cls.get_by_id(id)).__dict__)
            updated_entry = await super().update(id, created_at=archive_entry.created_at, **kwargs)
            await LendableRepo.update(id=archive_entry.lendable_id, changed_at=archive_entry.change_date)
            if archive_entry.lendable_id != updated_entry.lendable_id:
                await LendableRepo.update(id=updated_entry.lendable_id, changed_at=archive_entry.change_date)


    @classmethod
    async def delete_by_id(cls, id) -> None:
        async with in_transaction():
            archive_entry = await LinkLenablePurposeArchiveRepo.create(**(await cls.get_by_id(id)).__dict__)
            await LendableRepo.update(id=archive_entry.lendable_id, changed_at=archive_entry.change_date)
            await cls.Db_type.filter(id=id).delete()


    @classmethod
    async def bulk_delete(cls, ids: list) -> None:
        # TODO make this more efficient
        async with in_transaction():
            for id in ids:
                await cls.delete_by_id(id)


class LinkLenablePurposeArchiveRepo(BaseRepo):
    Db_type = LinkLendablePurpose

    @classmethod
    async def update(cls, id, **kwargs):
        raise PermissionError("Entries form the archive are not allowed to be changed.")

    @classmethod
    async def delete_by_id(cls, id) -> None:
        raise PermissionError("Entries form the archive are not allowed to be deleted.")

    @classmethod
    async def bulk_delete(cls, ids: list) -> None:
        raise PermissionError("Entries form the archive are not allowed to be deleted.")

