import pytest
from httpx import AsyncClient

CREATED_FRANCHISE_ID = None


@pytest.mark.asyncio
async def test_create_franchise(client: AsyncClient, admin_token: str):
    global CREATED_FRANCHISE_ID
    response = await client.post(
        "/api/v1/franchise",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Alpha Franchise",
            "email": "alpha@franchise.com",
            "password": "Alpha@1234",
            "phone": "8888888888",
            "address": "456 Alpha Road",
            "franchise_code": "ALPHA-001",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["franchise_code"] == "ALPHA-001"
    CREATED_FRANCHISE_ID = data["data"]["id"]


@pytest.mark.asyncio
async def test_create_franchise_duplicate_code(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/franchise",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Beta Franchise",
            "email": "beta@franchise.com",
            "password": "Beta@1234",
            "phone": "7777777777",
            "address": "789 Beta Lane",
            "franchise_code": "ALPHA-001",  
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_franchises(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/v1/franchise?page=1&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert data["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_search_franchise(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/v1/franchise?search=Alpha&page=1&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert any("Alpha" in item["name"] for item in data["data"]["items"])


@pytest.mark.asyncio
async def test_get_franchise_by_id(client: AsyncClient, admin_token: str):
    global CREATED_FRANCHISE_ID
    if not CREATED_FRANCHISE_ID:
        pytest.skip("No franchise created yet")
    response = await client.get(
        f"/api/v1/franchise/{CREATED_FRANCHISE_ID}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == CREATED_FRANCHISE_ID


@pytest.mark.asyncio
async def test_update_franchise(client: AsyncClient, admin_token: str):
    global CREATED_FRANCHISE_ID
    if not CREATED_FRANCHISE_ID:
        pytest.skip("No franchise created yet")
    response = await client.put(
        f"/api/v1/franchise/{CREATED_FRANCHISE_ID}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Alpha Franchise Updated", "phone": "6666666666"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "Alpha Franchise Updated"
    assert data["data"]["franchise_code"] == "ALPHA-001"  # immutable


@pytest.mark.asyncio
async def test_delete_franchise(client: AsyncClient, admin_token: str):
    global CREATED_FRANCHISE_ID
    if not CREATED_FRANCHISE_ID:
        pytest.skip("No franchise created yet")
    response = await client.delete(
        f"/api/v1/franchise/{CREATED_FRANCHISE_ID}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_franchise_cannot_create(client: AsyncClient, franchise_token: str):
    response = await client.post(
        "/api/v1/franchise",
        headers={"Authorization": f"Bearer {franchise_token}"},
        json={
            "name": "Sneaky",
            "email": "sneaky@test.com",
            "password": "Test@1234",
            "phone": "1234567890",
            "address": "Nowhere",
            "franchise_code": "SNKY-001",
        },
    )
    assert response.status_code == 403
