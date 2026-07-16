from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.models.storage_location import StorageLocation
from depot_server.api2.storage_location import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_storage_locations_calls_repo(client):
    loc_id = uuid4()
    mock_db_loc = MagicMock()
    mock_db_loc.pk = loc_id
    mock_db_loc.name = "Loc A"
    mock_db_loc.description = "Desc A"
    mock_db_loc.map_asset_id = None
    mock_db_loc.is_ausgabepflichtig = False

    model_loc = StorageLocation(id=loc_id, name="Loc A", description="Desc A", map_item=None,
                                is_subject_to_issuance=False)

    with patch("depot_server.api2.storage_location.StorageLocationRepo.Db_type.all",
               new_callable=AsyncMock) as mock_all:
        with patch("depot_server.api2.storage_location.storage_location_from_orm") as mock_from_orm:
            mock_all.return_value = [mock_db_loc]
            mock_from_orm.return_value = model_loc

            response = client.get("/storage_location")

            mock_all.assert_called_once()
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == str(loc_id)
            assert data[0]["name"] == "Loc A"


@pytest.mark.asyncio
async def test_get_storage_location_by_id_calls_repo(client):
    loc_id = uuid4()
    mock_db_loc = MagicMock()
    mock_db_loc.pk = loc_id
    mock_db_loc.name = "Loc B"
    mock_db_loc.description = "Desc B"
    mock_db_loc.map_asset_id = None
    mock_db_loc.is_ausgabepflichtig = True

    model_loc = StorageLocation(id=loc_id, name="Loc B", description="Desc B", map_item=None,
                                is_subject_to_issuance=True)

    with patch("depot_server.api2.storage_location.StorageLocationRepo.get_by_id", new_callable=AsyncMock) as mock_get:
        with patch("depot_server.api2.storage_location.storage_location_from_orm") as mock_from_orm:
            mock_get.return_value = mock_db_loc
            mock_from_orm.return_value = model_loc

            response = client.get(f"/storage_location/{loc_id}")

            mock_get.assert_called_once_with(loc_id)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(loc_id)
            assert data["is_subject_to_issuance"] is True


@pytest.mark.asyncio
async def test_get_storage_location_not_found(client):
    loc_id = uuid4()
    with patch("depot_server.api2.storage_location.StorageLocationRepo.get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/storage_location/{loc_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Storage location not found"


@pytest.mark.asyncio
async def test_create_storage_location_calls_repo(client):
    loc_id = uuid4()
    now = datetime.now()

    mock_db_loc = MagicMock()
    mock_db_loc.pk = loc_id
    mock_db_loc.name = "New Loc"
    mock_db_loc.description = "New Desc"
    mock_db_loc.map_asset_id = None
    mock_db_loc.is_ausgabepflichtig = False

    model_loc = StorageLocation(id=loc_id, name="New Loc", description="New Desc", map_item=None,
                                is_subject_to_issuance=False)

    with patch("depot_server.api2.storage_location.StorageLocationRepo.create", new_callable=AsyncMock) as mock_create:
        with patch("depot_server.api2.storage_location.storage_location_from_orm") as mock_from_orm:
            mock_create.return_value = mock_db_loc
            mock_from_orm.return_value = model_loc

            payload = {"name": "New Loc", "description": "New Desc", "map_item": None, "is_subject_to_issuance": False}
            response = client.post("/storage_location", json=payload)

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["name"] == "New Loc"
            assert call_kwargs["description"] == "New Desc"
            # map_item omitted because None

            assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_storage_location_calls_repo_and_saves(client):
    loc_id = uuid4()
    mock_db_loc = MagicMock()
    mock_db_loc.pk = loc_id
    mock_db_loc.name = "Existing"
    mock_db_loc.description = "Old"
    mock_db_loc.map_asset_id = None
    mock_db_loc.is_ausgabepflichtig = False

    model_loc = StorageLocation(id=loc_id, name="Updated", description="Updated Desc", map_item=None,
                                is_subject_to_issuance=True)

    with patch("depot_server.api2.storage_location.StorageLocationRepo.get_by_id", new_callable=AsyncMock) as mock_get:
        with patch("depot_server.api2.storage_location.StorageLocationRepo.save", new_callable=AsyncMock) as mock_save:
            with patch("depot_server.api2.storage_location.storage_location_from_orm") as mock_from_orm:
                mock_get.return_value = mock_db_loc
                mock_from_orm.return_value = model_loc

                payload = {"name": "Updated", "description": "Updated Desc", "map_item": None,
                           "is_subject_to_issuance": True}
                response = client.put(f"/storage_location/{loc_id}", json=payload)

                mock_get.assert_called_once_with(loc_id)
                # ensure attributes were set on the db object
                assert mock_db_loc.name == "Updated"
                assert mock_db_loc.description == "Updated Desc"
                assert mock_db_loc.is_ausgabepflichtig is True
                mock_save.assert_called_once_with(mock_db_loc)

                assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_storage_location_calls_repo(client):
    loc_id = uuid4()
    with patch("depot_server.api2.storage_location.StorageLocationRepo.delete_by_id",
               new_callable=AsyncMock) as mock_delete:
        response = client.delete(f"/storage_location/{loc_id}")
        mock_delete.assert_called_once_with(loc_id)
        assert response.status_code == 200
