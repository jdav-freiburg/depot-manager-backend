from datetime import datetime
from uuid import UUID

from depot_server.api2.models.item_group import ItemGroup, ItemGroupAmount, ItemGroupBase
from depot_server.db2.models.item.item_group import ItemGroup as DbItemGroup
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_item import ItemRepo


def item_group_from_orm(item_group: DbItemGroup) -> ItemGroup:
    return ItemGroup(
        id=item_group.id,
        name=item_group.name,
        description=item_group.description,
        lendable=item_group.lendable,
        parent=item_group.parent_id
    )

class ItemGroupService:
    @staticmethod
    async def update_item_group(item_group_id: UUID, item_group: ItemGroupBase) -> DbItemGroup | None:
        db_item_group = await ItemGroupRepo.update_item_group(item_group_id, **item_group.model_dump())
        await ItemRepo.update_by_item_group(
            item_group_id,
            name=item_group.name,
            description=item_group.description,
        )
        return db_item_group


    @staticmethod
    async def get_total_amount(item_group_id: UUID, only_lendable=True) -> int:
        # TODO implement actual logic based on reservations and item instances
        return 5