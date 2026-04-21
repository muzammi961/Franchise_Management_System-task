import httpx
import asyncio

async def test_api_otp():
    url_send = "http://localhost:8000/api/v1/auth/send-otp"
    data_send = {"email": "tripverse12@gmail.com"}
    
    print(f"Testing POST {url_send}...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url_send, json=data_send)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.json()}")
        except Exception as e:
            print(f"Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_otp())
