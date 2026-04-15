-- Migration 020: Add missing columns to employees table
-- Adds blood_type, medical_conditions, work_type, and emergency_contact_2_* columns
-- These columns were added to the SQLAlchemy model but not yet migrated to the database

ALTER TABLE employees
  ADD COLUMN IF NOT EXISTS blood_type VARCHAR(10),
  ADD COLUMN IF NOT EXISTS medical_conditions TEXT,
  ADD COLUMN IF NOT EXISTS work_type VARCHAR(20),
  ADD COLUMN IF NOT EXISTS emergency_contact_2_name VARCHAR(200),
  ADD COLUMN IF NOT EXISTS emergency_contact_2_phone VARCHAR(20),
  ADD COLUMN IF NOT EXISTS emergency_contact_2_relationship VARCHAR(100),
  ADD COLUMN IF NOT EXISTS emergency_contact_2_note TEXT;
