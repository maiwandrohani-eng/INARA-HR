"""
Payroll Module - Database Models
Payroll, PayrollEntry, PayrollApproval models
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Numeric, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from core.database import Base
from core.models import BaseModel, TenantMixin


class PayrollStatus(str, enum.Enum):
    """Payroll approval status"""
    DRAFT = "DRAFT"  # HR is creating/editing
    PENDING_FINANCE = "PENDING_FINANCE"  # Waiting for Finance Manager review
    PENDING_CEO = "PENDING_CEO"  # Waiting for CEO approval
    APPROVED = "APPROVED"  # CEO approved, back to Finance
    REJECTED = "REJECTED"  # Rejected by Finance or CEO
    PROCESSED = "PROCESSED"  # Finance has processed payment


class Payroll(BaseModel, TenantMixin, Base):
    """Payroll batch for a specific month"""
    __tablename__ = "payrolls"
    
    # Period information
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    
    # Financial summary
    total_basic_salary = Column(Numeric(12, 2), nullable=False, default=0)
    total_allowances = Column(Numeric(12, 2), nullable=False, default=0)
    total_gross_salary = Column(Numeric(12, 2), nullable=False, default=0)
    total_deductions = Column(Numeric(12, 2), nullable=False, default=0)
    total_net_salary = Column(Numeric(12, 2), nullable=False, default=0)
    
    # Status tracking
    status = Column(SQLEnum(PayrollStatus), nullable=False, default=PayrollStatus.DRAFT)
    
    # Audit trail
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    processed_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # PDF storage
    pdf_filename = Column(String(500), nullable=True)  # ZIP file with all payslips
    
    # Relationships
    entries = relationship("PayrollEntry", back_populates="payroll", cascade="all, delete-orphan")
    approvals = relationship("PayrollApproval", back_populates="payroll", cascade="all, delete-orphan")
    
    def __repr__(self):
        try:
            # Access attributes safely without triggering lazy loads
            year = object.__getattribute__(self, 'year')
            month = object.__getattribute__(self, 'month')
            status = object.__getattribute__(self, 'status')
            return f"<Payroll {year}-{month:02d} {status}>"
        except:
            return f"<Payroll {id(self)}>"


class PayrollEntry(BaseModel, Base):
    """Individual employee entry in a payroll batch"""
    __tablename__ = "payroll_entries"
    
    # Link to payroll batch
    payroll_id = Column(UUID(as_uuid=True), ForeignKey('payrolls.id'), nullable=False)
    
    # Employee information
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    employee_number = Column(String(50), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    
    # Salary breakdown
    basic_salary = Column(Numeric(12, 2), nullable=False)
    allowances = Column(Numeric(12, 2), nullable=False, default=0)
    gross_salary = Column(Numeric(12, 2), nullable=False)
    deductions = Column(Numeric(12, 2), nullable=False, default=0)
    net_salary = Column(Numeric(12, 2), nullable=False)
    
    # Currency
    currency = Column(String(3), nullable=False, default='USD')
    
    # Relationships
    payroll = relationship("Payroll", back_populates="entries")
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<PayrollEntry {self.employee_number} - {self.first_name} {self.last_name}>"


class PayrollApproval(BaseModel, Base):
    """Track approval workflow for payroll"""
    __tablename__ = "payroll_approvals"
    
    # Link to payroll
    payroll_id = Column(UUID(as_uuid=True), ForeignKey('payrolls.id'), nullable=False)
    
    # Approval information
    approver_role = Column(String(50), nullable=False)  # "finance_manager", "ceo"
    approver_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Decision
    approved = Column(String(10), nullable=False)  # "true", "false", "pending"
    decision_date = Column(DateTime, nullable=True)
    comments = Column(String(1000), nullable=True)
    
    # Relationships
    payroll = relationship("Payroll", back_populates="approvals")
    approver = relationship("User")
    
    def __repr__(self):
        return f"<PayrollApproval {self.approver_role} - {self.approved}>"
