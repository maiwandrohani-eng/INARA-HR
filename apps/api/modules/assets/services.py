"""Asset/Equipment Management Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
import uuid

from modules.assets.repositories import AssetRepository, AssetAssignmentRepository, AssetMaintenanceRepository
from modules.assets.schemas import AssetCreate, AssetAssignmentCreate, AssetMaintenanceCreate
from core.exceptions import NotFoundException, BadRequestException


class AssetService:
    """Service for asset management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.assignment_repo = AssetAssignmentRepository(db)
        self.maintenance_repo = AssetMaintenanceRepository(db)
    
    async def create_asset(self, asset_data: AssetCreate, country_code: str = "US") -> dict:
        """Create a new asset"""
        asset = await self.asset_repo.create(asset_data, country_code)
        await self.db.commit()
        return {
            "id": str(asset.id),
            "asset_number": asset.asset_number,
            "asset_name": asset.asset_name,
            "status": asset.status
        }
    
    async def get_assets(self, status: Optional[str] = None, asset_type: Optional[str] = None) -> List[dict]:
        """Get all assets"""
        assets = await self.asset_repo.get_all(status=status, asset_type=asset_type)
        return [{
            "id": str(a.id),
            "asset_number": a.asset_number,
            "asset_name": a.asset_name,
            "asset_type": a.asset_type,
            "status": a.status,
            "location": a.location,
            "serial_number": a.serial_number
        } for a in assets]
    
    async def assign_asset(self, assignment_data: AssetAssignmentCreate, country_code: str = "US") -> dict:
        """Assign asset to employee"""
        # Check if asset is available
        asset = await self.asset_repo.get_by_id(assignment_data.asset_id)
        if not asset:
            raise NotFoundException(resource="Asset")
        
        if asset.status != "available":
            raise BadRequestException(message=f"Asset is not available. Current status: {asset.status}")
        
        assignment = await self.assignment_repo.create(assignment_data, country_code)
        await self.db.commit()
        
        return {
            "id": str(assignment.id),
            "asset_id": str(assignment.asset_id),
            "employee_id": str(assignment.employee_id),
            "status": assignment.status
        }
    
    async def return_asset(self, assignment_id: uuid.UUID, return_date: Optional[date] = None, condition: Optional[str] = None) -> dict:
        """Return an assigned asset"""
        assignment = await self.assignment_repo.return_asset(assignment_id, return_date or date.today(), condition)
        if not assignment:
            raise NotFoundException(resource="Asset assignment")
        
        await self.db.commit()
        return {"id": str(assignment.id), "status": assignment.status}
    
    async def schedule_maintenance(self, maintenance_data: AssetMaintenanceCreate, country_code: str = "US") -> dict:
        """Schedule asset maintenance"""
        asset = await self.asset_repo.get_by_id(maintenance_data.asset_id)
        if not asset:
            raise NotFoundException(resource="Asset")
        
        maintenance = await self.maintenance_repo.create(maintenance_data, country_code)
        await self.db.commit()
        
        return {
            "id": str(maintenance.id),
            "asset_id": str(maintenance.asset_id),
            "maintenance_type": maintenance.maintenance_type,
            "status": maintenance.status
        }

