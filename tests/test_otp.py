import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_otp_success(client: AsyncClient):
    with patch("app.services.otp_service.redis_get", new_callable=AsyncMock) as mock_get, \
         patch("app.services.otp_service.redis_set", new_callable=AsyncMock), \
         patch("app.services.otp_service.redis_incr", new_callable=AsyncMock, return_value=1), \
         patch("app.services.otp_service.redis_expire", new_callable=AsyncMock), \
         patch("app.services.otp_service.send_otp_email", new_callable=AsyncMock) as mock_mail:
        mock_get.return_value = None 

        response = await client.post("/api/v1/auth/send-otp", json={"email": "user@test.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_mail.assert_called_once()


@pytest.mark.asyncio
async def test_send_otp_rate_limit(client: AsyncClient):
    with patch("app.services.otp_service.redis_get", new_callable=AsyncMock, return_value="5"):
        response = await client.post("/api/v1/auth/send-otp", json={"email": "user@test.com"})
        assert response.status_code == 429


@pytest.mark.asyncio
async def test_verify_otp_success(client: AsyncClient):
    with patch("app.services.otp_service.redis_get", new_callable=AsyncMock, return_value="123456"), \
         patch("app.services.otp_service.redis_delete", new_callable=AsyncMock):
        response = await client.post("/api/v1/auth/verify-otp", json={
            "email": "user@test.com",
            "otp": "123456",
        })
        assert response.status_code == 200
        assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_verify_otp_wrong(client: AsyncClient):
    with patch("app.services.otp_service.redis_get", new_callable=AsyncMock, return_value="123456"):
        response = await client.post("/api/v1/auth/verify-otp", json={
            "email": "user@test.com",
            "otp": "000000",
        })
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_otp_expired(client: AsyncClient):
    with patch("app.services.otp_service.redis_get", new_callable=AsyncMock, return_value=None):
        response = await client.post("/api/v1/auth/verify-otp", json={
            "email": "user@test.com",
            "otp": "123456",
        })
        assert response.status_code == 400
