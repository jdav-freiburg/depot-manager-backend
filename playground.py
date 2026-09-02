import asyncio
from uuid import uuid4

from tortoise import Tortoise

from depot_server.db2.models import Item
from depot_server.db2.models.common import Condition
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_storage_location import StorageLocationRepo
from depot_server.db2.repository.report.repo_report_profile import ReportProfileRepo


async def init():
    await Tortoise.init(
        db_url="sqlite://playground.sqlite",
        modules={"depot": ["depot_server.db2.models"]},
    )

    await Tortoise.generate_schemas()
    print("Init done")

    # Create required related objects first (FK and M2M prerequisites)
    group = await ItemGroupRepo.create(
        name="Electronics",
        id_prefix="EXT",
        description="Electronics",
        # Add other required fields for ItemGroup
    )

    storage_location = await StorageLocationRepo.create(
        name="Warehouse A",
        # Add other required fields for StorageLocation
    )

    report_profile = await ReportProfileRepo.create(
        name="Standard Inspection",
        created_by=uuid4(),
        updated_by=uuid4(),
        # Add other required fields for ReportProfile
    )

    report_profile2 = await ReportProfileRepo.create(
        name="Extensive Inspection",
        created_by=uuid4(),
        updated_by=uuid4(),
        # Add other required fields for ReportProfile
    )

    # Now create the Item with FKs set
    item: Item = await ItemRepo.create(
        group=group,  # Required FK
        storage_location=storage_location,  # Optional FK
        report_profile=report_profile,  # Optional FK
        external_id="EXT-001",  # Required
        created_by=uuid4(),  # Required UUID, replace with actual user ID
        name="Dell Laptop",  # Required
        description="A standard office laptop",
        manufacturer="Dell",
        model="Latitude 5420",
        serial_number="SN123456",
        lendable=True,
        condition=Condition.GOOD,  # Required serial_number

        # Other optional fields like manufacture_date, purchase_date, etc., can be added
    )

    profiles = await ReportProfileRepo.Db_type.all()

    await Tortoise.close_connections()


if __name__ == "__main__":
    a = "hallo"
    print(f"läuft: {a}")
    asyncio.run(init())
