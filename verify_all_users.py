"""
Quick script to verify all existing user accounts
Run with: railway run python verify_all_users.py
"""
import asyncio
import sys
import os

# Add the apps/api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'api'))

async def verify_all_users():
    from core.database import async_session
    from modules.auth.models import User
    from sqlalchemy import select, update
    
    async with async_session() as db:
        # Get all unverified users
        result = await db.execute(
            select(User).where(User.is_verified == False)
        )
        unverified_users = result.scalars().all()
        
        if not unverified_users:
            print("✅ All users are already verified!")
            return
        
        print(f"Found {len(unverified_users)} unverified users:")
        for user in unverified_users:
            print(f"  - {user.email} ({user.first_name} {user.last_name})")
        
        # Update all to verified
        await db.execute(
            update(User)
            .where(User.is_verified == False)
            .values(is_verified=True)
        )
        await db.commit()
        
        print(f"\n✅ Successfully verified {len(unverified_users)} users!")

if __name__ == "__main__":
    asyncio.run(verify_all_users())
