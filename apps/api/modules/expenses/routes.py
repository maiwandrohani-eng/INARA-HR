"""Expense Management Module - Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.expenses.services import ExpenseService
from modules.expenses.schemas import ExpenseReportCreate, ExpenseItemCreate

router = APIRouter()


@router.post("/reports", status_code=201)
async def create_expense_report(
    report_data: ExpenseReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new expense report"""
    expense_service = ExpenseService(db)
    report = await expense_service.create_expense_report(report_data)
    return report


@router.get("/reports/employee/{employee_id}")
async def get_employee_expense_reports(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all expense reports for an employee"""
    try:
        employee_uuid = uuid.UUID(employee_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid employee ID format")
    
    expense_service = ExpenseService(db)
    reports = await expense_service.get_employee_expense_reports(employee_uuid)
    return reports


@router.post("/items", status_code=201)
async def add_expense_item(
    item_data: ExpenseItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Add expense item to a report"""
    expense_service = ExpenseService(db)
    item = await expense_service.add_expense_item(item_data)
    return item


@router.post("/reports/{report_id}/submit")
async def submit_expense_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Submit expense report for approval"""
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid report ID format")
    
    expense_service = ExpenseService(db)
    result = await expense_service.submit_expense_report(report_uuid)
    return result

