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
async def test_base_save_and_get(init_db):
    # create via classmethod create
    tag = await TagRepo.create(name="base1", description="d", color="#abcdef")
    assert isinstance(tag, TagModel)

    # modify and save via BaseRepo.save
    tag.name = "base1-mod"
    saved = await TagRepo.save(tag)
    assert saved.name == "base1-mod"

    # get_by_id returns the updated object
    fetched = await TagRepo.get_by_id(tag.id)
    assert fetched is not None
    assert fetched.name == "base1-mod"


@pytest.mark.asyncio
async def test_delete_by_id_raises_when_missing(init_db):
    with pytest.raises(ItemNotFound):
        await TagRepo.delete_by_id(uuid4())
