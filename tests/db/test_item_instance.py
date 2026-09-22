from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise
from tortoise.exceptions import ValidationError

from depot_server.db2.models import ItemInstance as ItemInstanceModel
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def item(init_db):
    return await ItemRepo.create_item(
        name="Test Item",
        description="Item description",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )


def instance_fields(item, purpose, serial_number, external_id):
    return {
        "item": item,
        "purpose": purpose,
        "external_id": external_id,
        "serial_number": serial_number,
        "manufacture_date": date(2024, 1, 1),
        "purchase_date": date(2024, 2, 1),
        "first_use_date": date(2024, 3, 1),
        "condition": Condition.GOOD,
        "condition_comment": None,
    }


@pytest.mark.asyncio
async def test_item_instance_repo_crud(init_db):
    purpose = await ItemPurposeRepo.create(
        name="Test Purpose",
        description="Purpose description",
    )
    purpose2 = await ItemPurposeRepo.create(
        name="Test Purpose 2",
        description="Purpose description 2",
    )
    item = await ItemRepo.create_item(
        name="Test Item",
        description="Item description",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )
    item2 = await ItemRepo.create_item(
        name="Test Item 2",
        description="Item description 2",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )
    instance = await ItemInstanceRepo.create(**instance_fields(item, purpose, serial_number="SN001",
                                                               external_id="EXT-001"))
    instance2 = await ItemInstanceRepo.create(**instance_fields(item, purpose, serial_number="SN002",
                                                                external_id="EXT-002"))
    instance3 = await ItemInstanceRepo.create(**instance_fields(item, purpose2, serial_number="SN003",
                                                                external_id="EXT-003"))
    # Each purpose can only be assigned to one item
    with pytest.raises(ValidationError):
        instance4 = await ItemInstanceRepo.create(**instance_fields(item2, purpose, serial_number="SN004",
                                                  external_id="EXT-004"))
    with pytest.raises(ValidationError):
        await ItemInstanceRepo.update(instance3.id, item=item2, purpose=purpose)

    # Each serial_number and external_id (if exists) must be unique per item
    with pytest.raises(ValidationError):
        await ItemInstanceRepo.create(**instance_fields(item, purpose, serial_number="SN001",
                                                         external_id="EXT-005"))
    with pytest.raises(ValidationError):
        await ItemInstanceRepo.create(**instance_fields(item, purpose, serial_number="SN005",
                                                         external_id="EXT-001"))
        
    instance5 = await ItemInstanceRepo.create(**instance_fields(item, purpose2, serial_number="SN005",
                                                               external_id=None))

    assert isinstance(instance, ItemInstanceModel)
    assert instance.serial_number == "SN001"
    assert (await ItemInstanceRepo.get_by_id(instance.id)).id == instance.id
    assert (await ItemInstanceRepo.get_all())[0].id == instance.id
    assert len(await ItemInstanceRepo.get_all()) == 4
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
