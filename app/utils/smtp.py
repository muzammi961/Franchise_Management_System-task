import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


async def send_email(to_email: str, subject: str, html_body: str) -> None:
    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject

    part = MIMEText(html_body, "html")
    message.attach(part)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
    )


async def send_otp_email(to_email: str, otp: str) -> None:
    subject = "Your OTP Code — Franchise Management System"
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
        <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
          <h2 style="color: #333;">Your One-Time Password</h2>
          <p style="color: #555;">Use the OTP below to complete your verification. It expires in <strong>5 minutes</strong>.</p>
          <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #4F46E5; text-align: center; padding: 20px 0;">
            {otp}
          </div>
          <p style="color: #999; font-size: 12px;">If you did not request this OTP, please ignore this email.</p>
        </div>
      </body>
    </html>
    """
    await send_email(to_email, subject, html_body)
