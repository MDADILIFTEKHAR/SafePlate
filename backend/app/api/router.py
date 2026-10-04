from fastapi import APIRouter
from app.api.endpoints import health, profile, pantry, meal_plan, safety, agent

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(profile.router)
api_router.include_router(pantry.router)
api_router.include_router(meal_plan.router)
api_router.include_router(safety.router)
api_router.include_router(agent.router)
