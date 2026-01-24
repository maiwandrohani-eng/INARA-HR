#!/usr/bin/env python3
"""
Script to verify all users in the database
Run from the project root: python3 verify_existing_users.py
"""
import os
import sys
import asyncio
import asyncpg

async def verify_users():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Run with: railway run python3 verify_existing_users.py")
        return 1
    
    # Convert postgresql:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Get unverified users
        unverified = await conn.fetch(
            "SELECT email, first_name, last_name FROM users WHERE is_verified = false"
        )
        
        if not unverified:
            print("✅ All users are already verified!")
            await conn.close()
            return 0
        
        print(f"\n📋 Found {len(unverified)} unverified users:")
        for user in unverified:
            print(f"   - {user['email']} ({user['first_name']} {user['last_name']})")
        
        # Update all to verified
        result = await conn.execute(
            "UPDATE users SET is_verified = true WHERE is_verified = false"
        )
        
        print(f"\n✅ Successfully verified {len(unverified)} users!")
        
        # Show all users
        all_users = await conn.fetch(
            "SELECT email, first_name, last_name, is_verified, is_active FROM users ORDER BY email"
        )
        
        print(f"\n👥 All users ({len(all_users)}):")
        for user in all_users:
            status = "✓" if user['is_verified'] else "✗"
            active = "Active" if user['is_active'] else "Inactive"
            print(f"   {status} {user['email']} - {user['first_name']} {user['last_name']} ({active})")
        
        await conn.close()
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(verify_users())
    sys.exit(exit_code)
