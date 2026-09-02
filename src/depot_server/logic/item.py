

from uuid import UUID

from depot_server.db2.models.item.item import Item

from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.api2.models.item import FullItem, FullItemRaw, Item, ItemPending


class ItemService:
    @staticmethod
    async def get_all_items() -> list[Item]:
        db_items = await ItemRepo.get_all_items()
        return [Item.model_validate({
            "id": item.id,
            "group_id": item.group_id,
            "lendable": item.group.lendable,
            "name": item.name,
            "description": item.description,
            "manufacturer": item.manufacturer,
            "model": item.model,
            "report_profile_id": item.report_profile_id,
            "max_lifespan": item.max_lifespan,
            "max_usage_lifespan": item.max_usage_lifespan,
            "psa_category": item.psa_category,
            "storage_location_id": item.storage_location_id,
        }) for item in db_items]

    @staticmethod
    async def get_item(item_id: UUID) -> Item|None:
        db_item = await ItemRepo.get_item_by_id(item_id)
        if not db_item:
            return None
        return Item.model_validate({
            "id": db_item.id,
            "group_id": db_item.group_id,
            "lendable": db_item.group.lendable,
            "name": db_item.name,
            "description": db_item.description,
            "manufacturer": db_item.manufacturer,
            "model": db_item.model,
            "report_profile_id": db_item.report_profile_id,
            "max_lifespan": db_item.max_lifespan,
            "max_usage_lifespan": db_item.max_usage_lifespan,
            "psa_category": db_item.psa_category,
            "storage_location_id": db_item.storage_location_id,
        }, from_attributes=True)

    @staticmethod
    async def create_item(item: FullItemRaw) -> FullItem:
        db_group = await ItemGroupRepo.create(name=item.name,
                                              description=item.description,
                                              lendable=item.lendable)
        db_item = await ItemRepo.create_item(group_id=db_group.id,
                                             name=item.name,
                                             description=item.description,
                                             manufacturer=item.manufacturer,
                                             model=item.model,
                                             report_profile_id=item.report_profile_id,
                                             max_lifespan=item.max_lifespan,
                                             max_usage_lifespan=item.max_usage_lifespan,
                                             psa_category=item.psa_category)
        db_instance = await ItemInstanceRepo.create_item_instance(item_id=db_item.id,
                                                 external_id=item.external_id,
                                                 serial_number=item.serial_number,
                                                 manufacture_date=item.manufacture_date,
                                                 purchase_date=item.purchase_date,
                                                 first_use_date=item.first_use_date,
                                                 condition=item.condition,
                                                 condition_comment=item.condition_comment)
        

        return FullItem.model_validate({
            "group_id": db_group.id,
            "lendable": db_group.lendable,
            "id": db_item.id,
            "name": db_item.name,
            "description": db_item.description,
            "manufacturer": db_item.manufacturer,
            "model": db_item.model,
            "report_profile_id": db_item.report_profile_id,
            "max_lifespan": db_item.max_lifespan,
            "max_usage_lifespan": db_item.max_usage_lifespan,
            "psa_category": db_item.psa_category,
            "instance_id": db_instance.id,
            "external_id": db_instance.external_id,
            "serial_number": db_instance.serial_number,
            "manufacture_date": db_instance.manufacture_date,
            "purchase_date": db_instance.purchase_date,
            "first_use_date": db_instance.first_use_date,
            "condition": db_instance.condition,
            "condition_comment": db_instance.condition_comment,
            })

    @staticmethod
    async def update_item(item_id: UUID, item: ItemPending) -> Item|None:
        db_item = await ItemRepo.update_item(item_id=item_id,
                                             group_id=item.group_id,
                                             name=item.name,
                                             description=item.description,
                                             manufacturer=item.manufacturer,
                                             model=item.model,
                                             report_profile_id=item.report_profile_id,
                                             max_lifespan=item.max_lifespan,
                                             max_usage_lifespan=item.max_usage_lifespan,
                                             psa_category=item.psa_category,
                                             storage_location_id=item.storage_location_id)
        if not db_item:
            return None
        db_group = await ItemGroupRepo.update_item_group(item_group_id=db_item.group_id,
                                                         name=item.name,
                                                         description=item.description,
                                                         lendable=item.lendable)
        return Item.model_validate({"id": db_item.id,
                                   "group_id": db_item.group_id,
                                   "lendable": db_group.lendable,
                                   "name": db_item.name,
                                   "description": db_item.description,
                                   "manufacturer": db_item.manufacturer,
                                   "model": db_item.model,
                                   "report_profile_id": db_item.report_profile_id,
                                   "max_lifespan": db_item.max_lifespan,
                                   "max_usage_lifespan": db_item.max_usage_lifespan,
                                   "psa_category": db_item.psa_category,
                                   "storage_location_id": db_item.storage_location_id})