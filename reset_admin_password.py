#!/usr/bin/env python3
"""
Reset Admin Password
Quick script to reset the admin password
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/api'))

from sqlalchemy import create_engine, text
from core.config import settings
from core.security import hash_password

def reset_password(email="admin@inara.org", password="Admin@123"):
    """Reset user password"""
    engine = create_engine(settings.DATABASE_URL)
    
    hashed = hash_password(password)
    
    with engine.connect() as conn:
        result = conn.execute(
            text("UPDATE users SET hashed_password = :pwd WHERE email = :email"),
            {"pwd": hashed, "email": email}
        )
        conn.commit()
        
        if result.rowcount > 0:
            print(f"✅ Password reset successfully!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
        else:
            print(f"❌ User {email} not found!")

if __name__ == "__main__":
    reset_password()
