-- Verify the employment_type index exists and is correct
-- Run this in Neon.tech SQL Editor to confirm

SELECT 
    indexname, 
    indexdef,
    tablename
FROM pg_indexes 
WHERE tablename = 'employees' 
    AND indexname = 'idx_employees_employment_type';

-- Expected output should show:
-- indexname: idx_employees_employment_type
-- indexdef: CREATE INDEX idx_employees_employment_type ON employees (employment_type) WHERE (is_deleted = false)
