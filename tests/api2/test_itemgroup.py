from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.item_group import router
from depot_server.api2.models.item_group import ItemGroup


@pytest.fixture
def client():
    """Create a FastAPI test client with the item_group router"""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_item_groups_calls_repo(client):
    """Test GET /item_group calls ItemGroupRepo.get_all"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.pk = ig_id
    mock_db_ig.name = "Group A"
    mock_db_ig.id_prefix = "GA"
    mock_db_ig.description = "First group"

    model_ig = ItemGroup(id=ig_id, name="Group A", id_prefix="GA", description="First group")

    with patch("depot_server.api2.item_group.ItemGroupRepo.get_all", new_callable=AsyncMock) as mock_get_all:
        with patch("depot_server.api2.item_group.item_group_from_orm") as mock_from_orm:
            mock_get_all.return_value = [mock_db_ig]
            mock_from_orm.return_value = model_ig

            response = client.get("/item_group")

            mock_get_all.assert_called_once()
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == str(ig_id)
            assert data[0]["name"] == "Group A"


@pytest.mark.asyncio
async def test_get_item_group_by_id_calls_repo(client):
    """Test GET /item_group/{id} calls ItemGroupRepo.get_by_id with correct id"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.pk = ig_id
    mock_db_ig.name = "Single Group"
    mock_db_ig.id_prefix = "SG"
    mock_db_ig.description = "A single group"

    model_ig = ItemGroup(id=ig_id, name="Single Group", id_prefix="SG", description="A single group")

    with patch("depot_server.api2.item_group.ItemGroupRepo.get_by_id", new_callable=AsyncMock) as mock_get:
        with patch("depot_server.api2.item_group.item_group_from_orm") as mock_from_orm:
            mock_get.return_value = mock_db_ig
            mock_from_orm.return_value = model_ig

            response = client.get(f"/item_group/{ig_id}")

            mock_get.assert_called_once_with(ig_id)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(ig_id)
            assert data["name"] == "Single Group"
            assert data["id_prefix"] == "SG"


@pytest.mark.asyncio
async def test_get_item_group_not_found(client):
    """Test GET /item_group/{id} returns 404 when not found"""
    ig_id = uuid4()

    with patch("depot_server.api2.item_group.ItemGroupRepo.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/item_group/{ig_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "ItemGroup not found"


@pytest.mark.asyncio
async def test_create_item_group_calls_repo(client):
    """Test POST /item_group calls ItemGroupRepo.create with correct parameters"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.pk = ig_id
    mock_db_ig.name = "New Group"
    mock_db_ig.id_prefix = "NG"
    mock_db_ig.description = "Newly created group"

    model_ig = ItemGroup(id=ig_id, name="New Group", id_prefix="NG", description="Newly created group")

    with patch("depot_server.api2.item_group.ItemGroupRepo.create", new_callable=AsyncMock) as mock_create:
        with patch("depot_server.api2.item_group.item_group_from_orm") as mock_from_orm:
            mock_create.return_value = mock_db_ig
            mock_from_orm.return_value = model_ig

            payload = {
                "name": "New Group",
                "id_prefix": "NG",
                "description": "Newly created group"
            }
            response = client.post("/item_group", json=payload)

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["name"] == "New Group"
            assert call_kwargs["id_prefix"] == "NG"
            assert call_kwargs["description"] == "Newly created group"

            assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_item_group_calls_repo(client):
    """Test PUT /item_group/{id} calls ItemGroupRepo.update_item_group with correct parameters"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.pk = ig_id
    mock_db_ig.name = "Updated Group"
    mock_db_ig.id_prefix = "UG"
    mock_db_ig.description = "Updated description"

    model_ig = ItemGroup(id=ig_id, name="Updated Group", id_prefix="UG", description="Updated description")

    with patch("depot_server.api2.item_group.ItemGroupRepo.update_item_group", new_callable=AsyncMock) as mock_update:
        with patch("depot_server.logic.item_group.ItemRepo.update_item_group", new_callable=AsyncMock) as mock_update_items:
            with patch("depot_server.api2.item_group.item_group_from_orm") as mock_from_orm:
            mock_update.return_value = mock_db_ig
            mock_from_orm.return_value = model_ig

            payload = {
                "name": "Updated Group",
                "id_prefix": "UG",
                "description": "Updated description"
            }
                response = client.put(f"/item_group/{ig_id}", json=payload)

                mock_update.assert_called_once()
                call_args = mock_update.call_args
                assert call_args[0][0] == ig_id  # First positional arg is item_group_id
                call_kwargs = call_args[1]
                assert call_kwargs["name"] == "Updated Group"
                assert call_kwargs["id_prefix"] == "UG"
                assert call_kwargs["description"] == "Updated description"
                mock_update_items.assert_awaited_once_with(
                    ig_id,
                    name="Updated Group",
                    description="Updated description",
                )

                assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_item_group_calls_repo(client):
    """Test DELETE /item_group/{id} calls ItemGroupRepo.delete_by_id with correct id"""
    ig_id = uuid4()

    with patch("depot_server.api2.item_group.ItemGroupRepo.delete_by_id", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = client.delete(f"/item_group/{ig_id}")

        mock_delete.assert_called_once_with(ig_id)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_item_group_from_orm_called(client):
    """Test that item_group_from_orm is called for response transformation"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.pk = ig_id
    mock_db_ig.name = "Test Group"
    mock_db_ig.id_prefix = "TG"
    mock_db_ig.description = "Test description"

    model_ig = ItemGroup(id=ig_id, name="Test Group", id_prefix="TG", description="Test description")

    with patch("depot_server.api2.item_group.ItemGroupRepo.get_by_id", new_callable=AsyncMock) as mock_get:
        with patch("depot_server.api2.item_group.item_group_from_orm") as mock_from_orm:
            mock_get.return_value = mock_db_ig
            mock_from_orm.return_value = model_ig

            response = client.get(f"/item_group/{ig_id}")

            mock_from_orm.assert_called_once_with(mock_db_ig)
            assert response.status_code == 200
