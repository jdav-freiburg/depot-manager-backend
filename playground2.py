import asyncio
from os import path
from uuid import UUID

from tortoise import Tortoise

from depot_server.db2.models import Item, ItemInstance, ItemGroup
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.models.common import Condition
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo


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
    print("Init done")

    schraubkarabiner =await ItemGroup.create(name="Schraubkarabiner", description="Schraubkarabiner", lendable=True)
    attache = await ItemGroup.create(name="Petzl attache", description="toller Karabiner", lendable=False, parent=schraubkarabiner)
    hawk = await ItemGroup.create(name="Ocun Hawk", description="toller Karabiner", lendable=False, parent=schraubkarabiner)
    attacheitem = await Item.create(group_id=attache.id, name="Petzl attache", description="toller Karabiner", psa_category=PsaCategory.CAT_1)
    hawkitem = await Item.create(group_id=hawk.id, name="Ocun Hawk", description="toller Karabiner", psa_category=PsaCategory.CAT_1)
    schnapperinstance = await ItemInstance.create(item=attacheitem,serial_number="SN123", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD, created_by=UUID("00000000-0000-0000-0000-000000000001"))
    myitems = await ItemGroupRepo.create(name="My Item", description="My Item Description", lendable=True)


if __name__ == "__main__":
    a = "hallo"
    print(f"läuft: {a}")
    asyncio.run(init("devdepot.sqlite"))
    