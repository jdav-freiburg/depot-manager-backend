from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import LendableGroup
from depot_server.db2.repository.base import ItemNotFound
from depot_server.db2.repository.item.repo_lendable_group import LendableGroupRepo


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_lendable_group_repo_crud_and_children(init_db):
    root = await LendableGroupRepo.create(name="Root", description="Root group")
    child = await LendableGroupRepo.create(
        name="Child",
        description="Child group",
        parent=root.id,
    )

    assert isinstance(root, LendableGroup)
    assert (await LendableGroupRepo.get_by_id(root.id)).id == root.id
    assert [group.id for group in await LendableGroupRepo.get_children_by_parent_id(root.id)] == [child.id]

    updated = await LendableGroupRepo.update(child.id, name="Updated child")
    assert updated.name == "Updated child"

    await LendableGroupRepo.delete_by_id(child.id)
    assert await LendableGroupRepo.get_by_id(child.id) is None


@pytest.mark.asyncio
async def test_lendable_group_repo_rejects_missing_parent(init_db):
    with pytest.raises(ItemNotFound):
        await LendableGroupRepo.create(name="Orphan", parent=uuid4())