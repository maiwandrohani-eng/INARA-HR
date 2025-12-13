#!/usr/bin/env python3
import csv
import sys
import os

# Add the API directory to the path
sys.path.insert(0, '/Users/maiwand/INARA-HR/apps/api')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.employees.models import Employee
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/inara_hr"

def convert_date(date_str):
    """Convert DD/MM/YYYY to date object"""
    if not date_str or not date_str.strip():
        return None
    
    try:
        # Handle DD/MM/YYYY format
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2]) if len(parts[2]) == 4 else 2000 + int(parts[2])
                return datetime(year, month, day).date()
    except Exception as e:
        print(f"Date parsing error for '{date_str}': {e}")
    
    return None

def main():
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("Reading CSV file...")
    employees_added = 0
    employees_skipped = 0
    errors = []
    
    with open('/Users/maiwand/INARA-HR/final.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        total_rows = sum(1 for row in csv_reader)
        file.seek(0)
        next(csv_reader)  # Skip header
        
        print(f"Found {total_rows} rows to process\n")
        
        for i, row in enumerate(csv_reader, 1):
            # Skip rows without required fields
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            
            if not first_name or not last_name:
                employees_skipped += 1
                continue
            
            try:
                # Create employee object
                employee = Employee()
                
                if row.get('Employee Number'):
                    employee.employee_number = row['Employee Number'].strip()
                
                employee.first_name = first_name
                employee.last_name = last_name
                
                if row.get('Work Email'):
                    employee.work_email = row['Work Email'].strip()
                
                if row.get('Phone'):
                    employee.phone = row['Phone'].strip()
                
                if row.get('Mobile'):
                    employee.mobile = row['Mobile'].strip()
                
                if row.get('Date of Birth (YYYY-MM-DD)'):
                    employee.date_of_birth = convert_date(row['Date of Birth (YYYY-MM-DD)'])
                
                if row.get('Gender (male/female/other)'):
                    gender = row['Gender (male/female/other)'].strip().lower()
                    if gender in ['male', 'female', 'other']:
                        employee.gender = gender
                
                if row.get('Nationality (Country Code)'):
                    employee.nationality = row['Nationality (Country Code)'].strip()
                
                if row.get('Employment Type (full_time/part_time/consultant/volunteer)'):
                    emp_type = row['Employment Type (full_time/part_time/consultant/volunteer)'].strip().lower().replace(' ', '_')
                    if emp_type in ['full_time', 'part_time', 'consultant', 'volunteer']:
                        employee.employment_type = emp_type
                
                if row.get('Work Location'):
                    employee.work_location = row['Work Location'].strip()
                
                if row.get('Hire Date (YYYY-MM-DD)'):
                    employee.hire_date = convert_date(row['Hire Date (YYYY-MM-DD)'])
                
                if row.get('Position/Title'):
                    employee.position = row['Position/Title'].strip()
                
                if row.get('Department'):
                    employee.department = row['Department'].strip()
                
                employee.status = 'active'
                
                session.add(employee)
                session.commit()
                
                print(f"[{i}/{total_rows}] ✓ Added: {first_name} {last_name}")
                employees_added += 1
                
            except Exception as e:
                session.rollback()
                error_msg = str(e)
                print(f"[{i}/{total_rows}] ✗ Failed: {first_name} {last_name} - {error_msg[:100]}")
                errors.append({
                    'name': f"{first_name} {last_name}",
                    'error': error_msg
                })
                employees_skipped += 1
    
    session.close()
    
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
            print(f"   Error: {err['error'][:200]}")

if __name__ == "__main__":
    main()
