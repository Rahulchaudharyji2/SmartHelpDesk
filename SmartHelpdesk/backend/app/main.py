import os
from datetime import datetime
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func

from dotenv import load_dotenv
load_dotenv()

from .models import init_db, SessionLocal, Ticket, KnowledgeBase
from .classifier import classify_text
from .routing import route_ticket
from .knowledge_base import KBEngine
from .notifications import (
    notify_ticket_created,
    notify_assignment,
    notify_requester_ticket_created,
    notify_user_assignment,
    notify_requester_assigned,
    notify_contact_requester,
)
from fastapi import FastAPI
app = FastAPI()
# ... routes ...
app = FastAPI(title="Smart Helpdesk MVP (Free Edition)", version="0.6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-assign config
AUTO_ASSIGN = os.getenv("AUTO_ASSIGN", "false").lower() == "true"
TEAMS_ROSTER_RAW = os.getenv("TEAMS_ROSTER", "")

def parse_roster(raw: str) -> Dict[str, List[str]]:
    # Format: "Network:a@x.com,b@y.com;Messaging:c@z.com"
    roster = {}
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        team, emails = chunk.split(":", 1)
        emails_list = [e.strip() for e in emails.split(",") if e.strip()]
        if emails_list:
            roster[team.strip()] = emails_list
    return roster

ROSTER = parse_roster(TEAMS_ROSTER_RAW)
kb_engine = KBEngine()

class IngestTicket(BaseModel):
    subject: str
    body: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None  # NEW: requester phone
    channel: str = Field(default="web", description="web|email|glpi|solman|chatbot")
    source_ref: Optional[str] = None
    urgency: Optional[str] = Field(default=None, description="low|medium|high|critical")

class ChatMessage(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None

class UpdateTicket(BaseModel):
    status: Optional[str] = Field(default=None, description="open|in_progress|resolved|closed")
    assignee_team: Optional[str] = None
    assignee_user: Optional[str] = None
    priority: Optional[str] = Field(default=None, description="P1|P2|P3|P4")

class KBIndexItem(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class KBQuery(BaseModel):
    text: str
    top_k: int = 3

@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(KnowledgeBase).count()
        if existing == 0:
            seed = [
                KnowledgeBase(
                    title="Reset Domain Password",
                    content="Use Ctrl+Alt+Del -> Change a password. If offsite, connect via VPN first. If locked, contact IT.",
                    tags="password,account,login"
                ),
                KnowledgeBase(
                    title="VPN Access and Setup",
                    content="Install FortiClient/AnyConnect. Use your AD credentials. For MFA, approve push in Authenticator.",
                    tags="vpn,remote,mfa"
                ),
                KnowledgeBase(
                    title="Outlook Email Configuration",
                    content="Open Outlook -> Add Account -> Enter email -> Choose Microsoft 365. Restart Outlook if prompted.",
                    tags="outlook,email,office"
                ),
                KnowledgeBase(
                    title="Printer Not Working",
                    content="Check power and network. Reinstall driver from Company Portal. Use IP printing if auto-discovery fails.",
                    tags="printer,hardware"
                ),
            ]
            db.add_all(seed)
            db.commit()
        kb_engine.build_index(db)
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

def apply_historical_prior(db, category: str, current_route: dict, confidence: Optional[float]):
    try:
        row = (
            db.query(Ticket.assignee_team, Ticket.priority, func.count().label("c"))
            .filter(Ticket.category == category, Ticket.assignee_team != None)  # noqa: E711
            .group_by(Ticket.assignee_team, Ticket.priority)
            .order_by(func.count().desc())
            .first()
        )
        if row and (confidence or 0) < 0.7:
            team = row[0] or current_route["team"]
            priority = row[1] or current_route["priority"]
            return {"team": team, "priority": priority}
    except Exception:
        pass
    return current_route

def choose_assignee(team: str, ticket_id: int) -> Optional[str]:
    emails = ROSTER.get(team) or []
    if not emails:
        return None
    idx = (ticket_id - 1) % len(emails)
    return emails[idx]

@app.post("/tickets/ingest")
def ingest_ticket(payload: IngestTicket):
    db = SessionLocal()
    try:
        # Classify and route
        cls = classify_text(payload.subject + "\n" + payload.body)
        route = route_ticket(cls["category"], payload.urgency, cls.get("confidence"))
        route = apply_historical_prior(db, cls["category"], route, cls.get("confidence"))

        # Create ticket
        ticket = Ticket(
            created_at=datetime.utcnow(),
            source=payload.channel,
            source_ref=payload.source_ref,
            user_email=payload.user_email,
            user_phone=payload.user_phone,
            subject=payload.subject,
            body=payload.body,
            category=cls["category"],
            priority=route["priority"],
            status="open",
            assignee_team=route["team"],
            assignee_user=None
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Optional auto-assign to an individual
        if AUTO_ASSIGN:
            assignee = choose_assignee(ticket.assignee_team, ticket.id)
            if assignee:
                ticket.assignee_user = assignee
                db.commit()
                db.refresh(ticket)

        # Notifications
        notify_ticket_created(ticket)               # Team/distro + webhooks + SMS list
        notify_requester_ticket_created(ticket)     # Requester confirmation (email)
        notify_assignment(ticket)                   # Team assignment alert
        notify_user_assignment(ticket)              # Individual assignee email + SMS
        notify_requester_assigned(ticket)           # Requester told who will contact them

        # KB suggestions
        suggestions = kb_engine.suggest(db, payload.subject + " " + payload.body, top_k=3)

        return {
            "ticket": ticket.to_dict(),
            "classification": cls,
            "routing": {"team": ticket.assignee_team, "priority": ticket.priority, "assignee_user": ticket.assignee_user},
            "kb_suggestions": suggestions
        }
    finally:
        db.close()

@app.get("/tickets")
def list_tickets(limit: int = 50, offset: int = 0, status: Optional[str] = None):
    db = SessionLocal()
    try:
        q = db.query(Ticket)
        if status:
            q = q.filter(Ticket.status == status)
        q = q.order_by(Ticket.created_at.desc()).offset(offset).limit(limit)
        return [t.to_dict() for t in q.all()]
    finally:
        db.close()

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return t.to_dict()
    finally:
        db.close()

@app.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, payload: UpdateTicket):
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if payload.status:
            t.status = payload.status
        if payload.assignee_team:
            t.assignee_team = payload.assignee_team
        if payload.assignee_user is not None:
            t.assignee_user = payload.assignee_user
        if payload.priority:
            t.priority = payload.priority
        db.commit()
        db.refresh(t)
        # If assignee changed, notify them and requester
        if payload.assignee_user is not None and t.assignee_user:
            notify_user_assignment(t)
            notify_requester_assigned(t)
        return t.to_dict()
    finally:
        db.close()

@app.post("/tickets/{ticket_id}/contact-requester")
def contact_requester(ticket_id: int, message: str = Body(..., embed=True)):
    # Agent-triggered: send message to requester via email + SMS (if phone present)
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        notify_contact_requester(t, message)
        return {"ok": True}
    finally:
        db.close()

@app.post("/chat")
def chat(payload: ChatMessage):
    text = (payload.message or "").lower().strip()

    def resp(message: str, resolved: bool = False, intent: Optional[str] = None, create_ticket: bool = False):
        return {"response": message, "resolved": resolved, "intent": intent, "create_ticket": create_ticket}

    if any(k in text for k in ["password", "reset", "forgot"]) and "vpn" not in text:
        return resp("To reset your domain password: Press Ctrl+Alt+Del -> Change a password. If remote, connect VPN first. If locked, reply 'create ticket' to open one.", True, "password_reset")
    if "vpn" in text:
        return resp("VPN setup: Install FortiClient/AnyConnect. Login with AD credentials. Approve MFA in your Authenticator app. Reply 'create ticket' for help.", True, "vpn_help")
    if "outlook" in text or "email" in text or "o365" in text:
        return resp("Outlook config: Open Outlook -> Add Account -> Enter email -> pick Microsoft 365. Restart Outlook if prompted. Reply 'create ticket' if issue persists.", True, "outlook_config")
    if "printer" in text or "print" in text:
        return resp("Printer fix: Check power/network. Reinstall driver from Company Portal. Use IP printing if needed. Reply 'create ticket' to escalate.", True, "printer_issue")

    if "create ticket" in text or "open ticket" in text:
        fake = IngestTicket(subject="Chatbot-created ticket", body=payload.message, user_email=payload.user_email or "unknown@local", user_phone=payload.user_phone, channel="chatbot")
        result = ingest_ticket(fake)
        return {"response": "Ticket created from chat.", "resolved": True, "intent": "create_ticket", "ticket": result["ticket"], "kb_suggestions": result["kb_suggestions"]}

    return resp("I can help with password reset, VPN, Outlook, or printer. Type your issue or say 'create ticket'.")