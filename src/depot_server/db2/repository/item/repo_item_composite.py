from depot_server.db2.models.item.item_composite import ItemComposite, ItemCompositeLink
from depot_server.db2.repository.base import BaseRepo


class ItemCompositeRepo(BaseRepo):
    Db_type = ItemComposite

    @classmethod
    async def get_all_with_links(cls):
        return await cls.Db_type.all().prefetch_related("item_composite_link")

class ItemCompositeLinkRepo(BaseRepo):
    Db_type = ItemCompositeLink

    @classmethod
    async def get_all_by_composite_id(cls, composite_id) -> list[ItemCompositeLink]:
        return await cls.Db_type.filter(item_composite_id=composite_id).all()

