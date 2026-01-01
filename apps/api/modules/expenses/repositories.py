"""Expense Management Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import date
from decimal import Decimal
import uuid

from modules.expenses.models import ExpenseReport, ExpenseItem
from modules.expenses.schemas import ExpenseReportCreate, ExpenseItemCreate


class ExpenseReportRepository:
    """Repository for expense report operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_report_number(self) -> str:
        """Generate unique report number"""
        result = await self.db.execute(
            select(func.count(ExpenseReport.id))
        )
        count = result.scalar() or 0
        return f"EXP-{date.today().year}-{count + 1:06d}"
    
    async def create(self, report_data: ExpenseReportCreate, country_code: str) -> ExpenseReport:
        """Create a new expense report"""
        report_dict = report_data.model_dump()
        report_dict["report_number"] = await self.generate_report_number()
        report_dict["country_code"] = country_code
        report = ExpenseReport(**report_dict)
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report
    
    async def get_by_id(self, report_id: uuid.UUID) -> Optional[ExpenseReport]:
        """Get expense report by ID"""
        result = await self.db.execute(
            select(ExpenseReport).where(
                and_(ExpenseReport.id == report_id, ExpenseReport.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee(self, employee_id: uuid.UUID, status: Optional[str] = None) -> List[ExpenseReport]:
        """Get all expense reports for an employee"""
        query = select(ExpenseReport).where(
            and_(
                ExpenseReport.employee_id == employee_id,
                ExpenseReport.is_deleted == False
            )
        )
        if status:
            query = query.where(ExpenseReport.status == status)
        query = query.order_by(ExpenseReport.report_date.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_total(self, report_id: uuid.UUID):
        """Recalculate and update total amount from items"""
        items = await self.db.execute(
            select(ExpenseItem).where(
                and_(
                    ExpenseItem.expense_report_id == report_id,
                    ExpenseItem.is_deleted == False
                )
            )
        )
        items_list = items.scalars().all()
        total = sum(item.amount_in_report_currency for item in items_list if item.amount_in_report_currency)
        
        report = await self.get_by_id(report_id)
        if report:
            report.total_amount = Decimal(str(total))
            await self.db.flush()


class ExpenseItemRepository:
    """Repository for expense item operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.report_repo = ExpenseReportRepository(db)
    
    async def create(self, item_data: ExpenseItemCreate, country_code: str) -> ExpenseItem:
        """Create a new expense item"""
        item_dict = item_data.model_dump()
        
        # Calculate amount in report currency if exchange rate provided
        if item_dict.get("exchange_rate") and item_dict.get("amount"):
            rate = float(item_dict["exchange_rate"])
            amount = float(item_dict["amount"])
            item_dict["amount_in_report_currency"] = Decimal(str(amount * rate))
        else:
            item_dict["amount_in_report_currency"] = item_dict["amount"]
        
        item_dict["country_code"] = country_code
        item_dict["receipt_attached"] = bool(item_dict.get("receipt_url"))
        
        item = ExpenseItem(**item_dict)
        self.db.add(item)
        await self.db.flush()
        
        # Update report total
        await self.report_repo.update_total(item_data.expense_report_id)
        
        await self.db.refresh(item)
        return item
    
    async def get_by_report(self, report_id: uuid.UUID) -> List[ExpenseItem]:
        """Get all items for an expense report"""
        result = await self.db.execute(
            select(ExpenseItem).where(
                and_(
                    ExpenseItem.expense_report_id == report_id,
                    ExpenseItem.is_deleted == False
                )
            ).order_by(ExpenseItem.expense_date.desc())
        )
        return list(result.scalars().all())

