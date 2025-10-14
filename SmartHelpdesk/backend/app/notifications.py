
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

# Event toggles
ALERT_EVENTS = {e.strip() for e in os.getenv("ALERT_EVENTS", "ticket_created,assignment").split(",") if e.strip()}
ALERT_USER_ON_CREATE = os.getenv("ALERT_USER_ON_CREATE", "true").lower() == "true"
ALERT_USER_ON_ASSIGNMENT = os.getenv("ALERT_USER_ON_ASSIGNMENT", "true").lower() == "true"

def _enabled(event: str) -> bool:
    return event in ALERT_EVENTS

def _console(subject: str, body: str):
    print(f"[ALERT] {subject}\n{body}\n")

def _smtp_send(to_addr: str, subject: str, body: str):
    if not SMTP_HOST or not SMTP_PORT or not to_addr:
        _console(subject, f"TO={to_addr}\n{body}")
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = ALERT_FROM
        msg["To"] = to_addr
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            try:
                server.starttls()
                if SMTP_USER and SMTP_PASS:
                    server.login(SMTP_USER, SMTP_PASS)
            except Exception:
                pass
            server.send_message(msg)
    except Exception as e:
        _console(f"EMAIL SEND FAILED: {subject}", f"TO={to_addr}\n{body}\nError: {e}")

def _send_email(subject: str, body: str):
    # Team/distro alerts (ALERT_TO)
    if ALERT_TO:
        _smtp_send(ALERT_TO, subject, body)
    else:
        _console(subject, body)

def _send_email_to(to_addr: str, subject: str, body: str):
    _smtp_send(to_addr, subject, body)

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
    if not _enabled("ticket_created"):
        return
    subject = f"[Helpdesk] New ticket #{ticket.id} ({ticket.priority}) - {ticket.subject}"
    body = f"Category: {ticket.category}\nTeam: {ticket.assignee_team}\nUser: {ticket.user_email}\n\n{ticket.body}"
    # Team/distro + webhooks
    _send_email(subject, body)
    _send_discord(f"New ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")
    _send_telegram(f"New ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")

def notify_requester_ticket_created(ticket: Ticket):
    # Email requester a confirmation
    if not ALERT_USER_ON_CREATE:
        return
    if not ticket.user_email:
        return
    subject = f"[Helpdesk] Ticket #{ticket.id} created — {ticket.subject}"
    body = (
        f"Hello,\n\nYour ticket has been created.\n"
        f"ID: {ticket.id}\nCategory: {ticket.category}\nTeam: {ticket.assignee_team}\nPriority: {ticket.priority}\n\n"
        f"Details:\n{ticket.body}\n\nWe will keep you updated.\n"
    )
    _send_email_to(ticket.user_email, subject, body)

def notify_assignment(ticket: Ticket):
    if not _enabled("assignment"):
        return
    subject = f"[Helpdesk] Assigned to {ticket.assignee_team} - Ticket #{ticket.id}"
    body = f"Ticket #{ticket.id} assigned to team {ticket.assignee_team} with priority {ticket.priority}."
    _send_email(subject, body)
    _send_discord(f"Assigned: ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}]")
    _send_telegram(f"Assigned: ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}]")

def notify_user_assignment(ticket: Ticket):
    # Notify individual assignee
    if not ALERT_USER_ON_ASSIGNMENT:
        return
    if not ticket.assignee_user:
        return
    subject = f"[Helpdesk] You are assigned — Ticket #{ticket.id}"
    body = f"You have been assigned ticket #{ticket.id} [{ticket.priority}] ({ticket.category}):\n{ticket.subject}\n\n{ticket.body}"
    _send_email_to(ticket.assignee_user, subject, body)