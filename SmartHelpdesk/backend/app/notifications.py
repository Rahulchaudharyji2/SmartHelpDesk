import os
import smtplib
from email.mime.text import MIMEText
import requests
from .models import Ticket

# Email config (optional; logs to console if not set)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_TO = os.getenv("ALERT_TO", "")
ALERT_FROM = os.getenv("ALERT_FROM", SMTP_USER or "noreply@localhost")

# Free webhook alerts (optional)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def _console(subject: str, body: str):
    print(f"[ALERT] {subject}\n{body}\n")

def _send_email(subject: str, body: str):
    if not SMTP_HOST or not SMTP_PORT or not ALERT_TO:
        _console(subject, body)
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = ALERT_FROM
        msg["To"] = ALERT_TO
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            try:
                server.starttls()
                if SMTP_USER and SMTP_PASS:
                    server.login(SMTP_USER, SMTP_PASS)
            except Exception:
                pass
            server.send_message(msg)
    except Exception as e:
        _console(f"EMAIL SEND FAILED: {subject}", f"{body}\nError: {e}")

def _send_discord(body: str):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": body}, timeout=10)
    except Exception as e:
        _console("DISCORD SEND FAILED", f"{body}\nError: {e}")

def _send_telegram(body: str):
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": body}, timeout=10)
    except Exception as e:
        _console("TELEGRAM SEND FAILED", f"{body}\nError: {e}")

def notify_ticket_created(ticket: Ticket):
    subject = f"[Helpdesk] New ticket #{ticket.id} ({ticket.priority}) - {ticket.subject}"
    body = f"Category: {ticket.category}\nTeam: {ticket.assignee_team}\nUser: {ticket.user_email}\n\n{ticket.body}"
    _send_email(subject, body)
    _send_discord(f"New ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")
    _send_telegram(f"New ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")

def notify_assignment(ticket: Ticket):
    subject = f"[Helpdesk] Assigned to {ticket.assignee_team} - Ticket #{ticket.id}"
    body = f"Ticket #{ticket.id} assigned to team {ticket.assignee_team} with priority {ticket.priority}."
    _send_email(subject, body)
    _send_discord(f"Assigned: ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}]")
    _send_telegram(f"Assigned: ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}]")