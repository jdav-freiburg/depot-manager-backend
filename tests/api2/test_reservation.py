from datetime import date
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.reservation import router
from depot_server.db2.models.common import ReservationImportance, ReservationType
from depot_server.db2.repository.base import ItemNotFound
from depot_server.logic.results.reservation import LogicFullReservation, LogicReservationLendableLink


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def reservation_model(reservation_id, user_id, lendable_id):
    return LogicFullReservation(
        id=reservation_id,
        user_id=user_id,
        name="Test reservation",
        collector=None,
        user_notes=None,
        contact="test@example.com",
        start=date(2026, 1, 1),
        end=date(2026, 1, 3),
        team_id=None,
        reservation_type=ReservationType.BORROW,
        importance=ReservationImportance.TEAM,
        links=[LogicReservationLendableLink(
            id=uuid4(),
            lendable_id=lendable_id,
            amount=2,
            missing_amount=None,
            returned_amount=None,
            borrowed=None,
            borrowed_message=None,
            returned=None,
            returned_message=None,
        )],
    )


def reservation_payload(lendable_id):
    return {
        "name": "Test reservation",
        "start": "2026-01-01",
        "end": "2026-01-03",
        "type": "borrow",
        "importance": "team",
        "team_id": None,
        "contact": "test@example.com",
        "user_notes": None,
        "items": {str(lendable_id): 2},
        "composite_items": {},
    }


def test_get_reservations_by_user_is_not_shadowed(client):
    user_id = uuid4()
    reservation = reservation_model(uuid4(), user_id, uuid4())
    with patch("depot_server.api2.reservation.ReservationService.get_reservations_by_user", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [reservation]
        response = client.get(f"/reservation/user/{user_id}")

    mock_get.assert_awaited_once_with(user_id)
    assert response.status_code == 200
    assert response.json()[0]["id"] == str(reservation.id)
    assert response.json()[0]["items"] == {str(reservation.links[0].lendable_id): 2}


def test_create_reservation_translates_api_model_to_contract(client):
    user_id = uuid4()
    lendable_id = uuid4()
    reservation = reservation_model(uuid4(), user_id, lendable_id)
    with patch("depot_server.api2.reservation.ReservationService.create_reservation", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = reservation
        response = client.post("/reservation/", json=reservation_payload(lendable_id))

    mock_create.assert_awaited_once()
    contract = mock_create.call_args.args[0]
    assert contract.user is not None
    assert contract.user != user_id
    assert contract.lendables == {lendable_id: 2}
    assert response.status_code == 200
    assert response.json()["id"] == str(reservation.id)


def test_get_reservation_not_found(client):
    reservation_id = uuid4()
    with patch(
        "depot_server.api2.reservation.ReservationService.get_reservation",
        new_callable=AsyncMock,
        side_effect=ItemNotFound("missing"),
    ) as mock_get:
        response = client.get(f"/reservation/{reservation_id}")

    mock_get.assert_awaited_once_with(reservation_id)
    assert response.status_code == 404