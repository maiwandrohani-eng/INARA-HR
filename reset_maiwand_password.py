#!/usr/bin/env python3
"""
Reset password for maiwand@inara.org
"""

import asyncio
import sys
sys.path.insert(0, '/Users/maiwand/INARA-HR/apps/api')

from core.database import async_engine
from core.security import hash_password
from sqlalchemy import text


async def reset_password():
    email = "maiwand@inara.org"
    new_password = "Maiwand@123"
    
    print(f"🔄 Resetting password for {email}...")
    
    # Hash the new password
    hashed_password = hash_password(new_password)
    
    async with async_engine.begin() as conn:
        # Update password
        result = await conn.execute(
            text("""
                UPDATE users 
                SET hashed_password = :password,
                    updated_at = NOW()
                WHERE email = :email
                RETURNING id, email, first_name, last_name, is_active
            """),
            {"password": hashed_password, "email": email}
        )
        
        user = result.fetchone()
        
        if user:
            print(f"\n✅ Password reset successfully!")
            print(f"   Email: {user[1]}")
            print(f"   Name: {user[2]} {user[3]}")
            print(f"   Active: {user[4]}")
            print(f"\n🔐 New credentials:")
            print(f"   Email: {email}")
            print(f"   Password: {new_password}")
        else:
            print(f"\n❌ User {email} not found!")
            return False
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(reset_password())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
