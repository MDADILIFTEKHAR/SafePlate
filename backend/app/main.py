from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.init_db import init_db
from app.api.router import api_router

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
            "message": "Something went wrong while processing your request. Please try again or switch to demo mode.",
            "type": exc.__class__.__name__
        }
    )

# Mount API routes
app.include_router(api_router, prefix="/api")
# Also mount directly on root for convenience with prompt specifications like GET /health
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "name": "SafePlate API",
        "tagline": "AI meal planning built around what YOU can safely eat.",
        "version": settings.VERSION,
        "docs": "/docs",
        "demo_mode": settings.DEMO_MODE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
