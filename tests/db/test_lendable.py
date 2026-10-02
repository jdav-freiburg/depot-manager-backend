from datetime import date, datetime
import pytest_asyncio
import pytest

from tortoise import Tortoise
from tortoise.exceptions import IntegrityError

from depot_server.db2.repository.item.repo_item_instance import ItemInstanceRepo
from depot_server.db2.repository.item.repo_item_purpose import ItemPurposeRepo
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_lendable import LendableRepo, LinkLendablePurposeRepo
from depot_server.logic.lendable import LendableService

from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest.mark.asyncio
async def test_lendable_duplicates(init_db):
    # Create an item purpose
    purpose = await ItemPurposeRepo.create(
        name="Test Purpose",
        description="Purpose description",
    )
    
    # Create an item
    item = await ItemRepo.create(
        name="Test Item",
        description="Item description",
        psa_category=PsaCategory.CAT_1,
    )
    
    # Create item instances
    for i in range(5):
        await ItemInstanceRepo.create(
            item=item,
            purpose=purpose,
            serial_number=f"SN00{i}",
            external_id=f"EXT00{i}",
            manufacture_date=date(2024, 1, 1),
            purchase_date=date(2024, 2, 1),
            first_use_date=date(2024, 3, 1),
            condition=Condition.GOOD,
        )
    
    # Create a lendable
    lendable = await LendableRepo.create(name="Test Lendable", description="A test lendable", lendable=True)
    lendable2 = await LendableRepo.create(name="Test Lendable 2", description="A test lendable 2", lendable=True)
    
    # Link the lendable to the purpose with a certain amount
    await LinkLendablePurposeRepo.create(lendable=lendable, amount=1, purpose=purpose)
    with pytest.raises(IntegrityError):
        await LinkLendablePurposeRepo.create(lendable=lendable2, amount=1, purpose=purpose)

@pytest.mark.asyncio
async def test_lendable_amount(init_db):
    # Create an item purpose
    purpose_einzelschlinge = await ItemPurposeRepo.create(
        name="Schlinge",
        description="Einzelitem",
    )
    purpose_schlinge_alpinexe = await ItemPurposeRepo.create(
            name="Schlinge",
            description="Für Alpinexen",
        )
    purpose_schnapper_alpinexe = await ItemPurposeRepo.create(
        name="Schnapper",
        description="Für Alpinexen",
    )
    
    # Create an item
    item = await ItemRepo.create(
        name="Schlinge 60 cm",
        description="Dynema Schlinge 60 cm",
        psa_category=PsaCategory.CAT_1,
    )
    item2 = await ItemRepo.create(
        name="Edelrid Schnapper",
        description="Schnapper",
        psa_category=PsaCategory.CAT_1,
    )
    # Create item instances
    for i in range(5):
        await ItemInstanceRepo.create(
            item=item,
            purpose=purpose_einzelschlinge,
            serial_number=f"SN00{i}",
            external_id=f"EXT00{i}",
            manufacture_date=date(2024, 1, 1),
            purchase_date=date(2024, 2, 1),
            first_use_date=date(2024, 3, 1),
            condition=Condition.GOOD,
        )
    for i in range(3):
        await ItemInstanceRepo.create(
            item=item,
            purpose=purpose_schlinge_alpinexe,
            serial_number=f"SN00{i + 5}",
            external_id=f"EXT00{i + 5}",
            manufacture_date=date(2024, 1, 1),
            purchase_date=date(2024, 2, 1),
            first_use_date=date(2024, 3, 1),
            condition=Condition.GOOD,
        )
    for i in range(3):
        await ItemInstanceRepo.create(
            item=item2,
            purpose=purpose_schnapper_alpinexe,
            serial_number=f"SN20{i}",
            external_id=f"EXT00{i}",
            manufacture_date=date(2024, 1, 1),
            purchase_date=date(2024, 2, 1),
            first_use_date=date(2024, 3, 1),
            condition=Condition.GOOD,
        )
    lendable_schlinge = await LendableRepo.create(name="Schlinge", description="A test lendable", lendable=True)
    lendable_alpinexe = await LendableRepo.create(name="Alpinexe", description="A test lendable", lendable=True)
    await LinkLendablePurposeRepo.create(lendable=lendable_schlinge, amount=1, purpose=purpose_einzelschlinge)
    await LinkLendablePurposeRepo.create(lendable=lendable_alpinexe, amount=1, purpose=purpose_schlinge_alpinexe)
    await LinkLendablePurposeRepo.create(lendable=lendable_alpinexe, amount=2, purpose=purpose_schnapper_alpinexe)

    assert (await LendableService().get_total_amount(lendable_schlinge.id)) == 5
    assert (await LendableService().get_total_amount(lendable_alpinexe.id)) == 1
