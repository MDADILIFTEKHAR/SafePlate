from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import AgentRun, UserProfile
from app.schemas.api_models import AgentRunRecord, AgentStepRecord
from app.services.agent.agent_loop import agent_loop

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/run", response_model=AgentRunRecord)
async def trigger_agent_run(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found.")

    profile_dict = {
        "id": profile.id,
        "name": profile.name,
        "daily_budget": profile.daily_budget,
        "max_cooking_time_minutes": profile.max_cooking_time_minutes,
        "spice_level": profile.spice_level,
        "cuisines": profile.get_cuisines_list(),
        "allergies": [a.name for a in profile.allergies],
        "dietary_preference": profile.dietary_preferences[0].preference_type if profile.dietary_preferences else "Vegetarian",
        "disliked_ingredients": profile.get_disliked_list()
    }
    pantry_items = [p.name for p in profile.pantry_items]

    result = await agent_loop.execute_plan_generation(profile_dict, pantry_items, db=db)
    
    run_record = db.query(AgentRun).filter(AgentRun.id == result["run_id"]).first()
    if not run_record:
        raise HTTPException(status_code=500, detail="Could not retrieve agent execution log.")

    steps_parsed = [
        AgentStepRecord(
            iteration=s["iteration"],
            candidate_summary=s.get("candidate_summary", ""),
            violations=s.get("violations", []),
            repair_instruction=s.get("repair_instruction"),
            status=s.get("status", "unknown"),
            timestamp=s.get("timestamp", "")
        ) for s in run_record.get_steps_data()
    ]

    return AgentRunRecord(
        id=run_record.id,
        prompt_type=run_record.prompt_type,
        iteration_count=run_record.iteration_count,
        final_status=run_record.final_status,
        violations=run_record.get_violations(),
        repair_actions=run_record.get_repair_actions(),
        execution_time_ms=run_record.execution_time_ms,
        steps_data=steps_parsed,
        created_at=run_record.created_at
    )

@router.get("/runs/{run_id}", response_model=AgentRunRecord)
def get_agent_run(run_id: str, db: Session = Depends(get_db)):
    record = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Agent run '{run_id}' not found.")

    steps_parsed = [
        AgentStepRecord(
            iteration=s["iteration"],
            candidate_summary=s.get("candidate_summary", ""),
            violations=s.get("violations", []),
            repair_instruction=s.get("repair_instruction"),
            status=s.get("status", "unknown"),
            timestamp=s.get("timestamp", "")
        ) for s in record.get_steps_data()
    ]

    return AgentRunRecord(
        id=record.id,
        prompt_type=record.prompt_type,
        iteration_count=record.iteration_count,
        final_status=record.final_status,
        violations=record.get_violations(),
        repair_actions=record.get_repair_actions(),
        execution_time_ms=record.execution_time_ms,
        steps_data=steps_parsed,
        created_at=record.created_at
    )
