import asyncio
from os import path
from uuid import UUID

from tortoise import Tortoise
from tortoise.expressions import Q

from depot_server.api2.models.item_composite import ItemCompositeBase
from depot_server.db2.models import Item, ItemInstance, ItemGroup
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.models.common import Condition
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_item_composite import ItemCompositeRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.logic.item_composite import ItemCompositeService


def remove_db(path):
    import os
    if os.path.exists(path):
        os.remove(path)
    print("DB purged")

async def init(path):
    remove_db(path)
    await Tortoise.init(
    db_url=f"sqlite://{path}",
    modules={"depot": ["depot_server.db2.models"]},
    )
    await Tortoise.generate_schemas()
    

    karabiner_group = await ItemGroup.create(name="Karabiner", description="Karabiner")
    schraubkarabiner_group = await ItemGroup.create(name="Schraubkarabiner", description="Schraubkarabiner", parent=karabiner_group)
    schnapper_group = await ItemGroup.create(name="Schnapper", description="Schnapper", parent=karabiner_group)
    
    attacheitem = await Item.create(group_id=schraubkarabiner_group.id, name="Petzl attache", description="toller Karabiner", lendable=True, psa_category=PsaCategory.CAT_1)
    hawkitem = await Item.create(group_id=schraubkarabiner_group.id, name="Ocun Hawk", description="toller Karabiner", lendable=False, psa_category=PsaCategory.CAT_1)
    seil = await Item.create(name="Ocun Seil", description="80 m", lendable=True, psa_category=PsaCategory.CAT_1)
    for i in range(5):
        await ItemInstance.create(item=hawkitem, serial_number=f"SN{i}", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD)
    composite = await ItemCompositeService.create(ItemCompositeBase(name="My Composite Item",
                                                   description="My Composite Item Description",
                                                   lendable=True,
                                                   elements={attacheitem.id: 2, seil.id: 3}))


    print("Init done")
    await Tortoise.close_connections()

if __name__ == "__main__":
    a = "hallo"
    print(f"läuft: {a}")
    asyncio.run(init("devdepot.sqlite"))
    