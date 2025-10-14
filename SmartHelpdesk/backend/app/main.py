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

# Optional KB (can be disabled by env flags)
KB_DISABLED = os.getenv("DISABLE_KB_INDEX", "false").lower() == "true"
SEED_DISABLED = os.getenv("DISABLE_SEED", "false").lower() == "true"
try:
    if not KB_DISABLED:
        from .knowledge_base import KBEngine
    else:
        KBEngine = None
except Exception as e:
    print("KBEngine import failed:", e)
    KBEngine = None

# Notifications safe import
try:
    from .notifications import (
        notify_ticket_created,
        notify_assignment,
        notify_requester_ticket_created,
        notify_user_assignment,
        notify_requester_assigned,
        notify_contact_requester,
    )
except Exception as e:
    print("Notifications import failed:", e)
    def _noop(*_, **__): pass
    notify_ticket_created = notify_assignment = notify_requester_ticket_created = \
        notify_user_assignment = notify_requester_assigned = notify_contact_requester = _noop

app = FastAPI(title="Smart Helpdesk API", version="0.6.1-vercel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTO_ASSIGN = os.getenv("AUTO_ASSIGN", "false").lower() == "true"
TEAMS_ROSTER_RAW = os.getenv("TEAMS_ROSTER", "")

def parse_roster(raw: str) -> Dict[str, List[str]]:
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
kb_engine = KBEngine() if KBEngine else None

class IngestTicket(BaseModel):
    subject: str
    body: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    channel: str = Field(default="web", description="web|email|glpi|solman|chatbot")
    source_ref: Optional[str] = None
    urgency: Optional[str] = Field(default=None, description="low|medium|high|critical")

class ChatMessage(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None

class UpdateTicket(BaseModel):
    status: Optional[str] = Field(default=None)
    assignee_team: Optional[str] = None
    assignee_user: Optional[str] = None
    priority: Optional[str] = Field(default=None)

@app.on_event("startup")
def on_startup():
    print("Startup: init_db")
    try:
        init_db()
        if kb_engine and not KB_DISABLED:
            db = SessionLocal()
            try:
                existing = db.query(KnowledgeBase).count()
                if existing == 0 and not SEED_DISABLED:
                    seed = [
                        KnowledgeBase(
                            title="Reset Domain Password",
                            content="Use Ctrl+Alt+Del -> Change password. If remote, connect VPN first.",
                            tags="password,account,login"
                        ),
                        KnowledgeBase(
                            title="VPN Access and Setup",
                            content="Install client; use AD credentials; approve MFA.",
                            tags="vpn,remote,mfa"
                        ),
                        KnowledgeBase(
                            title="Outlook Email Configuration",
                            content="Add Account -> Microsoft 365, restart if prompted.",
                            tags="outlook,email,office"
                        ),
                        KnowledgeBase(
                            title="Printer Not Working",
                            content="Check power/network; reinstall driver; use IP printing if needed.",
                            tags="printer,hardware"
                        ),
                    ]
                    db.add_all(seed)
                    db.commit()
                print("Building KB index...")
                kb_engine.build_index(db)
            except Exception as e:
                print("KB init error:", e)
            finally:
                db.close()
        else:
            print("KB disabled.")
    except Exception as e:
        print("Startup error (non-fatal):", e)

@app.get("/ping")
def ping():
    return {"pong": True, "time": datetime.utcnow().isoformat()}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
        "kb_enabled": not KB_DISABLED,
        "seed_disabled": SEED_DISABLED,
        "auto_assign": AUTO_ASSIGN
    }

def apply_historical_prior(db, category: str, current_route: dict, confidence: Optional[float]):
    try:
        row = (
            db.query(Ticket.assignee_team, Ticket.priority, func.count().label("c"))
            .filter(Ticket.category == category, Ticket.assignee_team != None)
            .group_by(Ticket.assignee_team, Ticket.priority)
            .order_by(func.count().desc())
            .first()
        )
        if row and (confidence or 0) < 0.7:
            return {"team": row[0] or current_route["team"], "priority": row[1] or current_route["priority"], "prior_applied": True}
    except Exception as e:
        print("Historical prior error:", e)
    return current_route

def choose_assignee(team: str, ticket_id: int) -> Optional[str]:
    emails = ROSTER.get(team) or []
    if not emails:
        return None
    idx = (ticket_id - 1) % len(emails)
    return emails[idx]

def safe_classify(text: str):
    try:
        return classify_text(text)
    except Exception as e:
        print("Classification error:", e)
        return {"category": "other", "confidence": 0.0, "error": str(e)}

@app.post("/tickets/ingest")
def ingest_ticket(payload: IngestTicket):
    db = SessionLocal()
    try:
        cls = safe_classify(payload.subject + "\n" + payload.body)
        route = route_ticket(cls["category"], payload.urgency, cls.get("confidence"))
        route = apply_historical_prior(db, cls["category"], route, cls.get("confidence"))

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

        if AUTO_ASSIGN:
            assignee = choose_assignee(ticket.assignee_team, ticket.id)
            if assignee:
                ticket.assignee_user = assignee
                db.commit()
                db.refresh(ticket)

        try:
            notify_ticket_created(ticket)
            notify_requester_ticket_created(ticket)
            notify_assignment(ticket)
            notify_user_assignment(ticket)
            notify_requester_assigned(ticket)
        except Exception as e:
            print("Notification error:", e)

        suggestions = []
        if kb_engine and not KB_DISABLED:
            try:
                suggestions = kb_engine.suggest(db, f"{payload.subject} {payload.body}", top_k=3)
            except Exception as e:
                print("KB suggestion error:", e)

        return {
            "ticket": ticket.to_dict(),
            "classification": cls,
            "routing": {
                "team": ticket.assignee_team,
                "priority": ticket.priority,
                "assignee_user": ticket.assignee_user,
                **({"prior_applied": True} if "prior_applied" in route else {})
            },
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
        try:
            if payload.assignee_user is not None and t.assignee_user:
                notify_user_assignment(t)
                notify_requester_assigned(t)
        except Exception as e:
            print("Notification error update:", e)
        return t.to_dict()
    finally:
        db.close()

@app.post("/tickets/{ticket_id}/contact-requester")
def contact_requester(ticket_id: int, message: str = Body(..., embed=True)):
    db = SessionLocal()
    try:
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        try:
            notify_contact_requester(t, message)
        except Exception as e:
            print("Contact requester notification error:", e)
        return {"ok": True}
    finally:
        db.close()

@app.post("/chat")
def chat(payload: ChatMessage):
    text = (payload.message or "").lower().strip()
    def resp(message: str, resolved: bool=False, intent: Optional[str]=None, create_ticket: bool=False):
        return {"response": message, "resolved": resolved, "intent": intent, "create_ticket": create_ticket}

    if any(k in text for k in ["password","reset","forgot"]) and "vpn" not in text:
        return resp("Reset password: Ctrl+Alt+Del -> Change password (VPN first if remote). 'create ticket' to escalate.", True, "password_reset")
    if "vpn" in text:
        return resp("VPN: Install client, AD creds, approve MFA. 'create ticket' to escalate.", True, "vpn_help")
    if any(k in text for k in ["outlook","email","o365"]):
        return resp("Outlook: Add Account -> Microsoft 365. Restart if prompted. 'create ticket' to escalate.", True, "outlook_config")
    if "printer" in text or "print" in text:
        return resp("Printer: Check power/network; reinstall driver; IP printing if discovery fails. 'create ticket' to escalate.", True, "printer_issue")

    if "create ticket" in text or "open ticket" in text:
        fake = IngestTicket(
            subject="Chatbot-created ticket",
            body=payload.message,
            user_email=payload.user_email or "unknown@local",
            user_phone=payload.user_phone,
            channel="chatbot"
        )
        result = ingest_ticket(fake)
        return {"response":"Ticket created from chat.", "resolved":True, "intent":"create_ticket",
                "ticket":result["ticket"], "kb_suggestions":result["kb_suggestions"]}

    return resp("I can help with password, VPN, Outlook, printer. Describe your issue or say 'create ticket'.")

@app.get("/db-test")
def db_test():
    try:
        db = SessionLocal()
        count = db.query(Ticket).count()
        db.close()
        return {"ok": True, "tickets": count}
    except Exception as e:
        return {"ok": False, "error": str(e)}