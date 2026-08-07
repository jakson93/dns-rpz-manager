import smtplib
from email.mime.text import MIMEText
from typing import Optional

import httpx

from app.core.config import settings


class NotificationService:
    @staticmethod
    async def send_telegram(message: str) -> bool:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            return False

        try:
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": settings.TELEGRAM_CHAT_ID,
                        "text": message,
                        "parse_mode": "HTML",
                    },
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    async def send_teams(message: str) -> bool:
        if not settings.TEAMS_WEBHOOK_URL:
            return False

        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": "DNS RPZ Manager Notification",
                "sections": [
                    {
                        "activityTitle": "DNS RPZ Manager",
                        "activityImage": "https://img.icons8.com/fluency/96/dns.png",
                        "text": message,
                        "markdown": True,
                    }
                ],
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.TEAMS_WEBHOOK_URL,
                    json=payload,
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    async def send_email(message: str, subject: str = "DNS RPZ Manager Notification") -> bool:
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_FROM]):
            return False

        try:
            msg = MIMEText(message, "html")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = settings.SMTP_FROM

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception:
            return False

    @staticmethod
    async def notify_all(message: str) -> dict:
        results = {
            "telegram": await NotificationService.send_telegram(message),
            "teams": await NotificationService.send_teams(message),
            "email": await NotificationService.send_email(message),
        }
        return results


notification_service = NotificationService()
