from uuid import UUID

from depot_server.api2.models.item_composite import ItemCompositeBase, ItemComposite as ApiItemComposite
from depot_server.db2.models.item.item_composite import ItemComposite as DbItemComposite, ItemCompositeLink
from depot_server.db2.repository.item.repo_item_composite import ItemCompositeRepo, ItemCompositeLinkRepo
from depot_server.db2.repository.base import ItemNotFound
from tortoise.transactions import in_transaction


class ItemCompositeService:
    
    @staticmethod
    async def get_all() -> list[ApiItemComposite]:
        composites = await ItemCompositeRepo.get_all_with_links()
        return [ApiItemComposite(id=composite.id,
                                 name=composite.name,
                                 description=composite.description,
                                 lendable=composite.lendable,
                                 elements={link.item_group_id: link.amount
                                           for link in composite.item_composite_link})
                for composite in composites]

    @staticmethod
    async def get_by_id(item_composite_id) -> ApiItemComposite:
        composite = await ItemCompositeRepo.get_by_id(item_composite_id)
        if not composite:
            raise ItemNotFound(f"ItemComposite with id {item_composite_id} not found")
        elements = await ItemCompositeLinkRepo.get_all_by_composite_id(composite.id)
        return ApiItemComposite(id=composite.id,
                                name=composite.name,
                                description=composite.description,
                                lendable=composite.lendable,
                                elements={element.item_group_id: element.amount for element in elements})

    @staticmethod
    async def create(item_composite: ItemCompositeBase) -> ApiItemComposite:
        composite_db = await ItemCompositeRepo.create(name=item_composite.name, description=item_composite.description, lendable=item_composite.lendable)
        for group_id, amount in item_composite.elements.items():
            await ItemCompositeLinkRepo.create(item_composite=composite_db, item_group_id=group_id, amount=amount)
        return ApiItemComposite(id=composite_db.id,
                                name=composite_db.name,
                                description=composite_db.description,
                                lendable=composite_db.lendable,
                                elements=item_composite.elements)

    @staticmethod
    async def update(item_composite_id, item_composite: ItemCompositeBase) -> ApiItemComposite:
        await ItemCompositeRepo.update(item_composite_id,
                                       name=item_composite.name,
                                       description=item_composite.description,
                                       lendable=item_composite.lendable)
        current_links = await ItemCompositeLinkRepo.get_all_by_composite_id(item_composite_id)
        # Update / Delete existing links 
        ids = []
        for link in current_links:
            if link.id not in item_composite.elements:
                await ItemCompositeLinkRepo.delete_by_id(link.id)
            else:
                await ItemCompositeLinkRepo.update(link.id, amount=item_composite.elements[link.item_group_id])
                ids.append(link.item_group_id)
        # Add new links
        for group_id, amount in item_composite.elements.items():
            if group_id not in ids:
                await ItemCompositeLinkRepo.create(item_composite_id=item_composite_id, item_group_id=group_id, amount=amount)
        return await ItemCompositeService.get_by_id(item_composite_id)


    @staticmethod
    async def delete(item_composite_id):
        async with in_transaction():
            composite_links = await ItemCompositeLinkRepo.get_all_by_composite_id(item_composite_id)
            for link in composite_links:
                await ItemCompositeLinkRepo.delete_by_id(link.id)
            await ItemCompositeRepo.delete_by_id(item_composite_id)
        return

    @staticmethod
    async def get_total_amount(item_composite_id: UUID) -> int:
        #TODO Implement logic
        return 5