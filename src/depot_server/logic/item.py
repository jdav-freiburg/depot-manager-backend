

from uuid import UUID

from depot_server.db2.models.item.item import Item
from depot_server.db2.models.item.item_instance import ItemInstance

from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.logic.contracts.item import CreateItem, CreateItemInstance, UpdateItemData, UpdateItemInstanceData
from depot_server.logic.results.item import LogicItem, LogicItemInstance

class ItemService:
    @classmethod
    def _to_logic_item(cls, db_item: Item) -> LogicItem:
        return LogicItem(
            id=db_item.id,
            name=db_item.name,
            description=db_item.description,
            manufacturer=db_item.manufacturer,
            model=db_item.model,
            report_profile_id=db_item.report_profile_id,
            max_lifespan=db_item.max_lifespan,
            max_usage_lifespan=db_item.max_usage_lifespan,
            psa_category=db_item.psa_category
        )

    @classmethod
    def _to_logic__item_instance(cls, db_instance: ItemInstance) -> LogicItemInstance:
       return LogicItemInstance(
            id=db_instance.id,
            item_id=db_instance.item_id,
            external_id=db_instance.external_id,
            serial_number=db_instance.serial_number,
            manufacture_date=db_instance.manufacture_date,
            purchase_date=db_instance.purchase_date,
            first_use_date=db_instance.first_use_date,
            condition=db_instance.condition,
            condition_comment=db_instance.condition_comment,
            purpose=db_instance.purpose_id,
       )
 
    @staticmethod
    async def get_total_amount(item_id: UUID) -> int:
        return await ItemInstanceRepo.get_amount_by_item(item_id)

    @classmethod
    async def get_all_items(cls) -> list[LogicItem]:
        db_items = await ItemRepo.get_all()
        return [cls._to_logic_item(item) for item in db_items]

    @classmethod
    async def get_item(cls,item_id: UUID) -> LogicItem|None:
        item = await ItemRepo.get_by_id(item_id)
        if not item:
            return None
        return cls._to_logic_item(item)

    @classmethod
    async def create_item(cls, contract: CreateItem) -> LogicItem:
        db_item = await ItemRepo.create(**contract.to_kwargs("name", "description", "manufacturer",
                                                    "model", "report_profile_id", "max_lifespan",
                                                    "max_usage_lifespan", "psa_category"))
        return cls._to_logic_item(db_item)

    @classmethod
    async def create_item_instance(cls, contract: CreateItemInstance) -> LogicItemInstance:
        db_instance = await ItemInstanceRepo.create(**contract.to_kwargs("item_id", "external_id",
                                                    "serial_number", "manufacture_date", "purchase_date",
                                                    "first_use_date", "condition", "condition_comment",
                                                    "external_id", "purpose"))
        return cls._to_logic__item_instance(db_instance)

    @classmethod
    async def update_item(cls, id: UUID, contract: UpdateItemData) -> LogicItem:
        db_item = await ItemRepo.update(id, **contract.to_kwargs("name", "description", "manufacturer",
                                                    "model", "report_profile_id", "max_lifespan",
                                                    "max_usage_lifespan", "psa_category"))

        return cls._to_logic_item(db_item)

    @classmethod
    async def update_item_instance(cls, id: UUID, contract: UpdateItemInstanceData) -> LogicItemInstance:
        db_instance = await ItemInstanceRepo.update(id, **contract.to_kwargs("serial_number", "manufacture_date",
                                                    "purchase_date", "first_use_date", "condition",
                                                    "condition_comment", "external_id", "purpose_id"))
        return cls._to_logic__item_instance(db_instance)