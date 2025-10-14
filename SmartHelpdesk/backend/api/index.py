from backend.app.main import app

# Optional root info route; FastAPI already has /ping /health
@app.get("/")
def root():
    return {"service": "Smart Help Desk API", "status": "ok"}