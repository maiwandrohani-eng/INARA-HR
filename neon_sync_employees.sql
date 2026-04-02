-- ============================================================
-- Sync Users → Employees (Neon Production)
-- Run this in the Neon SQL Editor
-- Safe to run multiple times — only creates MISSING records
-- ============================================================

-- Step 1: Link existing employees (manually added) to their user accounts
UPDATE employees e
SET user_id    = u.id,
    updated_at = NOW()
FROM users u
WHERE e.work_email = u.email
  AND e.user_id IS NULL
  AND u.is_deleted = false;

-- Step 2: Create employee records for every user that still has none
WITH max_emp AS (
    SELECT COALESCE(MAX(CAST(SPLIT_PART(employee_number, '-', 2) AS INT)), 0) AS max_num
    FROM employees
    WHERE employee_number ~ '^EMP-[0-9]+$'
),
new_users AS (
    SELECT
        u.id          AS user_id,
        u.email,
        u.first_name,
        u.last_name,
        u.country_code,
        u.created_at,
        ROW_NUMBER() OVER (ORDER BY u.created_at) AS rn
    FROM users u
    LEFT JOIN employees e ON u.id = e.user_id
    WHERE e.id IS NULL
      AND u.is_deleted = false
      AND u.email NOT IN ('admin@inara.org', 'hr@inara.org')
      AND u.email NOT IN (SELECT work_email FROM employees WHERE work_email IS NOT NULL)
)
INSERT INTO employees (
    id, user_id, employee_number,
    first_name, last_name, work_email,
    status, employment_type, hire_date,
    country_code, created_at, updated_at, is_deleted
)
SELECT
    gen_random_uuid(),
    nu.user_id,
    'EMP-' || LPAD((m.max_num + nu.rn)::TEXT, 3, '0'),
    nu.first_name,
    nu.last_name,
    nu.email,
    'ACTIVE',
    'FULL_TIME',
    COALESCE(nu.created_at::DATE, CURRENT_DATE),
    COALESCE(NULLIF(nu.country_code, ''), 'LB'),
    NOW(),
    NOW(),
    false
FROM new_users nu
CROSS JOIN max_emp m;

-- Verify result
SELECT COUNT(*) AS total_employees FROM employees WHERE is_deleted = false;
SELECT employee_number, first_name, last_name, work_email, status
FROM employees
WHERE is_deleted = false
ORDER BY employee_number;
