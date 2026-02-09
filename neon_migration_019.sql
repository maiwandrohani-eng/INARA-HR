-- Migration 019: Add index on employment_type for faster filtering
-- Run this in Neon.tech SQL Editor

-- Add index on employment_type (partial index for non-deleted employees)
CREATE INDEX IF NOT EXISTS idx_employees_employment_type 
ON employees (employment_type)
WHERE is_deleted = false;

-- Verify the index was created
SELECT 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE tablename = 'employees' 
    AND indexname = 'idx_employees_employment_type';
