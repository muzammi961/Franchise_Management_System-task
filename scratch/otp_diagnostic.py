import asyncio
import socket
import sys
from app.utils.otp import generate_otp
from app.utils.smtp import send_otp_email
from app.utils.redis import redis_set, redis_get, redis_delete
from app.core.config import settings

async def test_otp_flow(test_email: str):
    print(f"--- OTP Diagnostic for {test_email} ---")
    
    # 1. Test Redis
    print("Testing Redis storage...")
    try:
        otp_dummy = "123456"
        await redis_set("test_otp", otp_dummy, 60)
        val = await redis_get("test_otp")
        if val == otp_dummy:
            print("[OK] Redis: Working! (Stored and retrieved successfully)")
            await redis_delete("test_otp")
        else:
            print(f"[FAIL] Redis: Value mismatch! Got {val}")
    except Exception as e:
        print(f"[FAIL] Redis: Connection failed! {e}")
        return

    # 2. Test SMTP Connection & Resolution
    print(f"Testing SMTP Resolution for {settings.SMTP_HOST}...")
    try:
        ip = socket.gethostbyname(settings.SMTP_HOST)
        print(f"[OK] SMTP Host: {settings.SMTP_HOST} resolved to {ip}")
    except Exception as e:
        print(f"[FAIL] SMTP Host: Failed to resolve! {e}")
        return

    # 3. Test Email Sending
    print(f"Attempting to send OTP email to {test_email}...")
    try:
        otp = generate_otp()
        # This will actually try to send via the configured SMTP server
        await send_otp_email(test_email, otp)
        print("[OK] SMTP: Email sent successfully! Check your inbox (or spam).")
    except Exception as e:
        print(f"[FAIL] SMTP: Failed to send email! {e}")
        print("\nPossible Causes:")
        print("1. Your SMTP_USERNAME or SMTP_PASSWORD in .env is incorrect.")
        print("2. For Gmail, you MUST use an 'App Password', not your regular login password.")
        print("3. Your firewall might be blocking port 587.")
        print("4. Gmail security settings might be blocking the connection.")

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else settings.SMTP_FROM_EMAIL
    try:
        asyncio.run(test_otp_flow(email))
    except Exception as fatal:
        print(f"Fatal Diagnostic Error: {fatal}")
