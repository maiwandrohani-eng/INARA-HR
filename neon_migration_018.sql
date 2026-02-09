-- Migration 018: Add additional employee fields
-- Blood type, work type, medical conditions, second emergency contact
-- Run this in Neon.tech SQL Editor

-- Step 1: Create work_type enum (if it doesn't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'worktype') THEN
        CREATE TYPE worktype AS ENUM ('on_site', 'remote', 'hybrid');
    END IF;
END $$;

-- Step 2: Add new columns to employees table
ALTER TABLE employees 
    ADD COLUMN IF NOT EXISTS blood_type VARCHAR(10),
    ADD COLUMN IF NOT EXISTS medical_conditions TEXT,
    ADD COLUMN IF NOT EXISTS emergency_contact_2_name VARCHAR(200),
    ADD COLUMN IF NOT EXISTS emergency_contact_2_phone VARCHAR(20),
    ADD COLUMN IF NOT EXISTS emergency_contact_2_relationship VARCHAR(100),
    ADD COLUMN IF NOT EXISTS emergency_contact_2_note TEXT,
    ADD COLUMN IF NOT EXISTS work_type worktype;

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    udt_name
FROM information_schema.columns 
WHERE table_name = 'employees' 
    AND column_name IN (
        'blood_type', 
        'medical_conditions', 
        'emergency_contact_2_name', 
        'emergency_contact_2_phone', 
        'emergency_contact_2_relationship', 
        'emergency_contact_2_note', 
        'work_type'
    )
ORDER BY column_name;
