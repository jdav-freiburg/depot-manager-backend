from datetime import datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import ItemInstance as ItemInstanceModel
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def item(init_db):
    group = await ItemGroupRepo.create(
        name="Test Group",
        description="Group description",
        parent=None,
    )
    return await ItemRepo.create_item(
        group=group,
        name="Test Item",
        description="Item description",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )


def instance_fields(item):
    return {
        "item": item,
        "external_id": "EXT-001",
        "serial_number": "SN001",
        "manufacture_date": datetime(2024, 1, 1),
        "purchase_date": datetime(2024, 2, 1),
        "first_use_date": datetime(2024, 3, 1),
        "condition": Condition.GOOD,
        "condition_comment": None,
    }


@pytest.mark.asyncio
async def test_item_instance_repo_crud(item):
    instance = await ItemInstanceRepo.create_item_instance(**instance_fields(item))

    assert isinstance(instance, ItemInstanceModel)
    assert instance.serial_number == "SN001"
    assert (await ItemInstanceRepo.get_item_instance_by_id(instance.id)).id == instance.id
    assert (await ItemInstanceRepo.get_all_item_instances())[0].id == instance.id

    updated = await ItemInstanceRepo.update(
        instance.id,
        serial_number="SN002",
        condition=Condition.MONITOR,
    )
    assert updated.serial_number == "SN002"
    assert updated.condition == Condition.MONITOR

    await ItemInstanceRepo.delete_item_instance(instance.id)
    assert await ItemInstanceRepo.get_item_instance_by_id(instance.id) is None


@pytest.mark.asyncio
async def test_item_instance_repo_update_missing_instance_raises(item):
    with pytest.raises(ItemNotFound):
        await ItemInstanceRepo.update(uuid4(), serial_number="Missing")
