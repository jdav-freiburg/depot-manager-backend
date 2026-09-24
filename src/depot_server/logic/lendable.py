from uuid import UUID

from depot_server.api2.models.item_composite import ItemCompositeBase, ItemComposite as ApiItemComposite
from depot_server.db2.models.item.lendable import Lendable as DbItemComposite, LinkLendablePurpose
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_lendable import LendableRepo, LinkLenablePurposeRepo
from depot_server.db2.repository.base import ItemNotFound
from tortoise.transactions import in_transaction


class LendableService:
    
    @staticmethod
    async def get_all() -> list[ApiItemComposite]:
        composites = await LendableRepo.get_all_current_with_links()
        return [ApiItemComposite(id=composite.id,
                                 name=composite.name,
                                 description=composite.description,
                                 lendable=composite.lendable,
                                 elements={link.item_id: link.amount
                                           for link in composite.item_composite_link})
                for composite in composites]

    @staticmethod
    async def get_by_id(item_composite_id) -> ApiItemComposite:
        composite = await LendableRepo.get_by_id(item_composite_id)
        if not composite:
            raise ItemNotFound(f"ItemComposite with id {item_composite_id} not found")
        elements = await LinkLenablePurposeRepo.get_all_by_composite_id(composite.id)
        return ApiItemComposite(id=composite.id,
                                name=composite.name,
                                description=composite.description,
                                lendable=composite.lendable,
                                elements={element.item_id: element.amount for element in elements})

    @staticmethod
    async def create(item_composite: ItemCompositeBase) -> ApiItemComposite:
        composite_db = await LendableRepo.create(name=item_composite.name, description=item_composite.description, lendable=item_composite.lendable)
        for item_id, amount in item_composite.elements.items():
            await LinkLenablePurposeRepo.create(item_composite=composite_db, item_id=item_id, amount=amount)
        return ApiItemComposite(id=composite_db.id,
                                name=composite_db.name,
                                description=composite_db.description,
                                lendable=composite_db.lendable,
                                elements=item_composite.elements)

    @classmethod
    async def update(cls,item_composite_id, item_composite: ItemCompositeBase) -> ApiItemComposite:
        async with in_transaction():
            await LendableRepo.update(item_composite_id,
                                        name=item_composite.name,
                                        description=item_composite.description,
                                        lendable=item_composite.lendable)
            current_links = await LinkLenablePurposeRepo.get_all_by_composite_id(item_composite_id)
            # Update / Delete existing links 
            ids = []
            for link in current_links:
                if link.item_id not in item_composite.elements:
                    await LinkLenablePurposeRepo.delete_by_id(link.id)
                else:
                    await LinkLenablePurposeRepo.update(link.id, amount=item_composite.elements[link.item_id])
                    ids.append(link.item_id)
            # Add new links
            for item_id, amount in item_composite.elements.items():
                if item_id not in ids:
                    await LinkLenablePurposeRepo.create(item_composite_id=item_composite_id, item_id=item_id, amount=amount)
        return await cls.get_by_id(item_composite_id)


    @staticmethod
    async def delete(item_composite_id):
        async with in_transaction():
            composite_links = await LinkLenablePurposeRepo.get_all_by_composite_id(item_composite_id)
            for link in composite_links:
                await LinkLenablePurposeRepo.delete_by_id(link.id)
            await LendableRepo.delete_by_id(item_composite_id)
        return

    @staticmethod
    async def get_total_amount(id) -> int:
        lendable = await LendableRepo.get_by_id_with_links(id)
        available_sets = []
        for link in lendable.lendable_purpose_link:
            required_amount = link.amount
            in_service_amount = await ItemInstanceRepo.get_amount_by_purpose(link.purpose_id)
            available_sets.append(in_service_amount // required_amount)
        return min(available_sets) if available_sets else 0