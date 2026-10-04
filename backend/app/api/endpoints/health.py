import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.database.session import get_db

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # 1. Database check
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # 2. AI Provider & Ollama connectivity check
    ollama_available = False
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if res.status_code == 200:
                ollama_available = True
    except Exception:
        ollama_available = False

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "ai_provider": settings.MODEL_PROVIDER,
        "model_name": settings.MODEL_NAME,
        "ai_engine": "active",
        "ollama_available": ollama_available,
        "realtime": True,
        "demo_mode": settings.DEMO_MODE,
        "version": settings.VERSION
    }
