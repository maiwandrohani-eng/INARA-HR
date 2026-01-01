"""Asset/Equipment Management Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import date
import uuid

from modules.assets.models import Asset, AssetAssignment, AssetMaintenance
from modules.assets.schemas import AssetCreate, AssetAssignmentCreate, AssetMaintenanceCreate


class AssetRepository:
    """Repository for asset operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_asset_number(self) -> str:
        """Generate unique asset number"""
        result = await self.db.execute(
            select(func.count(Asset.id))
        )
        count = result.scalar() or 0
        return f"AST-{count + 1:06d}"
    
    async def create(self, asset_data: AssetCreate, country_code: str) -> Asset:
        """Create a new asset"""
        asset_dict = asset_data.model_dump()
        asset_dict["asset_number"] = await self.generate_asset_number()
        asset_dict["country_code"] = country_code
        asset = Asset(**asset_dict)
        self.db.add(asset)
        await self.db.flush()
        await self.db.refresh(asset)
        return asset
    
    async def get_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        """Get asset by ID"""
        result = await self.db.execute(
            select(Asset).where(and_(Asset.id == asset_id, Asset.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, status: Optional[str] = None, asset_type: Optional[str] = None) -> List[Asset]:
        """Get all assets"""
        query = select(Asset).where(Asset.is_deleted == False)
        
        if status:
            query = query.where(Asset.status == status)
        if asset_type:
            query = query.where(Asset.asset_type == asset_type)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_status(self, asset_id: uuid.UUID, status: str) -> Optional[Asset]:
        """Update asset status"""
        asset = await self.get_by_id(asset_id)
        if asset:
            asset.status = status
            await self.db.flush()
        return asset


class AssetAssignmentRepository:
    """Repository for asset assignment operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, assignment_data: AssetAssignmentCreate, country_code: str) -> AssetAssignment:
        """Create a new assignment"""
        assignment_dict = assignment_data.model_dump()
        assignment_dict["country_code"] = country_code
        assignment = AssetAssignment(**assignment_dict)
        
        # Update asset status to assigned
        asset = await self.db.get(Asset, assignment_data.asset_id)
        if asset:
            asset.status = "assigned"
        
        self.db.add(assignment)
        await self.db.flush()
        await self.db.refresh(assignment)
        return assignment
    
    async def get_by_employee(self, employee_id: uuid.UUID) -> List[AssetAssignment]:
        """Get all assignments for an employee"""
        result = await self.db.execute(
            select(AssetAssignment).where(
                and_(
                    AssetAssignment.employee_id == employee_id,
                    AssetAssignment.is_deleted == False,
                    AssetAssignment.status == "active"
                )
            )
        )
        return list(result.scalars().all())
    
    async def return_asset(self, assignment_id: uuid.UUID, return_date: date, condition: Optional[str] = None) -> Optional[AssetAssignment]:
        """Return an assigned asset"""
        result = await self.db.execute(
            select(AssetAssignment).where(
                and_(AssetAssignment.id == assignment_id, AssetAssignment.is_deleted == False)
            )
        )
        assignment = result.scalar_one_or_none()
        
        if assignment:
            assignment.status = "returned"
            assignment.actual_return_date = return_date
            if condition:
                assignment.condition_at_return = condition
            
            # Update asset status to available
            asset = await self.db.get(Asset, assignment.asset_id)
            if asset:
                asset.status = "available"
            
            await self.db.flush()
        
        return assignment


class AssetMaintenanceRepository:
    """Repository for asset maintenance operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, maintenance_data: AssetMaintenanceCreate, country_code: str) -> AssetMaintenance:
        """Create a new maintenance record"""
        maintenance_dict = maintenance_data.model_dump()
        maintenance_dict["country_code"] = country_code
        maintenance = AssetMaintenance(**maintenance_dict)
        
        # Update asset status if needed
        if maintenance_data.status == "in_progress":
            asset = await self.db.get(Asset, maintenance_data.asset_id)
            if asset:
                asset.status = "maintenance"
        
        self.db.add(maintenance)
        await self.db.flush()
        await self.db.refresh(maintenance)
        return maintenance
    
    async def get_by_asset(self, asset_id: uuid.UUID) -> List[AssetMaintenance]:
        """Get all maintenance records for an asset"""
        result = await self.db.execute(
            select(AssetMaintenance).where(
                and_(AssetMaintenance.asset_id == asset_id, AssetMaintenance.is_deleted == False)
            ).order_by(AssetMaintenance.scheduled_date.desc())
        )
        return list(result.scalars().all())

