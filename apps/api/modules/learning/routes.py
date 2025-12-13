"""Learning Module - Routes"""
from fastapi import APIRouter, Depends
from core.database import get_db
from core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/courses")
async def list_courses(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "List courses - TODO"}

@router.post("/enrollments")
async def enroll_in_course(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "Enroll in course - TODO"}

@router.get("/my-courses")
async def my_courses(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "My courses - TODO"}
