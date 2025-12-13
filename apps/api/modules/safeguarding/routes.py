"""Safeguarding Module - Routes"""
from fastapi import APIRouter, Depends
from core.database import get_db
from core.dependencies import get_current_active_user, require_admin

router = APIRouter()

@router.post("/cases")
async def report_case(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Report safeguarding case"""
    return {"message": "Report case - TODO"}

@router.get("/cases")
async def list_cases(db = Depends(get_db), current_user = Depends(require_admin)):
    """List safeguarding cases (Admin/HR only)"""
    return {"message": "List cases - TODO"}

@router.get("/cases/{case_id}")
async def get_case(case_id: str, db = Depends(get_db), current_user = Depends(require_admin)):
    """Get case details (Admin/HR only)"""
    return {"message": f"Get case {case_id} - TODO"}

@router.patch("/cases/{case_id}")
async def update_case(case_id: str, db = Depends(get_db), current_user = Depends(require_admin)):
    """Update case (Admin/HR only)"""
    return {"message": f"Update case {case_id} - TODO"}
