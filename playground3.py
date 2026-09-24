import os
import asyncio
from tortoise import Tortoise
from tortoise.query_utils import Prefetch

from depot_server.db2.models.item.lendable import Lendable, LinkLendablePurpose
from depot_server.db2.models.item.item_purpose import ItemPurpose


def remove_db(path):
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
    purpose1 = await ItemPurpose.create(name="Test Purpose")
    purpose2 = await ItemPurpose.create(name="Test Purpose 2")
    lendable1 = await Lendable.create(name="Test Lendable 1", description="Test Description 1", in_limbus=0)
    lendable2 = await Lendable.create(name="Test Lendable 2", description="Test Description 2", in_limbus=0)
    link1 = await LinkLendablePurpose.create(lendable=lendable1, purpose=purpose1, amount=2)
    link2 = await LinkLendablePurpose.create(lendable=lendable1, purpose=purpose2, amount=3)

    #lendable_with_links = await Lendable.filter(id=lendable1.id, lendable_purpose_link__amount__gte=1).select_related("lendable_purpose_link").all()

    

    lendable_with_links = await (
        Lendable
        .filter(id=lendable1.id, lendable_purpose_link__amount=2)
        .prefetch_related(
            Prefetch(
                "lendable_purpose_link",
                queryset=LinkLendablePurpose.filter(amount__gte=2),
            )
        )
        .first()
    )

    # for lendable in lendable_with_links:
    #     print(f"Lendable: {lendable.name}, Description: {lendable.description}")
    #     for link in lendable.lendable_purpose_link:
    #         print(link)

    #print(lendable_with_links.lendable_purpose_link[0].amount)
    for link in lendable_with_links.lendable_purpose_link:
        print(f"Link: {link.id}, Amount: {link.amount}")

    print("Init done")
    await Tortoise.close_connections()


if __name__ == "__main__":
    a = "hallo"
    print(f"läuft: {a}")
    asyncio.run(init("devdepot.v3.sqlite"))