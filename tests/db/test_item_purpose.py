from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise
from tortoise.exceptions import ValidationError

from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo

@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def item(init_db):
    return await ItemRepo.create(
        name="Test Item",
        description="Item description",
        psa_category=PsaCategory.NONE,
    )

@pytest.mark.asyncio
async def test_purpose_duplicate(init_db):
    item = await ItemRepo.create(
        name="Test Item",
        description="Item description",
        psa_category=PsaCategory.NONE,
    )
    item2 = await ItemRepo.create(
        name="Test Item 2",
        description="Item description 2",
        psa_category=PsaCategory.NONE,
    )
    purpose1 = await ItemPurposeRepo.create(item=item, name="Purpose 1")

    with pytest.raises(ValidationError):
        await ItemInstanceRepo.create(item=item2, purpose=purpose1,
                                      serial_number="SN001", external_id="EXT001",
                                      manufacture_date=date(2024, 1, 1), purchase_date=date(2024, 2, 1),
                                      first_use_date=date(2024, 3, 1), condition="good")