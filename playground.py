import asyncio

from tortoise import Tortoise

from depot_server.db2.models import Tag
from depot_server.db2.repository.base import TagRepo


async def init():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"depot": ["depot_server.db2.models"]},
    )

    await Tortoise.generate_schemas()
    print("Init done")

    item1 = await TagRepo.create(name="test", description="test description", color="#FF00FF")
    tag2 = Tag.construct(id=item1.pk, name="changed name", description="test description", color="#FF00FF")

    # diff = TagRepo._calculate_diff(item1, tag2)
    print(item1)
    print(tag2)
    # print(f"diff: {diff}")

    await Tortoise.close_connections()


if __name__ == "__main__":
    a = "hallo"
    print(f"läuft: {a}")
    asyncio.run(init())
