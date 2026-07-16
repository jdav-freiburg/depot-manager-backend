from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from depot_server.api2.announcement import router
from depot_server.api2.models.announcement import Announcement


@pytest.fixture
def client():
    """Create a FastAPI test client with the announcement router"""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_announcements_calls_repo(client):
    """Test GET /announcement calls NewsRepo.get_all_announcements"""
    announcement_id = uuid4()
    author = "author"
    now = datetime.now()

    mock_db_announcement = MagicMock()
    mock_db_announcement.pk = announcement_id
    mock_db_announcement.author = author
    mock_db_announcement.title = "Test Announcement"
    mock_db_announcement.text = "This is a test announcement"
    mock_db_announcement.timestamp = now
    mock_db_announcement.expires = now + timedelta(days=7)
    mock_db_announcement.is_visible = True
    mock_db_announcement.is_pinned = False

    with patch("depot_server.api2.announcement.NewsRepo.get_all_announcements", new_callable=AsyncMock) as mock_get_all:
        with patch("depot_server.api2.announcement.announcement_from_orm") as mock_from_orm:
            mock_get_all.return_value = [mock_db_announcement]
            mock_announcement = MagicMock(spec=Announcement)
            mock_from_orm.return_value = mock_announcement

            response = client.get("/announcement")

            # Verify repo method was called
            mock_get_all.assert_called_once()
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1


@pytest.mark.asyncio
async def test_get_announcement_by_id_calls_repo(client):
    """Test GET /announcement/{id} calls NewsRepo.get_announcement_by_id with correct id"""
    announcement_id = uuid4()
    author = "author"
    now = datetime.now()

    mock_db_announcement = MagicMock()
    mock_db_announcement.pk = announcement_id
    mock_db_announcement.author = author
    mock_db_announcement.title = "Single Announcement"
    mock_db_announcement.text = "Single test text"
    mock_db_announcement.timestamp = now
    mock_db_announcement.expires = now + timedelta(days=7)
    mock_db_announcement.is_visible = True
    mock_db_announcement.is_pinned = False

    with patch("depot_server.api2.announcement.NewsRepo.get_announcement_by_id", new_callable=AsyncMock) as mock_get:
        with patch("depot_server.api2.announcement.announcement_from_orm") as mock_from_orm:
            mock_get.return_value = mock_db_announcement
            mock_announcement = MagicMock(spec=Announcement)
            mock_from_orm.return_value = mock_announcement

            response = client.get(f"/announcement/{announcement_id}")

            # Verify repo method was called with correct id
            mock_get.assert_called_once_with(announcement_id)
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_announcement_not_found(client):
    """Test GET /announcement/{id} returns 404 when announcement not found"""
    announcement_id = uuid4()

    with patch("depot_server.api2.announcement.NewsRepo.get_announcement_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/announcement/{announcement_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Announcement not found"


@pytest.mark.asyncio
async def test_create_announcement_calls_repo(client):
    """Test POST /announcement calls NewsRepo.create_announcement with correct parameters"""
    announcement_id = uuid4()
    author = "<user who made the request>"
    now = datetime.now()
    expires = now + timedelta(days=7)

    mock_db_announcement = MagicMock()
    mock_db_announcement.pk = announcement_id
    mock_db_announcement.author = author
    mock_db_announcement.title = "New Announcement"
    mock_db_announcement.text = "New test text"
    mock_db_announcement.timestamp = now
    mock_db_announcement.expires = expires
    mock_db_announcement.is_visible = True
    mock_db_announcement.is_pinned = False

    with patch("depot_server.api2.announcement.NewsRepo.create_announcement", new_callable=AsyncMock) as mock_create:
        with patch("depot_server.api2.announcement.announcement_from_orm") as mock_from_orm:
            mock_create.return_value = mock_db_announcement
            mock_announcement = MagicMock(spec=Announcement)
            mock_from_orm.return_value = mock_announcement

            payload = {
                "title": "New Announcement",
                "text": "New test text",
                "author": "author",
                "expires": expires.isoformat(),
                "is_draft": False,
                "is_pinned": False
            }
            response = client.post("/announcement", json=payload)

            # Verify repo create was called with correct parameters
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["author"] == author
            assert call_kwargs["title"] == "New Announcement"
            assert call_kwargs["text"] == "New test text"

            assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_announcement_calls_repo(client):
    """Test PUT /announcement/{id} calls NewsRepo.update_announcement with correct parameters"""
    announcement_id = uuid4()
    author = "<user who made the request>"
    now = datetime.now()
    expires = now + timedelta(days=14)

    mock_db_announcement = MagicMock()
    mock_db_announcement.pk = announcement_id
    mock_db_announcement.author = author
    mock_db_announcement.title = "Updated Announcement"
    mock_db_announcement.text = "Updated text"
    mock_db_announcement.timestamp = now
    mock_db_announcement.expires = expires
    mock_db_announcement.is_visible = False
    mock_db_announcement.is_pinned = True

    with patch("depot_server.api2.announcement.NewsRepo.update_announcement", new_callable=AsyncMock) as mock_update:
        with patch("depot_server.api2.announcement.announcement_from_orm") as mock_from_orm:
            mock_update.return_value = mock_db_announcement
            mock_announcement = MagicMock(spec=Announcement)
            mock_from_orm.return_value = mock_announcement

            payload = {
                "title": "Updated Announcement",
                "text": "Updated text",
                "author": "author",
                "expires": expires.isoformat(),
                "is_draft": False,
                "is_pinned": True
            }
            response = client.put(f"/announcement/{announcement_id}", json=payload)

            # Verify repo update was called with correct announcement_id and payload
            mock_update.assert_called_once()
            call_args = mock_update.call_args
            assert call_args[0][0] == announcement_id  # First positional arg is announcement_id
            call_kwargs = call_args[1]
            assert call_kwargs["title"] == "Updated Announcement"
            assert call_kwargs["text"] == "Updated text"

            assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_announcement_calls_repo(client):
    """Test DELETE /announcement/{id} calls NewsRepo.delete_announcement with correct id"""
    announcement_id = uuid4()

    with patch("depot_server.api2.announcement.NewsRepo.delete_announcement", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = client.delete(f"/announcement/{announcement_id}")

        # Verify repo delete was called with correct announcement_id
        mock_delete.assert_called_once_with(announcement_id)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_announcement_from_orm_mocked(client):
    """Test that announcement_from_orm is called for response transformation"""
    announcement_id = uuid4()
    author = "author"
    now = datetime.now()

    mock_db_announcement = MagicMock()
    mock_db_announcement.pk = announcement_id
    mock_db_announcement.author = author
    mock_db_announcement.title = "Test Announcement"
    mock_db_announcement.text = "Test text"
    mock_db_announcement.timestamp = now
    mock_db_announcement.expires = now + timedelta(days=7)
    mock_db_announcement.is_visible = True
    mock_db_announcement.is_pinned = False

    with patch("depot_server.api2.announcement.NewsRepo.get_announcement_by_id", new_callable=AsyncMock) as mock_get:
        with patch("depot_server.api2.announcement.announcement_from_orm") as mock_from_orm:
            mock_get.return_value = mock_db_announcement
            mock_announcement = MagicMock(spec=Announcement)
            mock_from_orm.return_value = mock_announcement

            response = client.get(f"/announcement/{announcement_id}")

            # Verify announcement_from_orm was called with the DB object
            mock_from_orm.assert_called_once_with(mock_db_announcement)
            assert response.status_code == 200
