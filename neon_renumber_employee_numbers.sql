BEGIN;

WITH ranked_employees AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            ORDER BY
                CASE WHEN COALESCE(is_deleted, false) THEN 1 ELSE 0 END,
                CASE
                    WHEN employee_number ~ '^EMP-[0-9]+$'
                    THEN CAST(SPLIT_PART(employee_number, '-', 2) AS INT)
                    ELSE 2147483647
                END,
                created_at,
                first_name,
                last_name,
                id
        ) AS new_sequence
    FROM employees
),
temporary_numbers AS (
    UPDATE employees e
    SET employee_number = 'TMP-' || REPLACE(e.id::text, '-', '')
    FROM ranked_employees r
    WHERE e.id = r.id
    RETURNING e.id
),
final_numbers AS (
    UPDATE employees e
    SET employee_number = 'EMP-' || LPAD(r.new_sequence::text, 3, '0')
    FROM ranked_employees r
    WHERE e.id = r.id
    RETURNING e.id, e.employee_number
)
UPDATE payroll_entries pe
SET employee_number = e.employee_number
FROM employees e
WHERE pe.employee_id = e.id
  AND pe.employee_number IS DISTINCT FROM e.employee_number;

COMMIT;

SELECT employee_number, first_name, last_name, work_email
FROM employees
ORDER BY employee_number;
