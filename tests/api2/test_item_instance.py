from datetime import date
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.item_instance import router
from depot_server.api2.models.item import APIItemInstance
from depot_server.db2.models.common import Condition
from depot_server.logic.item_instance import ItemInstanceUniqueConflict


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def instance_model(instance_id, item_id):
    return APIItemInstance(
        id=instance_id,
        item_id=item_id,
        external_id="EXT-001",
        serial_number="SN001",
        manufacture_date=date(2024, 1, 1),
        purchase_date=date(2024, 2, 1),
        first_use_date=date(2024, 3, 1),
        condition=Condition.GOOD,
    )


def instance_payload(item_id):
    return {
        "item_id": str(item_id),
        "external_id": "EXT-001",
        "serial_number": "SN001",
        "manufacture_date": "2024-01-01",
        "purchase_date": "2024-02-01",
        "first_use_date": "2024-03-01",
        "condition": "good",
        "condition_comment": None,
    }


def test_get_item_instances_calls_repo(client):
    instance_id = uuid4()
    item_id = uuid4()
    with patch("depot_server.api2.item_instance.ItemInstanceRepo.get_all", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [instance_model(instance_id, item_id)]
        response = client.get("/item_instance")

    mock_get.assert_awaited_once_with()
    assert response.status_code == 200
    assert response.json()[0]["id"] == str(instance_id)


def test_get_item_instance_not_found(client):
    instance_id = uuid4()
    with patch("depot_server.api2.item_instance.ItemInstanceRepo.get_full_item", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/item_instance/{instance_id}")

    mock_get.assert_awaited_once_with(instance_id)
    assert response.status_code == 404
    assert response.json()["detail"] == "ItemInstance not found"


def test_create_item_instance_calls_service(client):
    instance_id = uuid4()
    item_id = uuid4()
    with patch("depot_server.api2.item_instance.ItemInstanceService.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = instance_model(instance_id, item_id)
        response = client.post("/item_instance", json=instance_payload(item_id))

    mock_create.assert_awaited_once()
    assert mock_create.call_args.args[0].item_id == item_id
    assert response.status_code == 200
    assert response.json()["id"] == str(instance_id)


def test_update_item_instance_calls_service(client):
    instance_id = uuid4()
    item_id = uuid4()
    result = instance_model(instance_id, item_id)
    with patch("depot_server.api2.item_instance.ItemInstanceRepo.get_by_id", new_callable=AsyncMock, return_value=result), \
            patch("depot_server.api2.item_instance.ItemInstanceRepo.has_colliding_unique", new_callable=AsyncMock, return_value=False), \
            patch("depot_server.api2.item_instance.ItemInstanceRepo.update", new_callable=AsyncMock, return_value=result) as mock_update:
        response = client.put(f"/item_instance/{instance_id}", json=instance_payload(item_id))

    mock_update.assert_awaited_once()
    assert mock_update.call_args.args[0] == instance_id
    assert response.status_code == 200
    assert response.json()["id"] == str(instance_id)


def test_create_item_instance_returns_conflict_for_duplicate(client):
    item_id = uuid4()
    with patch(
        "depot_server.api2.item_instance.ItemInstanceService.create",
        new_callable=AsyncMock,
        side_effect=ItemInstanceUniqueConflict("duplicate instance"),
    ):
        response = client.post("/item_instance", json=instance_payload(item_id))

    assert response.status_code == 409
    assert response.json()["detail"] == "duplicate instance"


def test_expired_route_is_not_parsed_as_uuid(client):
    with patch("depot_server.api2.item_instance.ItemInstanceService.get_expired_item_instances", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        response = client.get("/item_instance/expired")

    mock_get.assert_awaited_once_with()
    assert response.status_code == 200
    assert response.json() == []


def test_delete_item_instance_calls_repo(client):
    instance_id = uuid4()
    with patch("depot_server.api2.item_instance.ItemInstanceRepo.delete_by_id", new_callable=AsyncMock) as mock_delete:
        response = client.delete(f"/item_instance/{instance_id}")

    mock_delete.assert_awaited_once_with(instance_id)
    assert response.status_code == 200