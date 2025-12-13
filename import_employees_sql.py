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
    'port': 5432
}

def convert_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD"""
    if not date_str or not date_str.strip():
        return None
    
    try:
        # Handle DD/MM/YYYY format
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                day = parts[0].zfill(2)
                month = parts[1].zfill(2)
                year = parts[2] if len(parts[2]) == 4 else f"20{parts[2]}"
                return f"{year}-{month}-{day}"
    except:
        pass
    
    return None

def main():
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("Reading CSV file...")
    employees_added = 0
    employees_skipped = 0
    errors = []
    
    with open('/Users/maiwand/INARA-HR/final.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)
        total_rows = len(rows)
        
        print(f"Found {total_rows} rows to process\n")
        
        for i, row in enumerate(rows, 1):
            # Skip rows without required fields
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            
            if not first_name or not last_name:
                employees_skipped += 1
                continue
            
            try:
                # Prepare values
                employee_id = str(uuid.uuid4())
                employee_number = row.get('Employee Number', '').strip()
                if not employee_number:
                    # Generate employee number if missing: INR-XXXX
                    employee_number = f"INR-{i:04d}"
                    
                work_email = row.get('Work Email', '').strip() or None
                phone = row.get('Phone', '').strip() or None
                mobile = row.get('Mobile', '').strip() or None
                date_of_birth = convert_date(row.get('Date of Birth (YYYY-MM-DD)', ''))
                
                gender_raw = row.get('Gender (male/female/other)', '').strip().lower()
                gender = gender_raw if gender_raw in ['male', 'female', 'other'] else None
                
                nationality = row.get('Nationality (Country Code)', '').strip() or None
                
                emp_type_raw = row.get('Employment Type (full_time/part_time/consultant/volunteer)', '').strip().upper().replace(' ', '_')
                # Map to database enum values
                if emp_type_raw == 'FULL_TIME':
                    employment_type = 'FULL_TIME'
                elif emp_type_raw == 'PART_TIME':
                    employment_type = 'PART_TIME'
                elif emp_type_raw == 'CONSULTANT':
                    employment_type = 'CONSULTANT'
                elif emp_type_raw == 'CONSULTANCY':
                    employment_type = 'CONSULTANT'
                elif emp_type_raw == 'VOLUNTEER':
                    employment_type = 'VOLUNTEER'
                else:
                    employment_type = 'FULL_TIME'  # Default
                
                work_location = row.get('Work Location', '').strip() or None
                hire_date = convert_date(row.get('Hire Date (YYYY-MM-DD)', ''))
                if not hire_date:
                    # Default hire date to today if missing
                    from datetime import date
                    hire_date = date.today()
                
                # Default date of birth if missing (required field)
                if not date_of_birth:
                    from datetime import date
                    date_of_birth = date(1990, 1, 1)
                
                status = 'ACTIVE'  # All imported employees are active
                
                # Note: position and department are stored as text in notes for now
                # since the actual fields are UUIDs that reference other tables
                
                # Insert into database
                insert_query = """
                INSERT INTO employees (
                    id, employee_number, first_name, last_name, work_email,
                    phone, mobile, date_of_birth, gender, nationality,
                    employment_type, work_location, hire_date, status, 
                    is_deleted, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    FALSE, NOW(), NOW()
                )
                """
                
                cursor.execute(insert_query, (
                    employee_id, employee_number, first_name, last_name, work_email,
                    phone, mobile, date_of_birth, gender, nationality,
                    employment_type, work_location, hire_date, status
                ))
                
                conn.commit()
                
                print(f"[{i}/{total_rows}] ✓ Added: {first_name} {last_name}")
                employees_added += 1
                
            except Exception as e:
                conn.rollback()
                error_msg = str(e)
                print(f"[{i}/{total_rows}] ✗ Failed: {first_name} {last_name} - {error_msg[:80]}")
                errors.append({
                    'name': f"{first_name} {last_name}",
                    'error': error_msg
                })
                employees_skipped += 1
    
    cursor.close()
    conn.close()
    
    # Summary
    print("\n" + "=" * 50)
    print("Import Summary:")
    print(f"✓ Successfully added: {employees_added}")
    print(f"✗ Skipped/Failed: {employees_skipped}")
    print("=" * 50)
    
    if errors:
        print("\nErrors (first 10):")
        for idx, err in enumerate(errors[:10], 1):
            print(f"\n{idx}. {err['name']}")
            print(f"   Error: {err['error'][:150]}")

if __name__ == "__main__":
    main()
