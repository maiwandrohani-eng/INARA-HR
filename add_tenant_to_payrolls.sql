-- Add tenant support to payrolls table
-- Run this directly in PostgreSQL if migration fails

-- Add country_code column
ALTER TABLE payrolls ADD COLUMN IF NOT EXISTS country_code VARCHAR(2);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS ix_payrolls_country_code ON payrolls(country_code);
CREATE INDEX IF NOT EXISTS ix_payrolls_period_tenant ON payrolls(month, year, country_code);

-- Optional: Update existing payrolls to have a default country_code
-- UPDATE payrolls SET country_code = 'US' WHERE country_code IS NULL;

COMMENT ON COLUMN payrolls.country_code IS 'ISO 3166-1 alpha-2 country code for multi-tenant support';
