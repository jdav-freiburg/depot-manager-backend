
from uuid import UUID

from depot_server.db2.repository.audit import AuditableRepo
from depot_server.db2.models.item.item_purpose import ItemPurpose

class ItemPurposeRepo(AuditableRepo):
    Db_type = ItemPurpose

    @classmethod
    async def get_lendables_by_item(cls, item_id: UUID) -> list[UUID]:
        purposes = await cls.Db_type.filter(item_id=item_id).prefetch_related("lendable_purpose_link").all()
        return [link.lendable_id for purpose in purposes for link in purpose.lendable_purpose_link]
        
    @classmethod
    async def get_linking_purpose(cls, item_id: UUID, lendable_id: UUID | None) -> UUID | None:
        if lendable_id is None:
            return None
        purpose = await cls.Db_type.filter(item_id=item_id, lendable_purpose_link__lendable_id=lendable_id).first()
        if purpose:
            return purpose.id
        return None