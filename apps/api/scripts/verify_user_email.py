#!/usr/bin/env python3
"""
Script to manually verify a user's email address
Usage: python verify_user_email.py <email>
"""

import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from modules.auth.repositories import UserRepository

async def verify_user_email(email: str):
    """Verify a user's email address"""
    engine = create_async_engine(settings.DATABASE_ASYNC_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(email)
        
        if not user:
            print(f"❌ User with email {email} not found")
            return False
        
        if user.is_verified:
            print(f"✅ User {email} is already verified")
            return True
        
        # Verify the user
        await user_repo.update(user.id, {
            "is_verified": True,
            "verification_token": None,
            "verification_token_expires": None
        })
        await session.commit()
        
        print(f"✅ Successfully verified email for {email}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_user_email.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(verify_user_email(email))
