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

# Webhooks (optional)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Twilio SMS (optional)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = [p.strip() for p in os.getenv("TWILIO_TO", "").split(",") if p.strip()]

# Per-assignee phone mapping: "email:phone,email2:phone2"
ASSIGNEE_CONTACTS_RAW = os.getenv("ASSIGNEE_CONTACTS", "")
ASSIGNEE_CONTACTS = {}
for pair in ASSIGNEE_CONTACTS_RAW.split(","):
    pair = pair.strip()
    if not pair or ":" not in pair:
        continue
    email, phone = pair.split(":", 1)
    ASSIGNEE_CONTACTS[email.strip().lower()] = phone.strip()

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
    if ALERT_TO:
        _smtp_send(ALERT_TO, subject, body)
    else:
        _console(subject, body)

def _send_email_to(to_addr: str, subject: str, body: str):
    if to_addr:
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

def _send_sms_to_list(numbers, body: str):
    if not numbers:
        return
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM):
        return
    try:
        from twilio.rest import Client  # lazy import
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        for to in numbers:
            try:
                client.messages.create(from_=TWILIO_FROM, to=to, body=body)
            except Exception as e:
                _console("SMS SEND FAILED (one recipient)", f"TO={to}\n{body}\nError: {e}")
    except Exception as e:
        _console("SMS INIT FAILED", f"{body}\nError: {e}")

def _assignee_phone(email: str) -> str:
    if not email:
        return ""
    return ASSIGNEE_CONTACTS.get(email.strip().lower(), "")

def notify_ticket_created(ticket: Ticket):
    if not _enabled("ticket_created"):
        return
    subject = f"[Helpdesk] New ticket #{ticket.id} ({ticket.priority}) - {ticket.subject}"
    body = f"Category: {ticket.category}\nTeam: {ticket.assignee_team}\nUser: {ticket.user_email or ''} / {ticket.user_phone or ''}\n\n{ticket.body}"
    _send_email(subject, body)
    _send_discord(f"New ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")
    _send_telegram(f"New ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")
    _send_sms_to_list(TWILIO_TO, f"New ticket #{ticket.id}: {ticket.assignee_team} [{ticket.priority}] — {ticket.subject}")

def notify_requester_ticket_created(ticket: Ticket):
    if not ALERT_USER_ON_CREATE or not ticket.user_email:
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
    _send_sms_to_list(TWILIO_TO, f"Assigned: ticket #{ticket.id} → {ticket.assignee_team} [{ticket.priority}]")

def notify_user_assignment(ticket: Ticket):
    if not ALERT_USER_ON_ASSIGNMENT or not ticket.assignee_user:
        return
    subject = f"[Helpdesk] You are assigned — Ticket #{ticket.id}"
    body = f"You have been assigned ticket #{ticket.id} [{ticket.priority}] ({ticket.category}):\n{ticket.subject}\n\n{ticket.body}\nRequester: {ticket.user_email or ''} / {ticket.user_phone or ''}"
    _send_email_to(ticket.assignee_user, subject, body)
    # SMS direct to assignee if mapping present
    phone = _assignee_phone(ticket.assignee_user)
    if phone:
        _send_sms_to_list([phone], f"You are assigned: #{ticket.id} [{ticket.priority}] — {ticket.subject}. Requester: {ticket.user_phone or ticket.user_email or ''}")

def notify_requester_assigned(ticket: Ticket):
    # Inform requester who will contact them
    if not ticket.user_email and not ticket.user_phone:
        return
    contact = ticket.assignee_user or ticket.assignee_team
    subject = f"[Helpdesk] Your ticket #{ticket.id} is assigned"
    body = f"Your ticket #{ticket.id} is assigned to {ticket.assignee_team} ({contact}). They will contact you shortly."
    if ticket.user_email:
        _send_email_to(ticket.user_email, subject, body)
    # SMS to requester if phone present
    if ticket.user_phone:
        _send_sms_to_list([ticket.user_phone], f"Ticket #{ticket.id} assigned to {ticket.assignee_team}. Contact: {contact}")

def notify_contact_requester(ticket: Ticket, message: str):
    # Agent-triggered: reach out to requester via email + SMS (if phone present)
    subject = f"[Helpdesk] Regarding your ticket #{ticket.id}"
    if ticket.user_email:
        _send_email_to(ticket.user_email, subject, message)
    if ticket.user_phone:
        _send_sms_to_list([ticket.user_phone], f"Ticket #{ticket.id}: {message}")