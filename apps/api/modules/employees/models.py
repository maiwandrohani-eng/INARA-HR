"""
Employee Management Module - Database Models
Employee profiles, contracts, positions, and documents
"""

from sqlalchemy import Column, String, Date, Enum as SQLEnum, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class EmploymentStatus(str, enum.Enum):
    """Employment status enumeration"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    RETIRED = "retired"


class EmploymentType(str, enum.Enum):
    """Employment type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    CONSULTANT = "consultant"
    INTERN = "intern"
    VOLUNTEER = "volunteer"


class WorkType(str, enum.Enum):
    """Work location type enumeration"""
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"


class Employee(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Employee master record"""
    __tablename__ = "employees"
    
    # Link to user account
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, unique=True)
    
    # Personal Information
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    preferred_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    nationality = Column(String(100), nullable=True)
    national_id = Column(String(100), nullable=True)
    passport_number = Column(String(50), nullable=True)
    blood_type = Column(String(10), nullable=True)  # A+, B+, O+, AB+, A-, B-, O-, AB-
    medical_conditions = Column(Text, nullable=True)  # Pre-existing medical conditions
    
    # Contact Information
    personal_email = Column(String(255), nullable=True)
    work_email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    country_code = Column(String(2), nullable=True)
    # Emergency Contact 1
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)
    # Emergency Contact 2
    emergency_contact_2_name = Column(String(200), nullable=True)
    emergency_contact_2_phone = Column(String(20), nullable=True)
    emergency_contact_2_relationship = Column(String(100), nullable=True)
    emergency_contact_2_note = Column(Text, nullable=True)  # Additional notes for emergency contact 2
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Employment Details
    status = Column(SQLEnum(EmploymentStatus), default=EmploymentStatus.ACTIVE, nullable=False)
    employment_type = Column(SQLEnum(EmploymentType), nullable=False)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    probation_end_date = Column(Date, nullable=True)
    
    # Organizational Details
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey('positions.id'), nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    work_location = Column(String(255), nullable=True)
    work_type = Column(SQLEnum(WorkType), nullable=True)  # On Site, Remote, Hybrid
    
    # Profile
    profile_photo_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # JSON string
    languages = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    user = relationship("User", back_populates="employee")
    department = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    position = relationship("Position", back_populates="employees")
    manager = relationship("Employee", remote_side="Employee.id", backref="direct_reports")
    contracts = relationship("Contract", back_populates="employee", cascade="all, delete-orphan")
    documents = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")
    resignations = relationship("Resignation", foreign_keys="[Resignation.employee_id]", back_populates="employee", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Get employee's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee {self.employee_number} - {self.first_name} {self.last_name}>"


class Department(BaseModel, TenantMixin, Base):
    """Department/Team structure"""
    __tablename__ = "departments"
    
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    head_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Relationships
    parent = relationship("Department", remote_side="Department.id", backref="children")
    head = relationship("Employee", foreign_keys=[head_id])
    employees = relationship("Employee", foreign_keys=[Employee.department_id], back_populates="department")
    
    def __repr__(self):
        return f"<Department {self.code} - {self.name}>"


class Position(BaseModel, TenantMixin, Base):
    """Job positions/titles"""
    __tablename__ = "positions"
    
    title = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    level = Column(String(50), nullable=True)  # e.g., Junior, Mid, Senior, Manager
    grade = Column(String(20), nullable=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="position")
    
    def __repr__(self):
        return f"<Position {self.code} - {self.title}>"


class Contract(BaseModel, TenantMixin, AuditMixin, Base):
    """Employment contracts"""
    __tablename__ = "contracts"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    contract_number = Column(String(100), unique=True, nullable=False)
    contract_type = Column(String(50), nullable=False)  # Fixed-term, Permanent, Consultant, etc.
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Compensation
    salary = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    salary_frequency = Column(String(20), nullable=False, default="monthly")  # monthly, annually, hourly
    
    # Details
    work_hours_per_week = Column(Numeric(5, 2), nullable=True)
    probation_period_months = Column(String(10), nullable=True)
    notice_period_days = Column(String(10), nullable=True)
    
    # Documents
    contract_file_url = Column(String(500), nullable=True)
    signed_date = Column(Date, nullable=True)
    
    is_active = Column(String(10), default="true", nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="contracts")
    
    def __repr__(self):
        return f"<Contract {self.contract_number} for Employee {self.employee_id}>"


class EmployeeDocument(BaseModel, TenantMixin, AuditMixin, Base):
    """Employee documents (ID, certificates, etc.)"""
    __tablename__ = "employee_documents"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    document_type = Column(String(100), nullable=False)  # ID, Passport, Certificate, etc.
    document_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=False)
    file_size = Column(String(20), nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="documents")
    
    def __repr__(self):
        return f"<EmployeeDocument {self.document_type} for {self.employee_id}>"
