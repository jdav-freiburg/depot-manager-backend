from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from depot_server.api2.models.tag import Tag
from depot_server.api2.tag import router


# Pydantic model tests
@pytest.mark.parametrize(
    "input_color,expected",
    [
        ("#FF00FF", "#ff00ff"),
        ("  #AbCdEf  ", "#abcdef"),
        ("#000000", "#000000"),
    ],
)
def test_color_normalizes_to_lowercase_and_strips(input_color, expected):
    t = Tag(id=uuid4(), name="tag", description="d", color=input_color)
    assert t.color == expected


@pytest.mark.parametrize(
    "bad_color",
    [
        "#GGGGGG",  # invalid hex digits
        "123456",  # missing '#'
        "#FFF",  # wrong length
        "#FFFFF",  # wrong length
        "#12345G",  # invalid char
        "",  # empty
        None,  # null
    ],
)
def test_invalid_colors_raise_validation_error(bad_color):
    with pytest.raises(ValidationError):
        Tag(id=uuid4(), name="tag", description="d", color=bad_color)


# API endpoint tests with mocked repository
@pytest.fixture
def client():
    """Create a FastAPI test client with the tag router"""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_tags_calls_repo_get_all(client):
    """Test GET /tag calls TagRepo.get_all_tags with correct parameters"""
    tag_id = uuid4()
    mock_db_tag = MagicMock()
    mock_db_tag.id = tag_id
    mock_db_tag.name = "test_tag"
    mock_db_tag.description = "test desc"
    mock_db_tag.color = "#abcdef"

    with patch("depot_server.api2.tag.TagRepo.get_all_tags", new_callable=AsyncMock) as mock_get_all:
        mock_get_all.return_value = [mock_db_tag]
        response = client.get("/tag")

        # Verify repo method was called once
        mock_get_all.assert_called_once()
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(tag_id)
        assert data[0]["name"] == "test_tag"


@pytest.mark.asyncio
async def test_get_tag_by_id_calls_repo(client):
    """Test GET /tag/{tag_id} calls TagRepo.get_tag_by_id with correct id"""
    tag_id = uuid4()
    mock_db_tag = MagicMock()
    mock_db_tag.id = tag_id
    mock_db_tag.name = "single_tag"
    mock_db_tag.description = "desc"
    mock_db_tag.color = "#ff0000"

    with patch("depot_server.api2.tag.TagRepo.get_tag_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_db_tag
        response = client.get(f"/tag/{tag_id}")

        # Verify repo method was called with correct tag_id
        mock_get.assert_called_once_with(tag_id)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(tag_id)
        assert data["name"] == "single_tag"


@pytest.mark.asyncio
async def test_get_tag_not_found(client):
    """Test GET /tag/{tag_id} returns 404 when tag not found"""
    tag_id = uuid4()

    with patch("depot_server.api2.tag.TagRepo.get_tag_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get(f"/tag/{tag_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not found"


@pytest.mark.asyncio
async def test_create_tag_calls_repo(client):
    """Test POST /tag calls TagRepo.create_tag with correct parameters"""
    tag_id = uuid4()
    mock_db_tag = MagicMock()
    mock_db_tag.id = tag_id
    mock_db_tag.name = "new_tag"
    mock_db_tag.description = "new desc"
    mock_db_tag.color = "#123456"

    with patch("depot_server.api2.tag.TagRepo.create_tag", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_db_tag

        payload = {"name": "new_tag", "description": "new desc", "color": "#123456"}
        response = client.post("/tag", json=payload)

        # Verify repo create was called with the payload fields
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["name"] == "new_tag"
        assert call_kwargs["description"] == "new desc"
        # color should be normalized to lowercase
        assert call_kwargs["color"] == "#123456"

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "new_tag"


@pytest.mark.asyncio
async def test_update_tag_calls_repo(client):
    """Test PUT /tag/{tag_id} calls TagRepo.update_tag with correct parameters"""
    tag_id = uuid4()
    mock_db_tag = MagicMock()
    mock_db_tag.id = tag_id
    mock_db_tag.name = "updated_tag"
    mock_db_tag.description = "updated desc"
    mock_db_tag.color = "#aabbcc"

    with patch("depot_server.api2.tag.TagRepo.update_tag", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_db_tag

        payload = {"name": "updated_tag", "description": "updated desc", "color": "#AABBCC"}
        response = client.put(f"/tag/{tag_id}", json=payload)

        # Verify repo update was called with correct tag_id and payload
        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == tag_id  # First positional arg is tag_id
        call_kwargs = call_args[1]
        assert call_kwargs["name"] == "updated_tag"
        assert call_kwargs["description"] == "updated desc"
        # Note: color is passed as-is (not normalized by TagPending model)
        assert call_kwargs["color"] == "#AABBCC"

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated_tag"


@pytest.mark.asyncio
async def test_delete_tag_calls_repo(client):
    """Test DELETE /tag/{tag_id} calls TagRepo.delete_tag with correct id"""
    tag_id = uuid4()

    with patch("depot_server.api2.tag.TagRepo.delete_tag", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = client.delete(f"/tag/{tag_id}")

        # Verify repo delete was called with correct tag_id
        mock_delete.assert_called_once_with(tag_id)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_tag_response_normalizes_color(client):
    """Test that Tag response model normalizes colors to lowercase"""
    tag_id = uuid4()
    mock_db_tag = MagicMock()
    mock_db_tag.id = tag_id
    mock_db_tag.name = "color_test"
    mock_db_tag.description = "desc"
    mock_db_tag.color = "#FF00FF"  # Uppercase hex

    with patch("depot_server.api2.tag.TagRepo.get_tag_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_db_tag
        response = client.get(f"/tag/{tag_id}")

        assert response.status_code == 200
        data = response.json()
        # Response model should normalize to lowercase
        assert data["color"] == "#ff00ff"
