#!/usr/bin/env python3
import csv
import psycopg2
from datetime import datetime
import uuid

# Database connection
DB_CONFIG = {
    'dbname': 'inara_hris',
    'user': 'inara_user',
    'password': 'inara_password',
    'host': 'localhost',
    'port': '5432'
}

def convert_date(date_str):
    """Convert date string to YYYY-MM-DD format"""
    if not date_str or date_str.strip() == '':
        return '1990-01-01'
    
    try:
        # Try YYYY-MM-DD format first
        dt = datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except:
        try:
            # Try DD/MM/YYYY format
            dt = datetime.strptime(date_str.strip(), '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return '1990-01-01'

def map_country_code(location, nationality):
    """Map country code from work location or nationality"""
    text = (location + ' ' + nationality).lower()
    
    if 'egypt' in text or 'cairo' in text or 'giza' in text:
        return 'EG'
    elif 'lebanon' in text or 'beirut' in text or 'bekaa' in text:
        return 'LB'
    elif 'palestine' in text or 'gaza' in text:
        return 'PS'
    elif 'syria' in text or 'damascus' in text or 'homs' in text:
        return 'SY'
    elif 'turkey' in text or 'türkiye' in text or 'ankara' in text or 'gaziantep' in text or 'istanbul' in text or 'konya' in text or 'izmir' in text:
        return 'TR'
    elif 'afghanistan' in text or 'kabul' in text or 'nangarhar' in text:
        return 'AF'
    elif 'pakistan' in text or 'peshawar' in text:
        return 'PK'
    elif 'georgia' in text or 'tbilisi' in text:
        return 'GE'
    elif 'uk' in text or 'britain' in text or 'swindon' in text:
        return 'GB'
    elif 'france' in text or 'carrieres' in text:
        return 'FR'
    else:
        return 'XX'

def map_employment_type(emp_type):
    """Map employment type to database enum"""
    if not emp_type:
        return 'FULL_TIME'
    
    emp_type_upper = emp_type.upper().strip()
    
    if 'CONSULTANT' in emp_type_upper or 'CONSULTANCY' in emp_type_upper:
        return 'CONSULTANT'
    elif 'PART' in emp_type_upper or 'PART_TIME' in emp_type_upper:
        return 'PART_TIME'
    elif 'VOLUNTEER' in emp_type_upper:
        return 'VOLUNTEER'
    else:
        return 'FULL_TIME'

print("Connecting to database...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("Reading CSV file...")
csv_file = '/Users/maiwand/INARA-HR/INARA_staff_directory_formatted.csv'

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Found {len(rows)} employees to import\n")

success_count = 0
failed_count = 0
errors = []

for idx, row in enumerate(rows, 1):
    try:
        # Generate UUID
        emp_id = str(uuid.uuid4())
        
        # Get basic fields
        first_name = row.get('First Name', '').strip()
        last_name = row.get('Last Name', '').strip()
        work_email = row.get('Work Email', '').strip()
        personal_email = row.get('Personal Email', '').strip()
        phone = row.get('Phone', '').strip()
        mobile = row.get('Mobile', '').strip()
        
        # Generate employee number if not present
        employee_number = f"INR-{idx:04d}"
        
        # Convert dates
        date_of_birth = convert_date(row.get('Date of Birth', ''))
        hire_date = convert_date(row.get('Hire Date', ''))
        
        # Get other fields
        gender = row.get('Gender', 'male').strip().lower()
        nationality = row.get('Nationality', '').strip()
        work_location = row.get('Work Location', '').strip()
        position = row.get('Position', '').strip()
        department = row.get('Department', '').strip()
        
        # Map country code
        country_code = map_country_code(work_location, nationality)
        
        # Map employment type
        employment_type = map_employment_type(row.get('Employment Type', ''))
        
        # Insert into database
        insert_query = """
            INSERT INTO employees (
                id, employee_number, first_name, last_name, 
                work_email, personal_email, phone, mobile,
                date_of_birth, gender, nationality, employment_type,
                hire_date, country_code, is_deleted, status,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """
        
        cur.execute(insert_query, (
            emp_id, employee_number, first_name, last_name,
            work_email, personal_email, phone, mobile,
            date_of_birth, gender, nationality, employment_type,
            hire_date, country_code, False, 'ACTIVE'
        ))
        
        conn.commit()
        success_count += 1
        print(f"[{idx}/{len(rows)}] ✓ {first_name} {last_name}")
        
    except Exception as e:
        conn.rollback()
        failed_count += 1
        error_msg = str(e).split('\n')[0]
        errors.append(f"{first_name} {last_name} - {error_msg}")
        print(f"[{idx}/{len(rows)}] ✗ {first_name} {last_name} - {error_msg}")

cur.close()
conn.close()

print("\n" + "="*50)
print("Import Summary:")
print(f"✓ Successfully added: {success_count}")
print(f"✗ Failed: {failed_count}")

if errors:
    print("\nFirst 10 errors:")
    for error in errors[:10]:
        print(f"  • {error}")

print("="*50)
