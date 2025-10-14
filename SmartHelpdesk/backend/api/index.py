from backend.app.main import app  # FastAPI instance in main.py

# (Optional) Root test route only if main.py does NOT already define "/"
@app.get("/")
def root():
    return {"service": "Smart Help Desk API", "status": "ok"}