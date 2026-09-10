from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import Item
from depot_server.db2.models.changelog import Changelog
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.repository.audit import AuditInfo
from depot_server.db2.repository.item.repo_item import ItemRepo
from depot_server.db2.repository.item.repo_item_group import ItemGroupRepo
from depot_server.db2.repository.item.repo_storage_location import StorageLocationRepo
from depot_server.db2.repository.item.repo_tag import TagRepo
from depot_server.db2.repository.report.repo_report_profile import ReportProfileRepo


@pytest_asyncio.fixture(scope="function")
async def init_db():
    """Initialize test database"""
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"depot": ["depot_server.db2.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture(scope="function")
async def test_data(init_db):
    """Create test data for item creation"""
    group = await ItemGroupRepo.create(
        name="Test Group",
        description="Test Group Description",
        parent=None,
    )

    storage_location = await StorageLocationRepo.create(
        name="Test Storage",
    )

    report_profile = await ReportProfileRepo.create(
        name="Test Profile",
        created_by=uuid4(),
        updated_by=uuid4(),
    )

    report_profile_alt = await ReportProfileRepo.create(
        name="Alternative Profile",
        created_by=uuid4(),
        updated_by=uuid4(),
    )

    tag = await TagRepo.create(
        name="Test Tag",
        description="A test tag",
        color="#FF0000",
    )

    tag_alt = await TagRepo.create(
        name="Alternative Tag",
        description="An alternative tag",
        color="#00FF00",
    )

    return {
        "group": group,
        "storage_location": storage_location,
        "report_profile": report_profile,
        "report_profile_alt": report_profile_alt,
        "tag": tag,
        "tag_alt": tag_alt,
    }


@pytest.mark.asyncio
async def test_save_without_audit_info_raises_error(test_data):
    """Test that changes can't be made without providing an AuditInfo object"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Modify the item
    item.name = "Modified Item"

    # Try to save without AuditInfo - should fail
    with pytest.raises(TypeError):
        await ItemRepo.save(item)


@pytest.mark.asyncio
async def test_single_field_change_recorded_in_changelog(test_data):
    """Test that a single field change is recorded in the Changelog"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Modify the item
    item.name = "Modified Item"
    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="Changed item name")

    # Save with audit info
    await ItemRepo.save(item, info)

    # Check that Changelog entry was created
    changelog = await Changelog.get(type_id=item.id)
    assert changelog is not None
    assert changelog.old["name"] == "Test Item"
    assert changelog.new["name"] == "Modified Item"
    assert str(changelog.user_id) == str(user_id)
    assert changelog.comment == "Changed item name"


@pytest.mark.asyncio
async def test_multiple_field_changes_recorded_in_changelog(test_data):
    """Test that multiple field changes are all recorded in the Changelog"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Modify multiple fields
    item.name = "Modified Item"
    item.description = "Modified description"
    item.manufacturer = "New Manufacturer"
    item.model = "Model Y"

    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="Multiple changes")

    # Save with audit info
    await ItemRepo.save(item, info)

    # Check that Changelog entry was created with all changes
    changelog = await Changelog.get(type_id=item.id)
    assert changelog is not None
    assert changelog.old["name"] == "Test Item"
    assert changelog.new["name"] == "Modified Item"
    assert changelog.old["description"] == "Original description"
    assert changelog.new["description"] == "Modified description"
    assert changelog.old["manufacturer"] == "Test Manufacturer"
    assert changelog.new["manufacturer"] == "New Manufacturer"
    assert changelog.old["model"] == "Model X"
    assert changelog.new["model"] == "Model Y"


@pytest.mark.asyncio
async def test_foreign_key_change_recorded_in_changelog(test_data):
    """Test that foreign key changes are recorded in the Changelog"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Modify the foreign key
    original_profile_id = item.report_profile_id
    item.report_profile = test_data["report_profile_alt"]

    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="Changed report profile")

    # Save with audit info
    await ItemRepo.save(item, info)

    # Check that Changelog entry was created with the FK change
    changelog = await Changelog.get(type_id=item.id)
    assert changelog is not None
    # FK fields are stored with _id suffix
    assert str(changelog.old["report_profile_id"]) == str(original_profile_id)
    assert str(changelog.new["report_profile_id"]) == str(test_data["report_profile_alt"].id)


@pytest.mark.asyncio
async def test_no_changelog_created_when_no_changes(test_data):
    """Test that no Changelog entry is created when there are no changes"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Don't modify the item - just try to save
    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="No changes")

    # Save with audit info (no changes)
    await ItemRepo.save(item, info)

    # Check that no Changelog entry was created
    changelogs = await Changelog.filter(type_id=item.id)
    assert len(changelogs) == 0


@pytest.mark.asyncio
async def test_transaction_rollback_on_error(test_data):
    """Test that if something fails, the transaction is rolled back, meaning no data is changed accidentally"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    original_name = item.name

    # Modify the item
    item.name = "Modified Item"

    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="This will fail")

    # Force an error by creating a conflicting external_id during save
    # We'll create a scenario where the transaction should rollback
    # For this test, we'll monkey-patch the save to simulate a failure
    original_save = item.save

    async def failing_save():
        await original_save()
        raise RuntimeError("Simulated database error during save")

    item.save = failing_save

    # Try to save - should raise error and rollback
    with pytest.raises(RuntimeError):
        await ItemRepo.save(item, info)

    # Reload the item from database
    reloaded_item = await Item.get(id=item.id)

    # Verify that the original values are still in the database (transaction rolled back)
    assert reloaded_item.name == original_name

    # Verify that no Changelog entry was created
    changelogs = await Changelog.filter(type_id=item.id)
    assert len(changelogs) == 0


@pytest.mark.asyncio
async def test_audit_info_with_empty_comment(test_data):
    """Test that AuditInfo can have an empty comment"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Modify the item
    item.name = "Modified Item"
    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="")

    # Save with empty comment
    await ItemRepo.save(item, info)

    # Check that Changelog entry was created with empty comment
    changelog = await Changelog.get(type_id=item.id)
    assert changelog is not None
    assert changelog.comment == ""
    assert changelog.old["name"] == "Test Item"
    assert changelog.new["name"] == "Modified Item"


@pytest.mark.asyncio
async def test_changelog_entry_has_correct_type_and_timestamp(test_data):
    """Test that Changelog entries record the correct model type and timestamp"""
    # Create an item
    item = await ItemRepo.create(
        group=test_data["group"],
        storage_location=test_data["storage_location"],
        report_profile=test_data["report_profile"],
        name="Test Item",
        description="Original description",
        manufacturer="Test Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        lendable=True,
    )

    # Modify the item
    item.name = "Modified Item"
    user_id = uuid4()
    info = AuditInfo(user_id=user_id, comment="Type and timestamp test")

    # Save with audit info
    await ItemRepo.save(item, info)

    # Check that Changelog entry has the correct type and ID
    changelog = await Changelog.get(type_id=item.id)
    assert changelog is not None
    assert str(item.__class__) in changelog.type_
    assert changelog.type_id == item.id
    assert changelog.timestamp is not None
