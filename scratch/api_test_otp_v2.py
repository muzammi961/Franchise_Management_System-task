import httpx
import asyncio

async def test_api_otp():
    # Use 127.0.0.1 to avoid localhost resolution issues on Windows
    url_send = "http://127.0.0.1:8000/api/v1/auth/send-otp"
    data_send = {"email": "tripverse12@gmail.com"}
    
    print(f"Testing POST {url_send}...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url_send, json=data_send, timeout=10.0)
            print(f"Status: {resp.status_code}")
            try:
                print(f"Body: {resp.json()}")
            except:
                print(f"Body (Text): {resp.text}")
        except httpx.ConnectError:
            print("❌ Connection Error: Is the server running on 127.0.0.1:8000?")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_otp())
