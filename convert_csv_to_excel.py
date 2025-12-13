#!/usr/bin/env python3
import csv
import openpyxl
from openpyxl import Workbook

# Read the CSV and convert to proper Excel format
input_file = '/Users/maiwand/INARA-HR/final.csv'
output_file = '/Users/maiwand/INARA-HR/employees_import.xlsx'

# Create a new workbook
wb = Workbook()
ws = wb.active
ws.title = "Employees"

# Read CSV
with open(input_file, 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    
    # Write header row with proper names (matching the import dialog)
    ws.append([
        'First Name',
        'Last Name',
        'Work Email',
        'Personal Email',
        'Phone',
        'Mobile',
        'Date of Birth',
        'Gender',
        'Nationality',
        'Employment Type',
        'Work Location',
        'Hire Date',
        'Position',
        'Department'
    ])
    
    # Skip the CSV header
    next(csv_reader)
    
    # Process each row
    for row in csv_reader:
        if len(row) < 14:
            continue
            
        # Map CSV columns to Excel columns
        first_name = row[1]  # First Name
        last_name = row[2]  # Last Name
        work_email = row[3]  # Work Email
        phone = row[4]  # Phone
        mobile = row[5]  # Mobile
        date_of_birth = row[6]  # Date of Birth
        gender = row[7]  # Gender
        nationality = row[8]  # Nationality
        employment_type = row[9]  # Employment Type
        work_location = row[10]  # Work Location
        hire_date = row[11]  # Hire Date
        position = row[12]  # Position/Title
        department = row[13]  # Department
        
        # Write row
        ws.append([
            first_name,
            last_name,
            work_email if work_email else f"{first_name.lower()}.{last_name.lower()}@inara.org",  # Generate email if missing
            '',  # Personal email
            phone,
            mobile,
            date_of_birth,
            gender.lower() if gender else 'male',
            nationality if nationality else 'Unknown',
            employment_type.lower().replace(' ', '_') if employment_type else 'full_time',
            work_location if work_location else 'Unknown',
            hire_date if hire_date else '2024-01-01',
            position,
            department
        ])

# Save the workbook
wb.save(output_file)
print(f"✓ Excel file created: {output_file}")
print(f"  Ready to import via the frontend Import Excel feature!")
