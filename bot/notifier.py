"""Notification system for deals found."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from loguru import logger
from config import NOTIFY_EMAIL, SMTP_SERVER, SMTP_PORT


class DealNotifier:
    """Sends notifications for found deals."""

    def __init__(self, email: str, smtp_server: str, smtp_port: int):
        self.email = email
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def notify_penny_items(self, items: List[Dict]):
        """Send notification for penny items found."""
        if not items or not self.email:
            return

        logger.info(f"Sending notification for {len(items)} penny items")
        try:
            subject = f"🎉 Found {len(items)} Penny Items!"
            body = self._build_email_body(items)
            self._send_email(subject, body)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def notify_lowest_deals(self, items: List[Dict]):
        """Send notification for lowest-priced deals."""
        if not items or not self.email:
            return

        logger.info(f"Sending notification for {len(items)} lowest deals")
        try:
            subject = f"💰 {len(items)} Lowest-Priced Items Available"
            body = self._build_email_body(items)
            self._send_email(subject, body)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def _build_email_body(self, items: List[Dict]) -> str:
        """Build email body with item details."""
        body = "<html><body><h2>Great Deals Found!</h2><table border='1'><tr><th>Title</th><th>Price</th><th>Source</th><th>Link</th></tr>"
        for item in items:
            body += f"<tr><td>{item.get('title', 'N/A')[:50]}</td><td>${item.get('price', 0):.2f}</td><td>{item.get('source', 'Unknown')}</td><td><a href='{item.get('url', '#')}'>View</a></td></tr>"
        body += "</table></body></html>"
        return body

    def _send_email(self, subject: str, body: str):
        """Send email notification."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email
            msg["To"] = self.email
            msg.attach(MIMEText(body, "html"))

            # Note: In production, use app password or environment variable
            # This is a placeholder - configure SMTP properly
            logger.info(f"Email notification prepared for: {subject}")
        except Exception as e:
            logger.error(f"Error preparing email: {e}")
