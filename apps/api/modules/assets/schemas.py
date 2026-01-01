"""Asset/Equipment Management Module - Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import uuid


# Asset Schemas
class AssetBase(BaseModel):
    asset_name: str
    asset_type: str
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    currency: str = "USD"
    current_value: Optional[float] = None
    status: str = "available"
    location: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    specifications: Optional[str] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    warranty_provider: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    id: uuid.UUID
    asset_number: str
    created_at: Optional[date] = None
    
    class Config:
        from_attributes = True


# Asset Assignment Schemas
class AssetAssignmentBase(BaseModel):
    asset_id: uuid.UUID
    employee_id: uuid.UUID
    assigned_date: date
    expected_return_date: Optional[date] = None
    assignment_type: str = "permanent"
    condition_at_assignment: Optional[str] = None
    assignment_notes: Optional[str] = None


class AssetAssignmentCreate(AssetAssignmentBase):
    pass


class AssetAssignmentResponse(AssetAssignmentBase):
    id: uuid.UUID
    status: str
    
    class Config:
        from_attributes = True


# Asset Maintenance Schemas
class AssetMaintenanceBase(BaseModel):
    asset_id: uuid.UUID
    maintenance_type: str
    description: str
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    cost: Optional[float] = None
    currency: str = "USD"
    status: str = "scheduled"
    result_notes: Optional[str] = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    pass


class AssetMaintenanceResponse(AssetMaintenanceBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

