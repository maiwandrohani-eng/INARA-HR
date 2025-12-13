"""
Script to seed employees from Excel file into the database
"""
import asyncio
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import AsyncSessionLocal
from modules.auth.models import User
from modules.employees.models import Employee
from core.security import hash_password

# Default password for all employees
DEFAULT_PASSWORD = "inara2024"


async def seed_employees():
    """Seed employees from JSON data"""
    
    # Load employee data
    with open('/tmp/employees_data.json', 'r') as f:
        data = json.load(f)
    
    employees_data = data['employees']
    created_users = {}  # Track created users by email
    
    async with AsyncSessionLocal() as session:
        try:
            for emp_data in employees_data:
                # Check if employee already exists
                result = await session.execute(
                    select(Employee).where(Employee.employee_number == emp_data['Employee ID'])
                )
                existing_emp = result.scalar_one_or_none()
                
                if existing_emp:
                    print(f"Employee {emp_data['Employee ID']} already exists, skipping...")
                    continue
                
                # Parse dates
                hiring_date = None
                if emp_data.get('Hiring Date'):
                    try:
                        if isinstance(emp_data['Hiring Date'], str):
                            # Try different date formats
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d\\%m\\%Y']:
                                try:
                                    hiring_date = datetime.strptime(emp_data['Hiring Date'], fmt)
                                    break
                                except:
                                    continue
                    except:
                        pass
                
                date_of_birth = None
                if emp_data.get('Date of Birth'):
                    try:
                        if isinstance(emp_data['Date of Birth'], str):
                            # Try different date formats
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d\\%m\\%Y']:
                                try:
                                    date_of_birth = datetime.strptime(emp_data['Date of Birth'], fmt)
                                    break
                                except:
                                    continue
                    except:
                        pass
                
                # Create username from email or employee ID
                email_to_use = emp_data.get('Email')
                if email_to_use:
                    email_to_use = email_to_use.strip()  # Remove leading/trailing spaces
                
                # Parse phone
                phone = None
                if emp_data.get('Phone'):
                    phone = str(emp_data['Phone']).replace(' ', '')
                
                # Parse salary
                salary = None
                if emp_data.get('Current Salary'):
                    try:
                        salary_str = str(emp_data['Current Salary']).replace('TRY', '')
                        salary = float(salary_str)
                    except:
                        pass
                
                # Create User account ONLY if email exists AND hasn't been used yet
                user_id = None
                if email_to_use and email_to_use not in created_users:
                    # Check if user exists in database
                    user_result = await session.execute(
                        select(User).where(User.email == email_to_use)
                    )
                    existing_user = user_result.scalar_one_or_none()
                    
                    if existing_user:
                        user_id = existing_user.id
                        created_users[email_to_use] = user_id
                    else:
                        # Map country to country code (ISO 3166-1 alpha-2)
                        country_code_map = {
                            'Afghanistan': 'AF',
                            'Lebanon': 'LB',
                            'Egypt': 'EG',
                            'Palestine': 'PS',
                            'Syria': 'SY',
                            'Turkiye': 'TR',
                            'Turkey': 'TR',
                            'UK': 'GB'
                        }
                        country_code = country_code_map.get(emp_data.get('Country'), 'LB')  # Default to Lebanon
                        
                        user = User(
                            email=email_to_use,
                            hashed_password=hash_password(DEFAULT_PASSWORD),
                            first_name=emp_data.get('First Name') or 'Unknown',
                            last_name=emp_data.get('Last Name') or 'Unknown',
                            phone=phone,
                            country_code=country_code,
                            is_active=True,
                            is_verified=True
                        )
                        session.add(user)
                        await session.flush()
                        user_id = user.id
                        created_users[email_to_use] = user_id
                
                # Determine employment type
                employment_type = 'full_time'  # default
                contract_type_map = {
                    'Full Time': 'full_time',
                    'Part Time': 'part_time',
                    'Consultancy': 'consultant',
                    'Volunteer': 'volunteer'
                }
                if emp_data.get('Contract Type') in contract_type_map:
                    employment_type = contract_type_map[emp_data['Contract Type']]
                
                # Map country to country code (ISO 3166-1 alpha-2)
                country_code_map = {
                    'Afghanistan': 'AF',
                    'Lebanon': 'LB',
                    'Egypt': 'EG',
                    'Palestine': 'PS',
                    'Syria': 'SY',
                    'Turkiye': 'TR',
                    'Turkey': 'TR',
                    'UK': 'GB'
                }
                emp_country_code = country_code_map.get(emp_data.get('Country'), 'LB')
                
                # Create Employee (don't link to user if employee has no email or email was already used - user_id will be null)
                # For work_email, make it unique by appending employee number if needed
                work_email = email_to_use if email_to_use else f"{emp_data['Employee ID'].lower()}@inara.org"
                if email_to_use and email_to_use in created_users:
                    # Email already used for another employee, make work_email unique
                    work_email = f"{emp_data['Employee ID'].lower()}@inara.org"
                
                employee = Employee(
                    user_id=user_id,  # Will be None if no email or email already used
                    employee_number=emp_data['Employee ID'],
                    first_name=emp_data.get('First Name') or 'Unknown',
                    last_name=emp_data.get('Last Name') or 'Unknown',
                    work_email=work_email,
                    personal_email=email_to_use,
                    phone=phone,
                    mobile=phone,
                    date_of_birth=date_of_birth or datetime(1990, 1, 1),  # Default if missing
                    gender=emp_data.get('Gender'),
                    address_line1=emp_data.get('Address'),
                    city=emp_data.get('City'),
                    country=emp_data.get('Country'),
                    country_code=emp_country_code,
                    hire_date=hiring_date or datetime.now(),
                    employment_type=employment_type,
                    work_location=emp_data.get('Office'),
                    status='active'
                )
                
                session.add(employee)
                print(f"Added employee: {emp_data['Employee ID']} - {emp_data['First Name']} {emp_data['Last Name']}")
            
            await session.commit()
            print(f"\nSuccessfully seeded {len(employees_data)} employees!")
            
        except Exception as e:
            await session.rollback()
            print(f"Error seeding employees: {e}")
            raise


if __name__ == "__main__":
    print("Starting employee seeding...")
    print(f"Default password for all accounts: {DEFAULT_PASSWORD}\n")
    asyncio.run(seed_employees())
