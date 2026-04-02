-- ============================================================
-- Sync Users → Employees (Neon Production)
-- Run this in the Neon SQL Editor
-- Safe to run multiple times — only creates MISSING records
-- ============================================================

DO $$
DECLARE
    rec         RECORD;
    max_num     INT := 0;
    next_num    INT;
    emp_number  TEXT;
    emp_id      UUID;
    created_count INT := 0;
BEGIN
    -- Find the current highest EMP-xxx number
    SELECT COALESCE(MAX(CAST(SPLIT_PART(employee_number, '-', 2) AS INT)), 0)
    INTO max_num
    FROM employees
    WHERE employee_number ~ '^EMP-[0-9]+$';

    -- Loop over every user that has no employee record
    -- Excludes system accounts: admin@inara.org and hr@inara.org
    FOR rec IN
        SELECT
            u.id          AS user_id,
            u.email,
            u.first_name,
            u.last_name,
            u.country_code,
            u.created_at
        FROM users u
        LEFT JOIN employees e ON u.id = e.user_id
        WHERE e.id IS NULL
          AND u.is_deleted = false
          AND u.email NOT IN ('admin@inara.org', 'hr@inara.org')
        ORDER BY u.created_at
    LOOP
        -- Assign next sequential employee number
        max_num    := max_num + 1;
        next_num   := max_num;
        emp_number := 'EMP-' || LPAD(next_num::TEXT, 3, '0');
        emp_id     := gen_random_uuid();

        INSERT INTO employees (
            id,
            user_id,
            employee_number,
            first_name,
            last_name,
            work_email,
            status,
            employment_type,
            hire_date,
            country_code,
            created_at,
            updated_at,
            is_deleted
        ) VALUES (
            emp_id,
            rec.user_id,
            emp_number,
            rec.first_name,
            rec.last_name,
            rec.email,
            'ACTIVE',
            'FULL_TIME',
            COALESCE(rec.created_at::DATE, CURRENT_DATE),
            COALESCE(NULLIF(rec.country_code, ''), 'LB'),
            NOW(),
            NOW(),
            false
        );

        created_count := created_count + 1;
        RAISE NOTICE 'Created % – % % (%)', emp_number, rec.first_name, rec.last_name, rec.email;
    END LOOP;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Done. Employee records created: %', created_count;
    RAISE NOTICE '========================================';
END;
$$;

-- Verify result
SELECT COUNT(*) AS total_employees FROM employees WHERE is_deleted = false;
SELECT employee_number, first_name, last_name, work_email, status
FROM employees
WHERE is_deleted = false
ORDER BY employee_number;
