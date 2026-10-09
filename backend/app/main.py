import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure backend directory is in sys.path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.init_db import init_db
from app.api.router import api_router

# Resolve the frontend dist directory (built React app)
_root = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = _root / "frontend" / "dist"
if not FRONTEND_DIST.exists():
    FRONTEND_DIST = Path("frontend/dist").resolve()
if not FRONTEND_DIST.exists():
    FRONTEND_DIST = Path("../frontend/dist").resolve()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Idempotent DB initialization on startup
    init_db()
    yield

app = FastAPI(
    title="SafePlate API",
    description="AI meal planning built around what YOU can safely eat. Local-first food safety and agentic optimization.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global sanitized exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log details on server for debugging
    print(f"[Internal Server Error on {request.method} {request.url.path}]: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Something went wrong while processing your request. Please try again or adjust your constraints.",
            "type": exc.__class__.__name__
        }
    )

# Mount API routes
app.include_router(api_router, prefix="/api")
# Also mount directly on root for convenience with prompt specifications like GET /health
app.include_router(api_router)

# Serve frontend static assets (JS, CSS) from Vite build output
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend-assets")

# Explicit root route: serve index.html for SPA entrypoint
@app.get("/")
async def serve_root():
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(content={
        "name": "SafePlate API",
        "tagline": "AI meal planning built around what YOU can safely eat.",
        "version": settings.VERSION,
        "docs": "/docs",
        "realtime": True,
        "note": "Frontend not built. Run 'cd frontend && npm run build' to generate the UI."
    })

# Serve static files at root level (favicon, icons, etc.)
@app.get("/favicon.svg")
@app.get("/favicon.ico")
async def serve_favicon():
    favicon_path = FRONTEND_DIST / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.get("/icons.svg")
async def serve_icons():
    icons_path = FRONTEND_DIST / "icons.svg"
    if icons_path.exists():
        return FileResponse(str(icons_path))
    return JSONResponse(status_code=404, content={"detail": "Not found"})

# Catch-all route: serve index.html for all non-API, non-asset paths (SPA client-side routing)
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    # Skip API routes and docs
    if full_path == "api" or full_path.startswith("api/") or full_path.startswith("docs") or full_path in ("redoc", "openapi.json"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # Try serving the exact file from dist (e.g., favicon.svg)
    file_path = FRONTEND_DIST / full_path
    if file_path.is_file():
        return FileResponse(str(file_path))

    # Otherwise, serve index.html for SPA client-side routing
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))

    # Fallback: return API info if no frontend build is available
    return JSONResponse(content={
        "name": "SafePlate API",
        "tagline": "AI meal planning built around what YOU can safely eat.",
        "version": settings.VERSION,
        "docs": "/docs",
        "realtime": True,
        "note": "Frontend not built. Run 'cd frontend && npm run build' to generate the UI."
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
