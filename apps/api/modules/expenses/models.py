"""
Expense Management Module - Models
Employee expense reimbursement, expense reports, approvals
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class ExpenseReport(BaseModel, TenantMixin, AuditMixin, Base):
    """Expense report (collection of expense items)"""
    __tablename__ = "expense_reports"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Report details
    report_number = Column(String(100), unique=True, nullable=False, index=True)
    report_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    
    # Financial summary
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(3), default="USD")
    
    # Status and workflow
    status = Column(String(20), default="draft")  # draft, submitted, approved, rejected, paid
    approver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Payment
    payment_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)  # bank_transfer, check, etc.
    payment_reference = Column(String(100), nullable=True)
    
    # Notes
    description = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="expense_reports")
    approver = relationship("Employee", foreign_keys=[approver_id])
    expense_items = relationship("ExpenseItem", back_populates="expense_report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ExpenseReport {self.report_number} - {self.status}>"


class ExpenseItem(BaseModel, TenantMixin, AuditMixin, Base):
    """Individual expense item within a report"""
    __tablename__ = "expense_items"
    
    expense_report_id = Column(UUID(as_uuid=True), ForeignKey('expense_reports.id'), nullable=False)
    
    # Expense details
    expense_date = Column(Date, nullable=False)
    expense_type = Column(String(50), nullable=False)  # travel, meals, accommodation, transportation, supplies, etc.
    category = Column(String(100), nullable=True)  # business_meals, client_entertainment, etc.
    
    # Amount and currency
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    exchange_rate = Column(Numeric(10, 6), nullable=True)  # If different from report currency
    amount_in_report_currency = Column(Numeric(10, 2), nullable=False)
    
    # Description and details
    description = Column(Text, nullable=False)
    vendor_name = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Receipt/document
    receipt_url = Column(String(500), nullable=True)
    receipt_attached = Column(Boolean, default=False, nullable=False)
    
    # Business purpose
    business_purpose = Column(Text, nullable=True)
    project_name = Column(String(200), nullable=True)  # Project name instead of FK for flexibility
    client_name = Column(String(200), nullable=True)
    
    # Approval status (can be different from report status)
    item_status = Column(String(20), default="pending")  # pending, approved, rejected
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    expense_report = relationship("ExpenseReport", back_populates="expense_items")
    
    def __repr__(self):
        return f"<ExpenseItem {self.expense_type} - {self.amount}>"

