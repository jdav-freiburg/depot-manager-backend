from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.lendable_group import router
from depot_server.db2.repository.base import ItemNotFound


@pytest.fixture
def client():
    """Create a FastAPI test client with the lendable_group router"""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_lendable_groups_calls_service(client):
    """Test GET /lendable_group calls LendableGroupService.get_all"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.id = ig_id
    mock_db_ig.name = "Group A"
    mock_db_ig.description = "First group"
    mock_db_ig.parent = None

    with patch("depot_server.api2.lendable_group.LendableGroupService.get_all", new_callable=AsyncMock) as mock_get_all:
        mock_get_all.return_value = [mock_db_ig]
        response = client.get("/lendable_group/")

        mock_get_all.assert_called_once()
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(ig_id)
        assert data[0]["name"] == "Group A"


@pytest.mark.asyncio
async def test_get_lendable_group_by_id_calls_service(client):
    """Test GET /lendable_group/{id} calls the service with the correct id"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.id = ig_id
    mock_db_ig.name = "Single Group"
    mock_db_ig.description = "A single group"
    mock_db_ig.parent = None

    with patch("depot_server.api2.lendable_group.LendableGroupService.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_db_ig
        response = client.get(f"/lendable_group/{ig_id}")

        mock_get.assert_called_once_with(ig_id)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(ig_id)
        assert data["name"] == "Single Group"


@pytest.mark.asyncio
async def test_get_lendable_group_not_found(client):
    """Test GET /lendable_group/{id} returns 404 when not found"""
    ig_id = uuid4()

    with patch("depot_server.api2.lendable_group.LendableGroupService.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = ItemNotFound
        response = client.get(f"/lendable_group/{ig_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "ItemGroup not found"


@pytest.mark.asyncio
async def test_create_lendable_group_calls_service(client):
    """Test POST /lendable_group calls LendableGroupService.create"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.id = ig_id
    mock_db_ig.name = "New Group"
    mock_db_ig.description = "Newly created group"
    mock_db_ig.parent = None

    with patch("depot_server.api2.lendable_group.LendableGroupService.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_db_ig
        payload = {
            "name": "New Group",
            "description": "Newly created group",
            "parent_id": None,
        }
        response = client.post("/lendable_group/", json=payload)

        mock_create.assert_called_once()
        contract = mock_create.call_args.args[0]
        assert contract.name == "New Group"
        assert contract.description == "Newly created group"
        assert contract.parent is None

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_lendable_group_calls_service(client):
    """Test PUT /lendable_group/{id} calls the service with correct parameters"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.id = ig_id
    mock_db_ig.name = "Updated Group"
    mock_db_ig.description = "Updated description"
    mock_db_ig.parent = None

    with patch("depot_server.api2.lendable_group.LendableGroupService.update_lendable_group", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_db_ig
        payload = {
            "name": "Updated Group",
            "description": "Updated description",
            "parent_id": None,
        }
        response = client.put(f"/lendable_group/{ig_id}", json=payload)

        mock_update.assert_awaited_once()
        call_args = mock_update.call_args
        assert call_args.args[0] == ig_id
        contract = call_args.args[1]
        assert contract.name == payload["name"]
        assert contract.description == payload["description"]
        assert contract.parent is None

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_lendable_group_calls_service(client):
    """Test DELETE /lendable_group/{id} calls the service with the correct id"""
    ig_id = uuid4()

    with patch("depot_server.api2.lendable_group.LendableGroupService.delete_by_id", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = client.delete(f"/lendable_group/{ig_id}")

        mock_delete.assert_called_once_with(ig_id)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_lendable_group_returns_service_result(client):
    """Test that the service result is transformed to the API model"""
    ig_id = uuid4()
    mock_db_ig = MagicMock()
    mock_db_ig.id = ig_id
    mock_db_ig.name = "Test Group"
    mock_db_ig.description = "Test description"
    mock_db_ig.parent = None

    with patch("depot_server.api2.lendable_group.LendableGroupService.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_db_ig
        response = client.get(f"/lendable_group/{ig_id}")

        assert response.json()["id"] == str(ig_id)
        assert response.status_code == 200
