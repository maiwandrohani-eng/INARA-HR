"""
Payroll Module - Pydantic Schemas
Request/Response models for payroll API
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal


class PayrollEntryBase(BaseModel):
    """Base schema for payroll entry"""
    employee_id: str
    employee_number: str
    first_name: str
    last_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    basic_salary: Decimal = Field(ge=0)
    allowances: Decimal = Field(default=Decimal('0'), ge=0)
    deductions: Decimal = Field(default=Decimal('0'), ge=0)
    currency: str = Field(default='USD', max_length=3)


class PayrollEntryCreate(PayrollEntryBase):
    """Schema for creating payroll entry"""
    pass


class PayrollEntryResponse(PayrollEntryBase):
    """Schema for payroll entry response"""
    id: str
    payroll_id: str
    gross_salary: Decimal
    net_salary: Decimal
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PayrollCreate(BaseModel):
    """Schema for creating payroll"""
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020, le=2100)
    payment_date: date
    entries: List[PayrollEntryCreate]


class PayrollUpdate(BaseModel):
    """Schema for updating payroll"""
    payment_date: Optional[date] = None
    entries: Optional[List[PayrollEntryCreate]] = None


class PayrollApprovalResponse(BaseModel):
    """Schema for approval response"""
    id: str
    payroll_id: str
    approver_role: str
    approver_id: str
    approved: str
    decision_date: Optional[datetime] = None
    comments: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PayrollResponse(BaseModel):
    """Schema for payroll response"""
    id: str
    month: int
    year: int
    payment_date: date
    total_basic_salary: Decimal
    total_allowances: Decimal
    total_gross_salary: Decimal
    total_deductions: Decimal
    total_net_salary: Decimal
    status: str
    created_by_id: str
    processed_by_id: Optional[str] = None
    pdf_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    entries: List[PayrollEntryResponse] = []
    approvals: List[PayrollApprovalResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class PayrollListResponse(BaseModel):
    """Schema for paginated payroll list"""
    payrolls: List[PayrollResponse]
    total: int
    page: int
    page_size: int


class PayrollSubmitRequest(BaseModel):
    """Schema for submitting payroll to Finance"""
    pass


class PayrollApprovalRequest(BaseModel):
    """Schema for approving/rejecting payroll"""
    approved: bool
    comments: Optional[str] = None


class PayrollStatsResponse(BaseModel):
    """Schema for payroll statistics"""
    total_payrolls: int
    pending_finance_count: int
    pending_ceo_count: int
    approved_count: int
    total_amount_this_month: Decimal
    total_amount_this_year: Decimal


class EmployeePayrollSummary(BaseModel):
    """Schema for employee payroll summary"""
    employee_id: str
    employee_number: str
    first_name: str
    last_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    basic_salary: Decimal
    has_active_contract: bool
    contract_monthly_salary: Optional[Decimal] = None
