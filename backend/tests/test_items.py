"""Item CRUD endpoint tests."""
import pytest
from app.models.db_models import User


@pytest.mark.asyncio
async def test_create_item(client, db_session):
    # Create a system user for the FK constraint
    user = User(id="system", email="system@test.local", hashed_password="x")
    db_session.add(user)
    await db_session.flush()

    response = await client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "A test item"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_items(client):
    response = await client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_item_not_found(client):
    response = await client.get("/api/v1/items/nonexistent-id")
    assert response.status_code == 404
