from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.item import router
from depot_server.api2.models.item import FullItem, Item
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import PsaCategory


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def item_model(item_id, group_id):
    return Item(
        id=item_id,
        group_id=group_id,
        lendable=True,
        name="Test Item",
        description="Item description",
        manufacturer="Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
    )


def full_item_model(item_id, group_id, instance_id):
    return FullItem(
        id=item_id,
        group_id=group_id,
        instance_id=instance_id,
        lendable=True,
        name="Test Item",
        description="Item description",
        manufacturer="Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
        external_id="EXT-001",
        serial_number="SN001",
        manufacture_date=datetime(2024, 1, 1),
        purchase_date=datetime(2024, 2, 1),
        first_use_date=datetime(2024, 3, 1),
        condition=Condition.GOOD,
    )


def full_item_payload(group_id):
    return {
        "name": "Test Item",
        "description": "Item description",
        "manufacturer": "Manufacturer",
        "model": "Model X",
        "psa_category": "none",
        "external_id": "EXT-001",
        "serial_number": "SN001",
        "manufacture_date": "2024-01-01T00:00:00",
        "purchase_date": "2024-02-01T00:00:00",
        "first_use_date": "2024-03-01T00:00:00",
        "condition": "good",
        "condition_comment": None,
        "lendable": True,
    }


@pytest.mark.asyncio
async def test_get_items_calls_service(client):
    item_id = uuid4()
    group_id = uuid4()
    with patch("depot_server.api2.item.ItemService.get_all_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [item_model(item_id, group_id)]

        response = client.get("/item")

        mock_get.assert_awaited_once_with()
        assert response.status_code == 200
        assert response.json()[0]["id"] == str(item_id)
        assert response.json()[0]["group_id"] == str(group_id)


@pytest.mark.asyncio
async def test_get_item_not_found(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemService.get_item", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        response = client.get(f"/item/{item_id}")

        mock_get.assert_awaited_once_with(item_id)
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_create_item_calls_service(client):
    item_id = uuid4()
    group_id = uuid4()
    instance_id = uuid4()
    result = full_item_model(item_id, group_id, instance_id)
    with patch("depot_server.api2.item.itemservice.create_item", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = result

        response = client.post("/item", json=full_item_payload(group_id))

        mock_create.assert_awaited_once()
        assert mock_create.call_args.args[0].name == "Test Item"
        assert response.status_code == 200
        assert response.json()["id"] == str(item_id)
        assert response.json()["instance_id"] == str(instance_id)


@pytest.mark.asyncio
async def test_update_item_calls_service(client):
    item_id = uuid4()
    group_id = uuid4()
    result = item_model(item_id, group_id)
    payload = {
        "group_id": str(group_id),
        "lendable": False,
        "name": "Updated Item",
        "description": "Updated description",
        "manufacturer": "New Manufacturer",
        "model": "Model Y",
        "psa_category": "none",
        "change_comment": "Updated item",
    }
    with patch("depot_server.api2.item.ItemService.update_item", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = result

        response = client.put(f"/item/{item_id}", json=payload)

        mock_update.assert_awaited_once()
        assert mock_update.call_args.args[0] == item_id
        assert mock_update.call_args.args[1].name == "Updated Item"
        assert response.status_code == 200
        assert response.json()["id"] == str(item_id)


@pytest.mark.asyncio
async def test_delete_item_calls_repo(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemRepo.delete_item", new_callable=AsyncMock) as mock_delete:
        response = client.delete(f"/item/{item_id}")

        mock_delete.assert_awaited_once_with(item_id)
        assert response.status_code == 200
