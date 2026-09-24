from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import Item as ItemModel
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def item_data(init_db):
    return await ItemRepo.create(
            name="Test Item",
            description="Item description",
            lendable=True,
            manufacturer="Manufacturer",
            model="Model X",
            psa_category=PsaCategory.NONE,
        )


@pytest.mark.asyncio
async def test_item_repo_crud(item_data):
    assert isinstance(item_data, ItemModel)
    assert item_data.name == "Test Item"
    assert (await ItemRepo.get_by_id(item_data.id)).id == item_data.id
    assert (await ItemRepo.get_all())[0].id == item_data.id

    updated = await ItemRepo.update_item(item_data.id, name="Updated Item", model="Model Y")
    assert updated.name == "Updated Item"
    assert updated.model == "Model Y"

    await ItemRepo.delete_by_id(item_data.id)
    assert await ItemRepo.get_by_id(item_data.id) is None


@pytest.mark.asyncio
async def test_item_repo_update_missing_item_raises(item_data):
    with pytest.raises(ItemNotFound):
        await ItemRepo.update_item(uuid4(), name="Missing")
