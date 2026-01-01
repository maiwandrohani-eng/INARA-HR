"""Employee Self-Service (ESS) Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.ess.schemas import ProfileUpdate
from modules.employees.models import Employee
from modules.employees.repositories import EmployeeRepository
from modules.leave.services import LeaveService
from modules.timesheets.models import Timesheet
from modules.payroll.models import PayrollEntry, Payroll
from modules.employee_files.models import PersonalFileDocument

router = APIRouter()


@router.get("/profile")
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get own employee profile"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    return {
        "id": str(employee.id),
        "employee_number": employee.employee_number,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.work_email,
        "phone": employee.phone,
        "department": employee.department.name if employee.department else None,
        "position": employee.position.title if employee.position else None,
        "manager": {
            "id": str(employee.manager.id),
            "name": f"{employee.manager.first_name} {employee.manager.last_name}"
        } if employee.manager else None,
        "hire_date": str(employee.hire_date) if employee.hire_date else None,
        "status": employee.status.value if hasattr(employee.status, 'value') else employee.status
    }


@router.patch("/profile")
async def update_my_profile(
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update own profile"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    update_dict = profile_data.model_dump(exclude_unset=True)
    updated_employee = await employee_repo.update(employee.id, update_dict)
    await db.commit()
    
    return {"message": "Profile updated successfully", "employee_id": str(updated_employee.id)}


@router.get("/payslips")
async def get_my_payslips(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get own payslips"""
    from sqlalchemy import and_
    from datetime import datetime
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    # Query PayrollEntry joined with Payroll
    query = select(PayrollEntry, Payroll).join(
        Payroll, PayrollEntry.payroll_id == Payroll.id
    ).where(
        and_(
            PayrollEntry.employee_id == employee.id,
            Payroll.status.in_(["APPROVED", "PROCESSED"]),
            Payroll.is_deleted == False
        )
    )
    
    if year:
        query = query.where(Payroll.year == year)
    
    if month:
        query = query.where(Payroll.month == month)
    
    query = query.order_by(Payroll.year.desc(), Payroll.month.desc())
    
    result = await db.execute(query)
    entries = result.all()
    
    return [{
        "id": str(entry.PayrollEntry.id),
        "payroll_id": str(entry.Payroll.id),
        "pay_period_start": f"{entry.Payroll.year}-{entry.Payroll.month:02d}-01",
        "pay_period_end": f"{entry.Payroll.year}-{entry.Payroll.month:02d}-{31}",
        "payment_date": entry.Payroll.payment_date.isoformat() if entry.Payroll.payment_date else None,
        "gross_pay": float(entry.PayrollEntry.gross_salary),
        "net_pay": float(entry.PayrollEntry.net_salary),
        "basic_salary": float(entry.PayrollEntry.basic_salary),
        "allowances": float(entry.PayrollEntry.allowances),
        "deductions": float(entry.PayrollEntry.deductions),
        "currency": entry.PayrollEntry.currency,
        "status": entry.Payroll.status.value
    } for entry in entries]


@router.get("/leave/balance")
async def get_my_leave_balance(
    year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get own leave balance"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    leave_service = LeaveService(db)
    balances = await leave_service.get_employee_balances(employee.id, year)
    
    return [balance.model_dump() for balance in balances]


@router.get("/timesheets")
async def get_my_timesheets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get own timesheets"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    query = select(Timesheet).where(
        Timesheet.employee_id == employee.id,
        Timesheet.is_deleted == False
    ).order_by(Timesheet.period_start.desc())
    
    result = await db.execute(query)
    timesheets = result.scalars().all()
    
    return [{
        "id": str(t.id),
        "period_start": str(t.period_start),
        "period_end": str(t.period_end),
        "status": t.status,
        "total_hours": float(t.total_hours) if t.total_hours else 0
    } for t in timesheets]


@router.get("/team")
async def get_my_team(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get team members (for managers)"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    query = select(Employee).where(
        Employee.manager_id == employee.id,
        Employee.is_deleted == False
    )
    
    result = await db.execute(query)
    team_members = result.scalars().all()
    
    return [{
        "id": str(member.id),
        "employee_number": member.employee_number,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "email": member.work_email,
        "position": member.position.title if member.position else None,
        "status": member.status.value if hasattr(member.status, 'value') else member.status
    } for member in team_members]


@router.get("/documents")
async def get_my_documents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get own documents"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    query = select(PersonalFileDocument).where(
        PersonalFileDocument.employee_id == employee.id,
        PersonalFileDocument.is_deleted == False
    ).order_by(PersonalFileDocument.created_at.desc())
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    return [{
        "id": str(f.id),
        "file_name": f.file_name,
        "file_type": f.file_type,
        "file_size": f.file_size,
        "category": f.category,
        "uploaded_at": f.created_at.isoformat() if f.created_at else None
    } for f in files]
