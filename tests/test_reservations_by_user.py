from datetime import date, timedelta
from fastapi.testclient import TestClient

import depot_server.api.reservations
from depot_server.api import app
from depot_server.helper.auth import Authentication
from depot_server.model import ReservationInWrite, Reservation, BayInWrite, ReportItemInWrite, Item, ReservationType, \
    ReservationItem, ReservationState
from tests.db_helper import clear_all
from tests.mock_auth import MockAuthentication, MockAuth


def test_reservations_by_user_current_user_and_items(monkeypatch, motor_mock):
    monkeypatch.setattr(Authentication, '__call__', MockAuthentication.__call__)

    with TestClient(app) as client:
        clear_all()

        # create bay
        create_bay = BayInWrite(external_id='bay_1', name="Bay 1", description="Top Left")
        resp = client.post('/api/v1/depot/bays', data=create_bay.json(), auth=MockAuth(sub='admin', roles=['admin']))
        assert resp.status_code == 201, resp.text

        # create items
        item_ids = []
        for i in range(2):
            create_item = ReportItemInWrite(
                external_id=f'item_{i}',
                name=f'Item {i}',
                description='x',
                total_report_state=0,
                condition=0,
                condition_comment='c',
                purchase_date=date.today(),
                picture_id=None,
                group_id=f'g{i}',
                tags=[],
                bay_id=resp.json()['id'],
                change_comment='x',
                report_profile_id=None,
                report=[],
            )
            r = client.post('/api/v1/depot/items', data=create_item.json(), auth=MockAuth(sub='admin', roles=['admin']))
            assert r.status_code == 201, r.text
            item_ids.append(r.json()['id'])

        # create reservation for user1
        create_reservation = ReservationInWrite(
            type=ReservationType.PRIVATE,
            name='R1',
            start=date.today() + timedelta(days=1),
            end=date.today() + timedelta(days=2),
            items=item_ids,
        )
        r = client.post('/api/v1/depot/reservations', data=create_reservation.json(), auth=MockAuth(sub='user1'))
        assert r.status_code == 201, r.text

        # create reservation for user2
        create_reservation.user_id = None
        r2 = client.post('/api/v1/depot/reservations', data=create_reservation.json(), auth=MockAuth(sub='user2'))
        assert r2.status_code == 201, r2.text

        # request without user_id should return current user's reservations
        resp = client.get('/api/v1/depot/reservations-by-user', auth=MockAuth(sub='user1'))
        assert resp.status_code == 200, resp.text
        reservations = [Reservation.validate(x) for x in resp.json()]
        assert len(reservations) == 1
        assert reservations[0].user_id == 'user1'
        # items not included by default
        assert 'items' not in resp.json()[0]

        # request with include_items
        resp = client.get('/api/v1/depot/reservations-by-user?include_items=true', auth=MockAuth(sub='user1'))
        assert resp.status_code == 200, resp.text
        reservations = [Reservation.validate(x) for x in resp.json()]
        assert len(reservations) == 1
        assert len(reservations[0].items) == len(item_ids)


def test_reservations_by_user_other_user(monkeypatch, motor_mock):
    monkeypatch.setattr(Authentication, '__call__', MockAuthentication.__call__)

    with TestClient(app) as client:
        clear_all()

        # create minimal data and reservation for user2
        create_bay = BayInWrite(external_id='bay_2', name="Bay 2", description="x")
        resp = client.post('/api/v1/depot/bays', data=create_bay.json(), auth=MockAuth(sub='admin', roles=['admin']))
        assert resp.status_code == 201, resp.text
        create_item = ReportItemInWrite(
            external_id='i1', name='I', description='x', total_report_state=0, condition=0,
            condition_comment='c', purchase_date=date.today(), picture_id=None, group_id='g', tags=[],
            bay_id=resp.json()['id'], change_comment='x', report_profile_id=None, report=[],
        )
        r = client.post('/api/v1/depot/items', data=create_item.json(), auth=MockAuth(sub='admin', roles=['admin']))
        assert r.status_code == 201, r.text
        item_id = r.json()['id']

        create_reservation = ReservationInWrite(
            type=ReservationType.PRIVATE,
            name='R2',
            start=date.today() + timedelta(days=3),
            end=date.today() + timedelta(days=4),
            items=[item_id],
        )
        r = client.post('/api/v1/depot/reservations', data=create_reservation.json(), auth=MockAuth(sub='user2'))
        assert r.status_code == 201, r.text

        # authenticated user1 can fetch reservations of user2 via the path param
        resp = client.get(f"/api/v1/depot/reservations-by-user/user2", auth=MockAuth(sub='user1'))
        assert resp.status_code == 200, resp.text
        reservations = [Reservation.validate(x) for x in resp.json()]
        assert len(reservations) == 1
        assert reservations[0].user_id == 'user2'


def test_reservations_by_user_requires_auth(monkeypatch, motor_mock):
    # Do not set Authentication to Mock; use default which will require auth
    with TestClient(app) as client:
        resp = client.get('/api/v1/depot/reservations-by-user')
        assert resp.status_code == 403
