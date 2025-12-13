"""Employee Self-Service (ESS) Module - Routes"""
from fastapi import APIRouter, Depends
from core.database import get_db
from core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/profile")
async def get_my_profile(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get own employee profile"""
    return {"message": "Get my profile - TODO"}

@router.patch("/profile")
async def update_my_profile(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Update own profile"""
    return {"message": "Update my profile - TODO"}

@router.get("/payslips")
async def get_my_payslips(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get own payslips"""
    return {"message": "Get my payslips - TODO"}

@router.get("/leave/balance")
async def get_my_leave_balance(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get own leave balance"""
    return {"message": "Get my leave balance - TODO"}

@router.get("/timesheets")
async def get_my_timesheets(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get own timesheets"""
    return {"message": "Get my timesheets - TODO"}

@router.get("/team")
async def get_my_team(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get team members (for managers)"""
    return {"message": "Get my team - TODO"}

@router.get("/documents")
async def get_my_documents(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get own documents"""
    return {"message": "Get my documents - TODO"}
