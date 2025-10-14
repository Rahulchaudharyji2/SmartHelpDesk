# Smart Helpdesk MVP (POWERGRID SIH) — Free/Open Source Prototype

A centralized, AI-assisted helpdesk prototype that unifies ticket intake (web, chat, email), auto-classifies issues, routes to the right team, suggests knowledge base articles, and sends alerts via free channels. Built to match the SIH problem statement and to be easy for others to run locally.

- Unified ingestion: web form, chatbot, optional IMAP email poller
- Automated classification: lightweight rule-based NLP (no paid APIs)
- Intelligent routing: category → team + priority
- Self-service chatbot: password reset, VPN, Outlook, printer + “create ticket”
- Knowledge base suggestions: TF‑IDF (offline, fast)
- Alerts: console logs by default; optional Discord/Telegram webhooks; optional local email via smtp4dev/MailHog
- Admin-lite: update ticket status/assignee/priority via API

## Tech stack

- Backend: FastAPI (Python), SQLAlchemy, SQLite
- NLP: Rule-based keywords, scikit-learn TF‑IDF for KB suggestions
- Frontend: Plain HTML + JS (responsive, mobile-friendly)
- Notifications: Console, Discord/Telegram (free), optional local SMTP
- Email ingestion: IMAP poller script (optional)

---

## Repository structure

```
.
├─ backend/
│  ├─ app/
│  │  ├─ main.py                 # FastAPI app (APIs, chatbot)
│  │  ├─ models.py               # SQLAlchemy models + DB init
│  │  ├─ classifier.py           # Rule-based ticket classifier
│  │  ├─ routing.py              # Category → team + priority mapping
│  │  ├─ knowledge_base.py       # TF‑IDF KB engine
│  │  └─ notifications.py        # Console/Discord/Telegram/SMTP alerts
│  └─ tools/
│     └─ imap_ingest.py          # Optional IMAP poller → /tickets/ingest
├─ frontend/
│  └─ index.html                 # Single page UI (tickets + chatbot)
├─ .env.example                  # Copy to .env and edit as needed
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## Quick start (Windows, macOS, Linux)

### 1) Prerequisites

- Python 3.10+ installed
- pip available
- VS Code recommended (with “Python” extension)
- Optional (free):
  - Discord account to use a webhook for alerts
  - Telegram to use a bot for alerts
  - smtp4dev (Windows) or MailHog (Docker) to preview emails locally

### 2) Clone and set up

```bash
git clone https://github.com/<your-org-or-username>/<your-repo>.git
cd <your-repo>
```

Create a virtual environment and activate it:

- Windows PowerShell
  ```powershell
  python -m venv .venv
  # If activation is blocked once, run:
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  .venv\Scripts\Activate.ps1
  ```

- macOS/Linux
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Configure environment

Copy the example env file and edit it as needed:

```bash
# Windows
copy .env.example .env
# macOS/Linux
cp .env.example .env
```

You can run with everything empty. Alerts will log to the console by default.

Key environment variables:

| Variable | Required | Default | Description |
|---|---|---:|---|
| DATABASE_URL | No | sqlite:///./helpdesk.db | SQLite DB path/URL |
| SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS | No | — | Optional local email (smtp4dev/MailHog); if blank, alerts print to console |
| ALERT_TO / ALERT_FROM | No | — | Email To/From when SMTP is set |
| DISCORD_WEBHOOK_URL | No | — | If set, alerts also post to Discord channel |
| TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID | No | — | If set, alerts also send to Telegram |
| IMAP_HOST/PORT/USER/PASS/MAILBOX/POLL_SECONDS | No | — | Optional: email ingestion poller config |
| HOST / PORT | No | 0.0.0.0 / 8000 | Backend address/port (used by IMAP poller) |

Examples:
- smtp4dev (free local email): `SMTP_HOST=localhost`, `SMTP_PORT=1025`
- Discord: set `DISCORD_WEBHOOK_URL` to your channel’s webhook URL
- Telegram: set bot token and chat id

### 4) Run the backend

```bash
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Check:
- Health: http://localhost:8000/health
- API docs (Swagger): http://localhost:8000/docs

On first run, tables and seed KB articles are created automatically.

### 5) Open the frontend

Option A: Open this file directly in a browser:
- `frontend/index.html`

Option B: Serve statically:
```bash
python -m http.server 5173 --directory frontend
# Then open http://localhost:5173
```

---

## How to use

### A) Create a ticket from the UI
- Open the form in the web page
- Fill Subject, Description, optionally your email and urgency
- Submit and view:
  - Auto category
  - Routed team
  - Priority
  - KB suggestions

### B) Chatbot (self-service + ticket creation)
- Try these messages:
  - “I forgot my password”
  - “VPN not connecting”
  - “Outlook not syncing”
  - “Printer jam”
- Type “create ticket” to open a ticket from chat context

### C) List and update tickets (API)
- List tickets:
  - GET http://localhost:8000/tickets
- Update a ticket (status/assignee/priority):
  - PATCH http://localhost:8000/tickets/{id}
  - Example body:
    ```json
    {
      "status": "in_progress",
      "assignee_user": "tech.user",
      "priority": "P2"
    }
    ```

### D) Create a ticket via API (example body)
Use Swagger at http://localhost:8000/docs or send JSON:

```json
{
  "subject": "VPN keeps disconnecting; MFA not prompted",
  "body": "Remote work, FortiClient drops after 2 mins, MFA not showing",
  "user_email": "user@example.com",
  "channel": "web",
  "urgency": "high"
}
```

### E) Knowledge Base indexing and suggestions (advanced)
- Add articles:
  - POST /kb/index with:
    ```json
    [
      {
        "title": "New KB Title",
        "content": "Step-by-step resolution...",
        "tags": ["tag1", "tag2"]
      }
    ]
    ```
- Ask for suggestions:
  - POST /kb/suggest with:
    ```json
    { "text": "My Outlook is stuck on updating inbox", "top_k": 3 }
    ```

---

## Optional integrations (free)

- Discord Webhook alerts:
  1) Channel → Integrations → Webhooks → New Webhook → Copy URL
  2) Set `DISCORD_WEBHOOK_URL` in `.env`
  3) Restart backend

- Telegram Bot alerts:
  1) Create bot with @BotFather → get token
  2) Start a chat with your bot
  3) Get your chat_id: open in browser `https://api.telegram.org/bot<token>/getUpdates`
  4) Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
  5) Restart backend

- Local email preview (smtp4dev):
  1) Install/run smtp4dev (Windows) or MailHog (Docker)
  2) Set in `.env`: `SMTP_HOST=localhost`, `SMTP_PORT=1025`, `ALERT_TO=dev@example.com`
  3) View emails at smtp4dev UI or MailHog UI

- Email ingestion (IMAP):
  1) Fill `IMAP_*` settings in `.env`
  2) Run poller:
     ```bash
     python backend/tools/imap_ingest.py
     ```
  3) New unseen emails → POST /tickets/ingest → tickets created

---

## Demo script (7–10 minutes)

1) Show health at http://localhost:8000/health and Swagger at /docs
2) Create: “VPN keeps disconnecting; MFA not prompted”
   - Show: category vpn → team Network → priority P2 → KB suggestion “VPN Access and Setup”
3) Chat: “I forgot my password”
   - Show self-service steps → type “create ticket” → ticket created
4) Create: “Outlook not syncing”
   - category email_outlook → team Messaging → priority P3 → KB suggestion
5) Show “Recent Tickets” in UI
6) Update a ticket status to `in_progress` via PATCH (Swagger)
7) Show console logs (and Discord/Telegram if configured)

---

## Troubleshooting

- PowerShell won’t activate venv:
  - Run once: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Port already in use:
  - Change to a free port: `--port 8080` and update HOST/PORT for IMAP poller if used
- CORS or network errors from frontend:
  - Ensure backend: http://localhost:8000 is running
  - Frontend uses fetch to `http://localhost:8000`
- scikit-learn install errors (Windows):
  - `pip install --upgrade pip`
  - Make sure 64-bit Python is installed
- SQLite file on OneDrive path:
  - OneDrive can lock files; if you see DB lock errors, move the project outside OneDrive or change `DATABASE_URL` to an absolute path outside OneDrive (e.g., `sqlite:///C:/dev/helpdesk.db`)
- “Base not defined” error:
  - Ensure you have the provided `models.py` where `Base`, `engine`, and `SessionLocal` are defined at module level and `init_db()` calls `Base.metadata.create_all(bind=engine)`.

---

## Roadmap (nice-to-have)

- Role-based UI (Agent vs Requester)
- SLA timers and alerts
- Tagging and analytics dashboard
- Connectors for GLPI/Solman (map payload → /tickets/ingest)
- Switch to PostgreSQL for multi-user demo

---

## Contributing

- Fork, create a feature branch, and submit a PR
- Please include a short demo video or screenshots for UI changes

---

## License

Add your preferred license (e.g., MIT) as a LICENSE file in the repo.

---
