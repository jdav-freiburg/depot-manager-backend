from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import Tag as TagModel
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_tag import TagRepo


@pytest_asyncio.fixture(scope="function")
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_tag_crud_operations(init_db):
    repo = TagRepo()

    # Create without explicit id - should auto-generate
    tag = await repo.create_tag(name="t1", description="d1", color="#ff00ff")
    assert isinstance(tag, TagModel)
    assert tag.name == "t1"
    assert tag.id is not None  # UUID was auto-generated
    original_id = tag.id

    # Get by id
    fetched = await repo.get_tag_by_id(tag.id)
    assert fetched is not None
    assert fetched.id == tag.id

    # List all
    all_tags = await repo.get_all_tags()
    assert any(t.id == tag.id for t in all_tags)

    # Update
    updated = await repo.update_tag(tag.id, name="updated", description="d2")
    assert updated.name == "updated"
    assert updated.description == "d2"

    # Invalid update field
    with pytest.raises(ValueError):
        await repo.update_tag(tag.id, nonexistent_field="x")

    # Delete
    await repo.delete_tag(tag.id)

    # After delete, get_by_id should return None
    got = await repo.get_tag_by_id(tag.id)
    assert got is None


@pytest.mark.asyncio
async def test_uuid_auto_generated_on_create(init_db):
    repo = TagRepo()

    # Create tag without providing id
    tag = await repo.create_tag(name="auto_id_tag", description="test", color="#abcdef")
    assert tag.id is not None
    id_after_create = tag.id

    # Verify it's persisted
    fetched = await repo.get_tag_by_id(id_after_create)
    assert fetched is not None
    assert fetched.id == id_after_create


@pytest.mark.asyncio
async def test_uuid_cannot_change_on_update(init_db):
    repo = TagRepo()

    # Create tag
    tag = await repo.create_tag(name="immutable_id", description="test", color="#123456")
    original_id = tag.id

    # Try to update the id - should raise ValueError
    new_id = uuid4()
    with pytest.raises(ValueError, match="Cannot update the id field"):
        await repo.update_tag(tag.id, id=new_id)


@pytest.mark.asyncio
async def test_delete_nonexistent_raises(init_db):
    # delete non existing should raise ItemNotFound
    with pytest.raises(ItemNotFound):
        await TagRepo.delete_by_id(uuid4())
