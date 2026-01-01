#!/usr/bin/env python3
"""Test script to verify payroll API endpoint"""

import requests
import json

# First, let's login to get a token
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {
    "email": "admin@inara.org",
    "password": "Admin@123"
}

print("=" * 60)
print("1. Testing Login...")
print("=" * 60)

try:
    login_response = requests.post(login_url, json=login_data)
    print(f"Status Code: {login_response.status_code}")
    
    if login_response.ok:
        login_result = login_response.json()
        token = login_result.get('access_token')
        print(f"✅ Login successful! Got token: {token[:20]}...")
        
        # Now try to create payroll
        print("\n" + "=" * 60)
        print("2. Testing Payroll Creation...")
        print("=" * 60)
        
        payroll_url = "http://localhost:8000/api/v1/payroll/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payroll_data = {
            "month": 12,
            "year": 2024,
            "payment_date": "2024-12-31",
            "entries": [{
                "employee_id": "312fafa9-4ad1-46c2-a5d9-4c58a1595c11",
                "employee_number": "EMP-001",
                "first_name": "Maiwand",
                "last_name": "Rohani",
                "position": "Founder & CEO",
                "department": "Executive",
                "basic_salary": 99.0,
                "allowances": 37.0,
                "deductions": 67.0,
                "currency": "USD"
            }]
        }
        
        print(f"Sending payload:")
        print(json.dumps(payroll_data, indent=2))
        
        payroll_response = requests.post(payroll_url, json=payroll_data, headers=headers)
        print(f"\nStatus Code: {payroll_response.status_code}")
        print(f"Response Headers: {dict(payroll_response.headers)}")
        
        if payroll_response.ok:
            result = payroll_response.json()
            print(f"✅ Payroll created successfully!")
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"❌ Payroll creation failed!")
            print(f"Error Response: {payroll_response.text}")
            
    else:
        print(f"❌ Login failed!")
        print(f"Error: {login_response.text}")
        
except Exception as e:
    print(f"❌ Exception occurred: {str(e)}")
    import traceback
    traceback.print_exc()
