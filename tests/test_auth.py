import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_super_admin_login_success(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["role"] == "SUPER_ADMIN"


@pytest.mark.asyncio
async def test_franchise_login_success(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "franchise@test.com",
        "password": "Franchise@1234",
        "franchise_code": "FRAN-TEST-001",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["role"] == "FRANCHISE"


@pytest.mark.asyncio
async def test_franchise_login_without_code_fails(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "franchise@test.com",
        "password": "Franchise@1234",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_franchise_login_wrong_code_fails(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "franchise@test.com",
        "password": "Franchise@1234",
        "franchise_code": "WRONG-CODE",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "WrongPassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    refresh_token = login_resp.json()["data"]["refresh_token"]

    response = await client.post("/api/v1/auth/refresh-token", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
