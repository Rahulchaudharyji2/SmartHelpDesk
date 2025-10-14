from backend.app.main import app

# Optional root override (FastAPI already has /ping /health)
@app.get("/")
def root_info():
    return {"service": "Smart Help Desk API", "status": "ok"}