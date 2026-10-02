from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.item import router
from depot_server.api2.models.item import APIItem
from depot_server.db2.models.item.item import PsaCategory


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def item_model(item_id):
    return APIItem(
        id=item_id,
        name="Test Item",
        description="Item description",
        manufacturer="Manufacturer",
        model="Model X",
        psa_category=PsaCategory.NONE,
    )


def item_payload():
    return {
        "name": "Test Item",
        "description": "Item description",
        "manufacturer": "Manufacturer",
        "model": "Model X",
        "psa_category": "none",
    }


def test_get_items_calls_service(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemService.get_all_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [item_model(item_id)]
        response = client.get("/item")

    mock_get.assert_awaited_once_with()
    assert response.status_code == 200
    assert response.json()[0]["id"] == str(item_id)
    assert response.json()[0]["lendables"] == []


def test_get_item_not_found(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemService.get_item", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/item/{item_id}")

    mock_get.assert_awaited_once_with(item_id)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item_calls_service(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemService.create_item", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = item_model(item_id)
        response = client.post("/item", json=item_payload())

    mock_create.assert_awaited_once()
    assert mock_create.call_args.args[0].name == "Test Item"
    assert response.status_code == 200
    assert response.json()["id"] == str(item_id)


def test_update_item_calls_service(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemService.update_item", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = item_model(item_id)
        response = client.put(f"/item/{item_id}", json=item_payload())

    mock_update.assert_awaited_once()
    assert mock_update.call_args.args[0] == item_id
    assert response.status_code == 200
    assert response.json()["id"] == str(item_id)


def test_delete_item_calls_repo(client):
    item_id = uuid4()
    with patch("depot_server.api2.item.ItemRepo.delete_by_id", new_callable=AsyncMock) as mock_delete:
        response = client.delete(f"/item/{item_id}")

    mock_delete.assert_awaited_once_with(item_id)
    assert response.status_code == 200