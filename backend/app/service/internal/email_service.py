from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from fastapi import HTTPException
from app.core.config import settings

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: str | None = None
) -> None:
    """
    Send an email using configured SMTP settings
    """
    msg = MIMEMultipart()
    msg['From'] = from_email or settings.SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send email"
        )