-- Update all unverified users to verified
-- Run this with: railway run psql < verify_users.sql

UPDATE users 
SET is_verified = true 
WHERE is_verified = false;

-- Show results
SELECT 
    email, 
    first_name, 
    last_name, 
    is_verified, 
    is_active 
FROM users 
ORDER BY email;
