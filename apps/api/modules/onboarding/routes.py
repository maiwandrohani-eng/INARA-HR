"""Onboarding Module - Routes"""
from fastapi import APIRouter, Depends
from core.database import get_db
from core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/checklist")
async def get_onboarding_checklist(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "Get onboarding checklist - TODO"}

@router.post("/checklist/{task_id}/complete")
async def complete_task(task_id: str, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": f"Complete task {task_id} - TODO"}
