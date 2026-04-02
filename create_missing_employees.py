#!/usr/bin/env python3
"""
Create employee records for all users that don't have one.
Links each user to a new employee record via user_id.
Skips system accounts (admin, hr).
"""
import os
import sys
import uuid
from datetime import datetime, date

# Add API to path
sys.path.insert(0, '/Users/maiwand/INARA-HR/apps/api')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://inara_user:inara_password@localhost:5432/inara_hris"

# Accounts that should NOT get employee records
SKIP_EMAILS = {'admin@inara.org', 'hr@inara.org'}

def main():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Get the current max employee number
        result = conn.execute(text(
            "SELECT employee_number FROM employees ORDER BY employee_number DESC LIMIT 1"
        ))
        row = result.fetchone()
        if row and row[0] and row[0].startswith('EMP-'):
            try:
                current_max = int(row[0].split('-')[1])
            except ValueError:
                current_max = 1
        else:
            current_max = 1

        # Fetch all users without an employee record, excluding system accounts
        result = conn.execute(text("""
            SELECT u.id, u.email, u.first_name, u.last_name, u.country_code, u.created_at
            FROM users u
            LEFT JOIN employees e ON u.id = e.user_id
            WHERE e.id IS NULL
              AND u.is_deleted = false
              AND u.email NOT IN :skip_emails
            ORDER BY u.created_at
        """), {"skip_emails": tuple(SKIP_EMAILS)})

        users_to_create = result.fetchall()
        print(f"Found {len(users_to_create)} users without employee records.\n")

        created = 0
        failed = 0

        for user in users_to_create:
            user_id, email, first_name, last_name, country_code, created_at = user
            current_max += 1
            emp_number = f"EMP-{current_max:03d}"
            emp_id = str(uuid.uuid4())
            now = datetime.utcnow()
            hire_date = created_at.date() if created_at else date.today()

            try:
                conn.execute(text("""
                    INSERT INTO employees (
                        id, user_id, employee_number, first_name, last_name,
                        work_email, status, employment_type, hire_date,
                        country_code, created_at, updated_at, is_deleted
                    ) VALUES (
                        :id, :user_id, :employee_number, :first_name, :last_name,
                        :work_email, 'ACTIVE', 'FULL_TIME', :hire_date,
                        :country_code, :created_at, :updated_at, false
                    )
                """), {
                    "id": emp_id,
                    "user_id": str(user_id),
                    "employee_number": emp_number,
                    "first_name": first_name,
                    "last_name": last_name,
                    "work_email": email,
                    "hire_date": hire_date,
                    "country_code": country_code if country_code else "LB",
                    "created_at": now,
                    "updated_at": now,
                })
                conn.commit()
                print(f"  ✓ {emp_number}  {first_name} {last_name} ({email})")
                created += 1
            except Exception as e:
                conn.rollback()
                print(f"  ✗ FAILED  {first_name} {last_name} ({email}): {e}")
                current_max -= 1  # reuse the number
                failed += 1

        print(f"\n{'='*50}")
        print(f"Created : {created}")
        print(f"Failed  : {failed}")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
