from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import Item as ItemModel
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def item_data(init_db):
    group = await ItemGroupRepo.create(
        name="Test Group",
        description="Group description",
        parent=None,
    )
    return {
        "group": group,
        "item": await ItemRepo.create_item(
            group=group,
            name="Test Item",
            description="Item description",
            lendable=True,
            manufacturer="Manufacturer",
            model="Model X",
            psa_category=PsaCategory.NONE,
        ),
    }


@pytest.mark.asyncio
async def test_item_repo_crud(item_data):
    item = item_data["item"]

    assert isinstance(item, ItemModel)
    assert item.name == "Test Item"
    assert (await ItemRepo.get_item_by_id(item.id)).id == item.id
    assert (await ItemRepo.get_all_items())[0].id == item.id

    updated = await ItemRepo.update_item(item.id, name="Updated Item", model="Model Y")
    assert updated.name == "Updated Item"
    assert updated.model == "Model Y"

    await ItemRepo.delete_item(item.id)
    assert await ItemRepo.get_item_by_id(item.id) is None


@pytest.mark.asyncio
async def test_item_repo_update_missing_item_raises(item_data):
    with pytest.raises(ItemNotFound):
        await ItemRepo.update_item(uuid4(), name="Missing")
