#!/usr/bin/env python3
import csv
import requests
import json
from datetime import datetime

# Admin credentials
EMAIL = "mariamy@inara.org"
PASSWORD = "inara2024"
BASE_URL = "http://localhost:8000/api/v1"

def login():
    """Login and get access token"""
    print("Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": EMAIL,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("access_token")
        if token:
            print("✓ Login successful\n")
            return token
    
    print(f"✗ Login failed: {response.text}")
    return None

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

def import_employee(employee, token):
    """Import a single employee"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/employees/",
        headers=headers,
        json=employee
    )
    
    return response

def main():
    # Login first
    token = login()
    if not token:
        return
    
    # Read CSV file
    print("Reading CSV file...")
    employees = []
    
    with open('/Users/maiwand/INARA-HR/final.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Skip rows without required fields
            if not row.get('First Name') or not row.get('Last Name'):
                continue
            
            # Map CSV fields to API fields
            employee = {}
            
            if row.get('Employee Number'):
                employee['employee_number'] = row['Employee Number'].strip()
            
            if row.get('First Name'):
                employee['first_name'] = row['First Name'].strip()
            
            if row.get('Last Name'):
                employee['last_name'] = row['Last Name'].strip()
            
            if row.get('Work Email'):
                employee['work_email'] = row['Work Email'].strip()
            
            if row.get('Phone'):
                employee['phone'] = row['Phone'].strip()
            
            if row.get('Mobile'):
                employee['mobile'] = row['Mobile'].strip()
            
            if row.get('Date of Birth (YYYY-MM-DD)'):
                date = convert_date(row['Date of Birth (YYYY-MM-DD)'])
                if date:
                    employee['date_of_birth'] = date
            
            if row.get('Gender (male/female/other)'):
                gender = row['Gender (male/female/other)'].strip().lower()
                if gender in ['male', 'female', 'other']:
                    employee['gender'] = gender
            
            if row.get('Nationality (Country Code)'):
                employee['nationality'] = row['Nationality (Country Code)'].strip()
            
            if row.get('Employment Type (full_time/part_time/consultant/volunteer)'):
                emp_type = row['Employment Type (full_time/part_time/consultant/volunteer)'].strip().lower().replace(' ', '_')
                if emp_type in ['full_time', 'part_time', 'consultant', 'volunteer']:
                    employee['employment_type'] = emp_type
            
            if row.get('Work Location'):
                employee['work_location'] = row['Work Location'].strip()
            
            if row.get('Hire Date (YYYY-MM-DD)'):
                date = convert_date(row['Hire Date (YYYY-MM-DD)'])
                if date:
                    employee['hire_date'] = date
            
            if row.get('Position/Title'):
                employee['position'] = row['Position/Title'].strip()
            
            if row.get('Department'):
                employee['department'] = row['Department'].strip()
            
            # Only add if we have required fields
            if employee.get('first_name') and employee.get('last_name'):
                employees.append(employee)
    
    print(f"Found {len(employees)} employees to import\n")
    
    # Import employees
    success_count = 0
    failed_count = 0
    errors = []
    
    for i, employee in enumerate(employees, 1):
        name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}"
        print(f"[{i}/{len(employees)}] Importing {name}...", end=' ')
        
        response = import_employee(employee, token)
        
        if response.status_code in [200, 201]:
            success_count += 1
            print("✓")
        else:
            failed_count += 1
            print("✗")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message') or error_data.get('detail') or response.text
            except:
                error_msg = response.text[:200]
            
            errors.append({
                'name': name,
                'email': employee.get('work_email', 'N/A'),
                'error': error_msg
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("Import Summary:")
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print("=" * 50)
    
    if errors:
        print("\nErrors:")
        for idx, err in enumerate(errors[:20], 1):  # Show first 20 errors
            print(f"\n{idx}. {err['name']} ({err['email']})")
            print(f"   Error: {err['error'][:200]}")
        
        if len(errors) > 20:
            print(f"\n... and {len(errors) - 20} more errors")

if __name__ == "__main__":
    main()
