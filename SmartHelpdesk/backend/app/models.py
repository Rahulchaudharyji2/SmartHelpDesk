import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# DB URL (SQLite local by default)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db")

# Engine and Session at module level
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), default="web", index=True)
    source_ref = Column(String(100), nullable=True)
    user_email = Column(String(200), nullable=True)
    user_phone = Column(String(30), nullable=True)  # NEW: requester phone
    subject = Column(String(500))
    body = Column(Text)
    category = Column(String(100), index=True)
    priority = Column(String(20), index=True)  # P1..P4
    status = Column(String(20), default="open", index=True)  # open|in_progress|resolved|closed
    assignee_team = Column(String(100), index=True)
    assignee_user = Column(String(100), nullable=True)  # email of assignee

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source,
            "source_ref": self.source_ref,
            "user_email": self.user_email,
            "user_phone": self.user_phone,
            "subject": self.subject,
            "body": self.body,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "assignee_team": self.assignee_team,
            "assignee_user": self.assignee_user
        }

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), index=True)
    content = Column(Text)
    tags = Column(String(300), nullable=True)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "content": self.content, "tags": (self.tags or "").split(",")}

def _ensure_ticket_columns():
    # Minimal migration for SQLite: add user_phone if missing
    try:
        if engine.url.get_backend_name() == "sqlite":
            with engine.connect() as conn:
                rows = conn.exec_driver_sql("PRAGMA table_info(tickets)").fetchall()
                cols = [r[1] for r in rows]
                if "user_phone" not in cols:
                    conn.exec_driver_sql("ALTER TABLE tickets ADD COLUMN user_phone VARCHAR(30)")
    except Exception:
        # Safe to ignore in demo; will still work on fresh DB
        pass

# Call this in app startup to ensure tables and columns exist
def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_ticket_columns()