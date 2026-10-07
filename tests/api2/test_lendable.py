from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.lendable import router
from depot_server.logic.results.lendable import LogicLendable


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def lendable_result(lendable_id):
    return LogicLendable(
        id=lendable_id,
        name="Test lendable",
        purposes=[],
        description="A test lendable",
        parent=None,
        ausgabepflichtig=False,
        storage_location_id=None,
        in_limbus=0,
        changed_at=datetime.now(),
    )


def lendable_payload(item_id):
    return {
        "name": "Test lendable",
        "description": "A test lendable",
        "ausgabepflichtig": False,
        "items": {str(item_id): 1},
    }


def test_create_lendable_assigns_items_and_calls_service(client):
    item_id = uuid4()
    lendable_id = uuid4()
    purpose = type("Purpose", (), {"id": uuid4()})()

    with (
        patch("depot_server.api2.lendable.ItemPurposeRepo.create", new_callable=AsyncMock) as create_purpose,
        patch("depot_server.api2.lendable.ItemInstanceRepo.assign_unassigned_to_purpose", new_callable=AsyncMock) as assign,
        patch("depot_server.api2.lendable.LendableService.create", new_callable=AsyncMock) as create_lendable,
        patch("depot_server.api2.lendable.ItemRepo.get_by_id", new_callable=AsyncMock) as get_item,
        patch("depot_server.api2.lendable.ReservationService.get_reserved_lendable_amount", new_callable=AsyncMock) as get_reserved,
        patch("depot_server.api2.lendable.LendableService.get_operational_amount", new_callable=AsyncMock) as get_operational,
        patch("depot_server.api2.lendable.LendableService.get_items", new_callable=AsyncMock) as get_items,
    ):
        create_purpose.return_value = purpose
        create_lendable.return_value = lendable_result(lendable_id)
        get_item.return_value = object()
        get_reserved.return_value = 0
        get_operational.return_value = 0
        get_items.return_value = {}

        response = client.post("/lendable/", json=lendable_payload(item_id))

    assert response.status_code == 200
    assert response.json()["id"] == str(lendable_id)
    create_purpose.assert_awaited_once_with(item_id=item_id)
    assign.assert_awaited_once_with(item_id, purpose)
    assert create_lendable.call_args.args[0].purposes == {purpose.id: 1}


def test_get_lendable_calls_service(client):
    lendable_id = uuid4()

    with (
        patch("depot_server.api2.lendable.LendableService.get_by_id", new_callable=AsyncMock) as get_lendable,
        patch("depot_server.api2.lendable.ReservationService.get_reserved_lendable_amount", new_callable=AsyncMock) as get_reserved,
        patch("depot_server.api2.lendable.LendableService.get_operational_amount", new_callable=AsyncMock) as get_operational,
        patch("depot_server.api2.lendable.LendableService.get_items", new_callable=AsyncMock) as get_items,
    ):
        get_lendable.return_value = lendable_result(lendable_id)
        get_reserved.return_value = 0
        get_operational.return_value = 0
        get_items.return_value = {}
        response = client.get(f"/lendable/{lendable_id}")

    assert response.status_code == 200
    get_lendable.assert_awaited_once()
    assert response.json()["id"] == str(lendable_id)


def test_update_lendable_translates_items_to_purposes(client):
    item_id = uuid4()
    lendable_id = uuid4()
    purpose = type("Purpose", (), {"id": uuid4()})()

    with (
        patch("depot_server.api2.lendable.ItemPurposeRepo.create", new_callable=AsyncMock) as create_purpose,
        patch("depot_server.api2.lendable.ItemInstanceRepo.assign_unassigned_to_purpose", new_callable=AsyncMock),
        patch("depot_server.api2.lendable.LendableService.update", new_callable=AsyncMock) as update_lendable,
        patch("depot_server.api2.lendable.LendableService.get_by_id", new_callable=AsyncMock) as get_lendable,
        patch("depot_server.api2.lendable.ReservationService.get_reserved_lendable_amount", new_callable=AsyncMock) as get_reserved,
        patch("depot_server.api2.lendable.LendableService.get_operational_amount", new_callable=AsyncMock) as get_operational,
        patch("depot_server.api2.lendable.LendableService.get_items", new_callable=AsyncMock) as get_items,
    ):
        create_purpose.return_value = purpose
        update_lendable.return_value = lendable_result(lendable_id)
        get_lendable.return_value = lendable_result(lendable_id)
        get_reserved.return_value = 0
        get_operational.return_value = 0
        get_items.return_value = {}

        response = client.put(
            f"/lendable/{lendable_id}",
            json=lendable_payload(item_id),
        )

    assert response.status_code == 200
    contract = update_lendable.call_args.args[1]
    assert contract.purposes == {purpose.id: 1}


def test_delete_lendable_calls_repo(client):
    lendable_id = uuid4()

    with patch("depot_server.api2.lendable.LendableRepo.delete_by_id", new_callable=AsyncMock) as delete_lendable:
        response = client.delete(f"/lendable/{lendable_id}")

    assert response.status_code == 200
    delete_lendable.assert_awaited_once_with(lendable_id)