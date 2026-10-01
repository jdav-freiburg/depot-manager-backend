from datetime import datetime
from uuid import UUID

from depot_server.db2.repository.item.repo_lendable_group import LendableGroupRepo
from depot_server.db2.models import LendableGroup as DBLendableGroup
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.logic.contracts.lendable import UpdateLendableGroupData
from depot_server.logic.results.lendable import LogicLendableGroup


class LendableGroupService:
    @classmethod
    def _to_logic_dataclass(cls, db_item_group: DBLendableGroup) -> LogicLendableGroup:
        return LogicLendableGroup(
            id=db_item_group.id,
            name=db_item_group.name,
            description=db_item_group.description,
            parent=db_item_group.parent
        )

    @classmethod
    async def update_lendable_group(cls, id: UUID, contract: UpdateLendableGroupData) -> LogicLendableGroup:
        db_item_group = await LendableGroupRepo.update(id, **contract.to_kwargs("name", "description", "parent"))
        return cls._to_logic_dataclass(db_item_group)

    @classmethod
    async def get_total_amount(cls, item_group_id: UUID) -> int:
        count = await LendableGroupRepo.Db_type.filter(id=item_group_id).select_related("item").select_related("item_instances").count()
        return count