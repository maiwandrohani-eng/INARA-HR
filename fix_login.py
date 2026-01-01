#!/usr/bin/env python3
"""Fix login for maiwand user"""
import asyncio
import sys
sys.path.insert(0, '/app')

from core.database import async_engine
from core.security import hash_password
from sqlalchemy import text

async def fix_login():
    # Reset both admin and maiwand passwords
    users = [
        ('maiwand@inara.org', 'Maiwand@123'),
        ('admin@inara.org', 'Admin@123'),
    ]
    
    async with async_engine.begin() as conn:
        for email, password in users:
            hashed = hash_password(password)
            
            result = await conn.execute(
                text("""
                    UPDATE users 
                    SET hashed_password = :pwd,
                        failed_login_attempts = 0,
                        locked_until = NULL
                    WHERE email = :email 
                    RETURNING email, first_name, last_name
                """),
                {"pwd": hashed, "email": email}
            )
            user = result.fetchone()
            if user:
                print(f"✅ {user[1]} {user[2]} ({user[0]})")
                print(f"   Password: {password}")
            else:
                print(f"❌ User {email} not found")

if __name__ == "__main__":
    asyncio.run(fix_login())
