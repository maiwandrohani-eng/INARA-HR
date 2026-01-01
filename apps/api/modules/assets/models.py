"""
Asset/Equipment Management Module - Models
IT assets, equipment tracking, assignment, maintenance
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Numeric, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class Asset(BaseModel, TenantMixin, AuditMixin, Base):
    """Asset/Equipment master record"""
    __tablename__ = "assets"
    
    asset_number = Column(String(100), unique=True, nullable=False, index=True)
    asset_name = Column(String(200), nullable=False)
    asset_type = Column(String(50), nullable=False)  # laptop, phone, monitor, printer, vehicle, furniture, etc.
    category = Column(String(100), nullable=True)  # IT, office_equipment, vehicle, etc.
    
    # Details
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, unique=True)
    
    # Financial
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    current_value = Column(Numeric(10, 2), nullable=True)
    
    # Status
    status = Column(String(20), default="available")  # available, assigned, maintenance, retired, lost, damaged
    
    # Location
    location = Column(String(200), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    
    # Specifications (JSON)
    specifications = Column(Text, nullable=True)  # JSON: RAM, storage, screen_size, etc.
    
    # Warranty
    warranty_start_date = Column(Date, nullable=True)
    warranty_end_date = Column(Date, nullable=True)
    warranty_provider = Column(String(200), nullable=True)
    
    # Relationships
    department = relationship("Department", backref="assets")
    assignments = relationship("AssetAssignment", back_populates="asset", cascade="all, delete-orphan")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Asset {self.asset_number} - {self.asset_name}>"


class AssetAssignment(BaseModel, TenantMixin, AuditMixin, Base):
    """Asset assignment to employees"""
    __tablename__ = "asset_assignments"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Assignment dates
    assigned_date = Column(Date, nullable=False)
    expected_return_date = Column(Date, nullable=True)
    actual_return_date = Column(Date, nullable=True)
    
    # Assignment details
    assignment_type = Column(String(50), default="permanent")  # permanent, temporary, loan
    condition_at_assignment = Column(String(50), nullable=True)  # new, excellent, good, fair
    condition_at_return = Column(String(50), nullable=True)
    
    # Notes
    assignment_notes = Column(Text, nullable=True)
    return_notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="active")  # active, returned, lost, damaged
    
    # Relationships
    asset = relationship("Asset", back_populates="assignments")
    employee = relationship("Employee", backref="asset_assignments")
    
    def __repr__(self):
        return f"<AssetAssignment {self.asset_id} -> {self.employee_id}>"


class AssetMaintenance(BaseModel, TenantMixin, AuditMixin, Base):
    """Asset maintenance records"""
    __tablename__ = "asset_maintenance"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    
    # Maintenance details
    maintenance_type = Column(String(50), nullable=False)  # repair, service, upgrade, cleaning, etc.
    description = Column(Text, nullable=False)
    
    # Dates
    scheduled_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    
    # Vendor/Provider
    vendor_name = Column(String(200), nullable=True)
    vendor_contact = Column(String(200), nullable=True)
    
    # Cost
    cost = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # Results
    result_notes = Column(Text, nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
    
    def __repr__(self):
        return f"<AssetMaintenance {self.asset_id} - {self.maintenance_type}>"

