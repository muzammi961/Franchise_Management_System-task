import socket
import asyncio
import redis.asyncio as aioredis
from app.core.config import settings

async def diagnostic():
    print("--- Diagnostic Report ---")

    print(f"Database URL: {settings.DATABASE_URL}")
    
    print(f"Testing Redis connection at {settings.REDIS_URL}...")
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        print("✅ Redis: Connected!")
    except Exception as e:
        print(f"❌ Redis: Failed to connect! ({e})")
        print("   TIP: Make sure Redis is installed and running on your machine.")

    print(f"Testing SMTP Host resolving for: {settings.SMTP_HOST}...")
    try:
        socket.gethostbyname(settings.SMTP_HOST)
        print(f"✅ SMTP Host: {settings.SMTP_HOST} resolved successfully!")
    except Exception as e:
        print(f"❌ SMTP Host: Failed to resolve '{settings.SMTP_HOST}'! ({e})")
        if "@" in settings.SMTP_HOST:
            print("   ERROR: You have put an EMAIL address in SMTP_HOST. Use 'smtp.gmail.com' instead.")

if __name__ == "__main__":
    asyncio.run(diagnostic())
