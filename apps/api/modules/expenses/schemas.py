"""Expense Management Module - Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal
import uuid


# Expense Report Schemas
class ExpenseReportBase(BaseModel):
    employee_id: uuid.UUID
    report_date: date
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    total_amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None
    status: str = "draft"


class ExpenseReportCreate(ExpenseReportBase):
    pass


class ExpenseReportResponse(ExpenseReportBase):
    id: uuid.UUID
    report_number: str
    approver_id: Optional[uuid.UUID] = None
    approved_date: Optional[date] = None
    
    class Config:
        from_attributes = True


# Expense Item Schemas
class ExpenseItemBase(BaseModel):
    expense_report_id: uuid.UUID
    expense_date: date
    expense_type: str
    category: Optional[str] = None
    amount: Decimal
    currency: str = "USD"
    exchange_rate: Optional[Decimal] = None
    description: str
    vendor_name: Optional[str] = None
    location: Optional[str] = None
    receipt_url: Optional[str] = None
    business_purpose: Optional[str] = None
    project_name: Optional[str] = None
    client_name: Optional[str] = None


class ExpenseItemCreate(ExpenseItemBase):
    pass


class ExpenseItemResponse(ExpenseItemBase):
    id: uuid.UUID
    amount_in_report_currency: Decimal
    receipt_attached: bool
    
    class Config:
        from_attributes = True

