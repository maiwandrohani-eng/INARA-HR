"""Expense Management Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
import uuid

from modules.expenses.repositories import ExpenseReportRepository, ExpenseItemRepository
from modules.expenses.schemas import ExpenseReportCreate, ExpenseItemCreate
from core.exceptions import NotFoundException, BadRequestException


class ExpenseService:
    """Service for expense management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.report_repo = ExpenseReportRepository(db)
        self.item_repo = ExpenseItemRepository(db)
    
    async def create_expense_report(self, report_data: ExpenseReportCreate, country_code: str = "US") -> dict:
        """Create a new expense report"""
        report = await self.report_repo.create(report_data, country_code)
        await self.db.commit()
        return {
            "id": str(report.id),
            "report_number": report.report_number,
            "total_amount": float(report.total_amount),
            "status": report.status
        }
    
    async def add_expense_item(self, item_data: ExpenseItemCreate, country_code: str = "US") -> dict:
        """Add expense item to a report"""
        # Verify report exists
        report = await self.report_repo.get_by_id(item_data.expense_report_id)
        if not report:
            raise NotFoundException(resource="Expense report")
        
        if report.status != "draft":
            raise BadRequestException(message="Cannot add items to a submitted report")
        
        item = await self.item_repo.create(item_data, country_code)
        await self.db.commit()
        
        return {
            "id": str(item.id),
            "expense_type": item.expense_type,
            "amount": float(item.amount),
            "amount_in_report_currency": float(item.amount_in_report_currency)
        }
    
    async def submit_expense_report(self, report_id: uuid.UUID) -> dict:
        """Submit expense report for approval"""
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise NotFoundException(resource="Expense report")
        
        if report.status != "draft":
            raise BadRequestException(message="Report is already submitted")
        
        if report.total_amount <= 0:
            raise BadRequestException(message="Cannot submit empty expense report")
        
        report.status = "submitted"
        await self.db.commit()
        
        return {"id": str(report.id), "status": report.status}
    
    async def get_employee_expense_reports(self, employee_id: uuid.UUID) -> List[dict]:
        """Get all expense reports for an employee"""
        reports = await self.report_repo.get_by_employee(employee_id)
        return [{
            "id": str(r.id),
            "report_number": r.report_number,
            "report_date": str(r.report_date),
            "total_amount": float(r.total_amount),
            "currency": r.currency,
            "status": r.status
        } for r in reports]

