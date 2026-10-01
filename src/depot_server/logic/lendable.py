from uuid import UUID

from depot_server.db2.models.item.lendable import Lendable
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_lendable import LendableRepo, LinkLenablePurposeRepo
from depot_server.db2.repository.item.repo_lendable_group import LendableGroupRepo
from depot_server.db2.repository.base import ItemNotFound
from depot_server.logic.contracts.lendable import CreateLendable, CreateLendableGroup, UpdateLendable
from depot_server.logic.results.lendable import LogicLendable, LogicLendableLink
from tortoise.transactions import in_transaction




class LendableService:

    @classmethod
    def _to_dataclass_lendable(cls, lendable: Lendable) -> LogicLendable:
        return LogicLendable(id=lendable.id,
                            name=lendable.name,
                            description=lendable.description,
                            purposes=[LogicLendableLink(id=link.id,
                                                        lendable_id=link.lendable_id,
                                                        amount=link.amount,
                                                        purpose_id=link.purpose_id,
                                                        created_at=link.created_at) for link in lendable.lendable_purpose_link],
                            in_limbus=lendable.in_limbus,
                            ausgabepflichtig=lendable.ausgabepflichtig,
                            parent=lendable.lendable_group.parent_id if lendable.lendable_group else None,
                            storage_location=lendable.storage_location,
                            changed_at=lendable.changed_at)
    
    @classmethod
    async def get_all(cls) -> list[LogicLendable]:
        lendables = await LendableRepo.get_all_current_with_links()
        return [cls._to_dataclass_lendable(lendable)
                for lendable in lendables]

    @classmethod
    async def get_by_id(cls, item_composite_id) -> LogicLendable:
        lendable = await LendableRepo.get_by_id(item_composite_id)
        if not lendable:
            raise ItemNotFound(f"Lendable with id {item_composite_id} not found")
        elements = await LinkLenablePurposeRepo.get_all_by_lendable_id(lendable.id)
        return cls._to_dataclass_lendable(lendable)

    @classmethod
    async def create(cls, command: CreateLendable) -> LogicLendable:
        async with in_transaction():
            group = await LendableGroupRepo.create(**command.to_kwargs("name", "description", "parent"))
            lendable = await LendableRepo.create(**command.to_kwargs("name", "description", "ausgabepflichtig", "storage_location"), lendable_group=group)
            purpose_links = []
            for purpose_id, amount in command.purposes.items():
                purpose_links.append(await LinkLenablePurposeRepo.create(lendable=lendable, purpose_id=purpose_id, amount=amount))

        return cls._to_dataclass_lendable(await LendableRepo.get_by_id_with_links(lendable.id))

    @classmethod
    async def update(cls, lendable_id, command: UpdateLendable) -> LogicLendable:
        async with in_transaction():
            prev_lendable = await LendableRepo.get_by_id_with_links(lendable_id)
            group = await LendableGroupRepo.update(id=prev_lendable.lendable_group_id,
                                                    **command.to_kwargs("name", "description", "parent"))
            await LendableRepo.update(lendable_id,
                                      **command.to_kwargs("name", "description", "ausgabepflichtig", "storage_location", "in_limbus"))
            if "purposes" in command.to_kwargs("purposes"):
                prev_links = await LinkLenablePurposeRepo.get_all_by_lendable_id(lendable_id)
                # Update / Delete existing links
                ids = []
                for link in prev_links:
                    if link.purpose_id not in command.purposes:
                        await LinkLenablePurposeRepo.delete_by_id(link.id)
                    else:
                        command.to_kwargs
                        await LinkLenablePurposeRepo.update(link.id, amount=command.purposes[link.purpose_id])
                        ids.append(link.purpose_id)
                # Add new links
                for purpose_id, amount in command.purposes.items():
                    if purpose_id not in ids:
                        await LinkLenablePurposeRepo.create(lendable_id=lendable_id, purpose_id=purpose_id, amount=amount)
        return await cls.get_by_id(lendable_id)


    @staticmethod
    async def delete(lendable_id):
        async with in_transaction():
            composite_links = await LinkLenablePurposeRepo.get_all_by_lendable_id(lendable_id)
            for link in composite_links:
                await LinkLenablePurposeRepo.delete_by_id(link.id)
            await LendableRepo.delete_by_id(lendable_id)
        return

    @staticmethod
    async def get_total_amount(id: UUID) -> int:
        lendable = await LendableRepo.get_by_id_with_links(id)
        available_sets = []
        for link in lendable.lendable_purpose_link:
            required_amount = link.amount
            in_service_amount = await ItemInstanceRepo.get_amount_by_purpose(link.purpose_id)
            available_sets.append(in_service_amount // required_amount)
        return min(available_sets) if available_sets else 0