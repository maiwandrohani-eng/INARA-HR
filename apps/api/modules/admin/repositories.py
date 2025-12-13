"""
Admin Module - Repository Layer
Database operations for admin configuration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
import uuid

from modules.admin.models import CountryConfig, SalaryBand


class CountryConfigRepository:
    """Repository for CountryConfig database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self) -> List[CountryConfig]:
        """Get all country configs"""
        result = await self.db.execute(
            select(CountryConfig).where(CountryConfig.is_deleted == False)
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, config_id: uuid.UUID) -> Optional[CountryConfig]:
        """Get country config by ID"""
        result = await self.db.execute(
            select(CountryConfig).where(
                and_(CountryConfig.id == config_id, CountryConfig.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, country_code: str) -> Optional[CountryConfig]:
        """Get country config by country code"""
        result = await self.db.execute(
            select(CountryConfig).where(
                and_(CountryConfig.country_code == country_code, CountryConfig.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: dict) -> CountryConfig:
        """Create new country config"""
        config = CountryConfig(**data)
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config
    
    async def update(self, config: CountryConfig, data: dict) -> CountryConfig:
        """Update country config"""
        for key, value in data.items():
            if value is not None:
                setattr(config, key, value)
        await self.db.flush()
        await self.db.refresh(config)
        return config
    
    async def delete(self, config: CountryConfig):
        """Soft delete country config"""
        config.is_deleted = True
        await self.db.flush()


class SalaryBandRepository:
    """Repository for SalaryBand database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self, country_code: Optional[str] = None) -> List[SalaryBand]:
        """Get all salary bands, optionally filtered by country"""
        query = select(SalaryBand).where(SalaryBand.is_deleted == False)
        if country_code:
            query = query.where(
                (SalaryBand.country_code == country_code) | (SalaryBand.country_code == None)
            )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_id(self, band_id: uuid.UUID) -> Optional[SalaryBand]:
        """Get salary band by ID"""
        result = await self.db.execute(
            select(SalaryBand).where(
                and_(SalaryBand.id == band_id, SalaryBand.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: dict) -> SalaryBand:
        """Create new salary band"""
        band = SalaryBand(**data)
        self.db.add(band)
        await self.db.flush()
        await self.db.refresh(band)
        return band
    
    async def update(self, band: SalaryBand, data: dict) -> SalaryBand:
        """Update salary band"""
        for key, value in data.items():
            if value is not None:
                setattr(band, key, value)
        await self.db.flush()
        await self.db.refresh(band)
        return band
    
    async def delete(self, band: SalaryBand):
        """Soft delete salary band"""
        band.is_deleted = True
        await self.db.flush()
