"""
BrainFeed Python Backend — FastAPI Application Entry Point
"""
import os
import sys

# Add parent directory to path so we can import backend package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime

from backend.db.database import init_db, SessionLocal
from backend.db.seed import seed
from backend.db.seed import seed
from backend.routes import auth, questions, analytics, sessions, events

app = FastAPI(title="BrainFeed", description="Intelligent Learning Platform with ML-powered personalization")

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Error handler to match frontend (data.error vs data.detail) ----------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return { error: ... } instead of { detail: ... } to match JS frontend."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid request data", "details": str(exc)}
    )


# ---------- Database init & seed ----------
@app.on_event("startup")
def startup_event():
    """Initialize DB and seed on startup."""
    init_db()
    db = SessionLocal()
    try:
        seed(db)
        print("[Server] Database initialized and seeded.")
    finally:
        db.close()


# ---------- Mount API routes ----------
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ---------- Serve static frontend files ----------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount specific subdirectories FIRST (before catch-all)
# These use absolute paths from root: /asset/..., /Pages/...
asset_dir = os.path.join(PROJECT_ROOT, "asset")
pages_dir = os.path.join(PROJECT_ROOT, "Pages")

if os.path.isdir(asset_dir):
    app.mount("/asset", StaticFiles(directory=asset_dir), name="asset")
    print(f"[Static] Mounted /asset → {asset_dir}")

if os.path.isdir(pages_dir):
    app.mount("/Pages", StaticFiles(directory=pages_dir, html=True), name="pages")
    print(f"[Static] Mounted /Pages → {pages_dir}")


# Root index.html — serve explicitly for "/"
@app.get("/")
async def serve_index():
    index_path = os.path.join(PROJECT_ROOT, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "BrainFeed API is running. No index.html found."}


# Fallback: serve any remaining root-level files (like other static assets)
if os.path.isdir(PROJECT_ROOT):
    app.mount("/", StaticFiles(directory=PROJECT_ROOT), name="root_static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))  # Render sets PORT, default to 10000 if not found
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
