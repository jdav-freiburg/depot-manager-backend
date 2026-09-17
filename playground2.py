import asyncio
from os import path
from uuid import UUID
from datetime import date

from tortoise import Tortoise
from tortoise.expressions import Q

from depot_server.api2.models.item_composite import ItemCompositeBase
from depot_server.api2.models.item import ItemInstanceBase, FullItemRaw
from depot_server.api2.models.reservation import ReservationPending
from depot_server.db2.models import Item, ItemInstance, ItemGroup
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.models.common import Condition
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_item_composite import ItemCompositeRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.logic.item import ItemService
from depot_server.logic.item_composite import ItemCompositeService
from depot_server.logic.item_instance import ItemInstanceService, ItemInstanceUniqueConflict
from depot_server.logic.reservation import ReservationService


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
    
    attacheitem = await ItemService.create_item(FullItemRaw(group_id=schraubkarabiner_group.id, name="Petzl attache", description="toller Karabiner", lendable=True,
                                                            psa_category=PsaCategory.CAT_1, serial_number="SN123", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    hawkitem = await ItemService.create_item(FullItemRaw(group_id=schraubkarabiner_group.id, name="Ocun Hawk", description="toller Karabiner", lendable=True,
                                                         psa_category=PsaCategory.CAT_1, serial_number="SN456", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    schlinge = await ItemService.create_item(FullItemRaw(group_id=karabiner_group.id, name="Ocun Schlinge", description="80 cm", lendable=False, psa_category=PsaCategory.CAT_1,
                                                         serial_number="SN789", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    schnapper = await ItemService.create_item(FullItemRaw(group_id=schnapper_group.id, name="Ocun Schnapper", description="toller Schnapper", lendable=False, psa_category=PsaCategory.CAT_1,
                                                          serial_number="SN000", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    await ItemInstanceService.create_item_instance(ItemInstanceBase(item_id=attacheitem.id, serial_number="SN1", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    seil = await Item.create(name="Ocun Seil", description="80 m", lendable=True, psa_category=PsaCategory.CAT_1)
    for i in range(3):
        await ItemInstanceService.create_item_instance(ItemInstanceBase(item_id=seil.id, serial_number=f"SN{i}", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    for i in range(5):
        await ItemInstanceService.create_item_instance(ItemInstanceBase(item_id=schnapper.id, serial_number=f"SN{i}", manufacture_date="2023-01-01", purchase_date="2023-01-02", first_use_date="2023-01-03", condition=Condition.GOOD))
    alpinexe = await ItemCompositeService.create(ItemCompositeBase(name="Alpinexe",
                                                   description="My Composite Item Description",
                                                   lendable=True,
                                                   elements={schlinge.id: 1, schnapper.id: 2}))
    reservation = await ReservationService.create_reservation(ReservationPending(
        name="Test Reservation",
        contact="mail@mail.com",
        items={attacheitem.id: 1, hawkitem.id: 1},
        start="2023-01-10",
        end="2023-01-20"
    ))
    reservation2 = await ReservationService.create_reservation(ReservationPending(
        name="Test Reservation 2",
        contact="mail2@mail.com",
        items={seil.id: 3},
        composite_items={alpinexe.id: 1},
        start="2023-01-15",
        end="2023-01-25"
    ))


    print("Init done")
    await Tortoise.close_connections()

if __name__ == "__main__":
    a = "hallo"
    print(f"läuft: {a}")
    asyncio.run(init("devdepot.sqlite"))
    