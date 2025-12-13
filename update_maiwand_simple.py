"""
Update maiwand@inara.org to super admin with new password
"""
import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Database connection
DATABASE_URL = "postgresql+asyncpg://inara_user:inara_password@localhost:5432/inara_hris"

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def update_user():
    """Update user to super admin"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Get user ID
        result = await session.execute(
            text("SELECT id FROM users WHERE email = 'maiwand@inara.org'")
        )
        user = result.first()
        
        if not user:
            print("❌ User maiwand@inara.org does not exist!")
            print("Creating the user...")
            
            # Get super_admin role ID
            result = await session.execute(
                text("SELECT id FROM roles WHERE name = 'super_admin'")
            )
            role = result.first()
            
            if not role:
                print("❌ super_admin role does not exist! Run seed script first.")
                return
            
            role_id = role[0]
            
            # Create user
            hashed_pw = hash_password("Come*1234")
            result = await session.execute(
                text("""
                    INSERT INTO users (email, hashed_password, first_name, last_name, 
                                      country_code, is_active, is_verified, is_superuser, 
                                      created_at, updated_at)
                    VALUES ('maiwand@inara.org', :password, 'Maiwand', 'User', 
                            'AF', true, true, true, NOW(), NOW())
                    RETURNING id
                """),
                {"password": hashed_pw}
            )
            user_id = result.scalar_one()
            
            # Assign role
            await session.execute(
                text("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (:user_id, :role_id)
                """),
                {"user_id": user_id, "role_id": role_id}
            )
            
            await session.commit()
            print("\n✅ User created successfully!")
            
        else:
            user_id = user[0]
            
            # Update password and make superuser
            hashed_pw = hash_password("Come*1234")
            await session.execute(
                text("""
                    UPDATE users 
                    SET hashed_password = :password,
                        is_superuser = true,
                        updated_at = NOW()
                    WHERE id = :user_id
                """),
                {"password": hashed_pw, "user_id": user_id}
            )
            
            # Get super_admin role ID
            result = await session.execute(
                text("SELECT id FROM roles WHERE name = 'super_admin'")
            )
            role = result.first()
            
            if role:
                role_id = role[0]
                
                # Check if role already assigned
                result = await session.execute(
                    text("""
                        SELECT 1 FROM user_roles 
                        WHERE user_id = :user_id AND role_id = :role_id
                    """),
                    {"user_id": user_id, "role_id": role_id}
                )
                exists = result.first()
                
                if not exists:
                    # Assign super_admin role
                    await session.execute(
                        text("""
                            INSERT INTO user_roles (user_id, role_id)
                            VALUES (:user_id, :role_id)
                        """),
                        {"user_id": user_id, "role_id": role_id}
                    )
            
            await session.commit()
            print("\n✅ User updated successfully!")
        
        print("\n📧 Email: maiwand@inara.org")
        print("🔑 Password: Come*1234")
        print("👑 Role: Super Admin")
        print("🔒 Superuser: true")
        print("\n👉 You can now login at http://localhost:3000/login")

if __name__ == "__main__":
    asyncio.run(update_user())
