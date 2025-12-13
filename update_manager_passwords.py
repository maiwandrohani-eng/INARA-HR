#!/usr/bin/env python3
"""
Update Finance and HR Manager Passwords
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

from sqlalchemy import select, update
from core.database import engine
from core.models import User
from core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession


async def update_passwords():
    """Update passwords for Finance and HR managers"""
    
    password = "Inara@123"
    hashed = hash_password(password)
    
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print()
    
    async with AsyncSession(engine) as db:
        try:
            # Update Mer Wais
            stmt = (
                update(User)
                .where(User.email == "mer@inara.org")
                .values(hashed_password=hashed)
            )
            result = await db.execute(stmt)
            
            # Update Gokce Kaya
            stmt = (
                update(User)
                .where(User.email == "gokce@inara.org")
                .values(hashed_password=hashed)
            )
            result2 = await db.execute(stmt)
            
            await db.commit()
            
            print(f"✓ Updated {result.rowcount + result2.rowcount} user passwords")
            print(f"  - mer@inara.org")
            print(f"  - gokce@inara.org")
            print()
            print(f"Password for both: {password}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(update_passwords())
