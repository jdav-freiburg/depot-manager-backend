from datetime import date, datetime
import pytest_asyncio
import pytest

from tortoise import Tortoise

from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_item_purpose_amount(init_db):
    # Create an item purpose
    purpose = await ItemPurposeRepo.create(
        name="Test Purpose",
        description="Purpose description",
    )

    