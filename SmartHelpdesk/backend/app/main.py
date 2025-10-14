import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv()

# Import from models (Base/engine are defined at module level now)
from .models import init_db, SessionLocal, Ticket, KnowledgeBase
from .classifier import classify_text
from .routing import route_ticket
from .knowledge_base import KBEngine
from .notifications import notify_ticket_created, notify_assignment

app = FastAPI(title="Smart Helpdesk MVP (Free Edition)", version="0.4.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kb_engine = KBEngine()

class IngestTicket(BaseModel):
    subject: str
    body: str
    user_email: Optional[str] = None
    channel: str = Field(default="web", description="web|email|glpi|solman|chatbot")
    source_ref: Optional[str] = None
    urgency: Optional[str] = Field(default=None, description="low|medium|high|critical")

class ChatMessage(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_email: Optional[str] = None

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
    # Ensure tables are created
    init_db()

    # Seed KB and build TF-IDF index
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

@app.post("/tickets/ingest")
def ingest_ticket(payload: IngestTicket):
    db = SessionLocal()
    try:
        cls = classify_text(payload.subject + "\n" + payload.body)
        route = route_ticket(cls["category"], payload.urgency, cls.get("confidence"))
        ticket = Ticket(
            created_at=datetime.utcnow(),
            source=payload.channel,
            source_ref=payload.source_ref,
            user_email=payload.user_email,
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

        notify_ticket_created(ticket)
        notify_assignment(ticket)

        suggestions = kb_engine.suggest(db, payload.subject + " " + payload.body, top_k=3)

        return {
            "ticket": ticket.to_dict(),
            "classification": cls,
            "routing": route,
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
        return t.to_dict()
    finally:
        db.close()

@app.post("/chat")
def chat(payload: ChatMessage):
    text = (payload.message or "").lower().strip()

    def resp(message: str, resolved: bool = False, intent: Optional[str] = None, create_ticket: bool = False):
        return {"response": message, "resolved": resolved, "intent": intent, "create_ticket": create_ticket}

    if any(k in text for k in ["password", "reset", "forgot"]) and "vpn" not in text:
        return resp(
            "To reset your domain password: Press Ctrl+Alt+Del -> Change a password. If remote, connect VPN first. If locked, reply 'create ticket' to open one.",
            resolved=True,
            intent="password_reset"
        )

    if "vpn" in text:
        return resp(
            "VPN setup: Install FortiClient/AnyConnect. Login with AD credentials. Approve MFA in your Authenticator app. Reply 'create ticket' for help.",
            resolved=True,
            intent="vpn_help"
        )

    if "outlook" in text or "email" in text or "o365" in text:
        return resp(
            "Outlook config: Open Outlook -> Add Account -> Enter email -> pick Microsoft 365. Restart Outlook if prompted. Reply 'create ticket' if issue persists.",
            resolved=True,
            intent="outlook_config"
        )

    if "printer" in text or "print" in text:
        return resp(
            "Printer fix: Check power/network. Reinstall driver from Company Portal. Use IP printing if needed. Reply 'create ticket' to escalate.",
            resolved=True,
            intent="printer_issue"
        )

    if "create ticket" in text or "open ticket" in text:
        subject = "Chatbot-created ticket"
        body = payload.message
        fake = IngestTicket(subject=subject, body=body, user_email=payload.user_email or "unknown@local", channel="chatbot")
        result = ingest_ticket(fake)
        return {
            "response": "Ticket created from chat.",
            "resolved": True,
            "intent": "create_ticket",
            "ticket": result["ticket"],
            "kb_suggestions": result["kb_suggestions"]
        }

    return resp("I can help with password reset, VPN, Outlook, or printer. Type your issue or say 'create ticket'.")