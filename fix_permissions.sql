-- Fix Role Permissions - Pure SQL Script
-- Run this on Railway to add permissions to roles

-- 1. Create permissions if they don't exist
INSERT INTO permissions (id, name, resource, action, description, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(), 
    'admin:all', 
    'admin', 
    'all', 
    'Full system administration',
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'admin:all');

INSERT INTO permissions (id, name, resource, action, description, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(), 
    'hr:admin', 
    'hr', 
    'admin', 
    'Full HR administration',
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'hr:admin');

INSERT INTO permissions (id, name, resource, action, description, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(), 
    'hr:read', 
    'hr', 
    'read', 
    'Read HR data',
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'hr:read');

INSERT INTO permissions (id, name, resource, action, description, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(), 
    'hr:write', 
    'hr', 
    'write', 
    'Write/update HR data',
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = 'hr:write');

-- 2. Link admin:all permission to admin, super_admin, ceo roles
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name IN ('admin', 'super_admin', 'ceo')
  AND p.name = 'admin:all'
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 3. Link hr:admin to admin, super_admin, ceo, hr_admin roles
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name IN ('admin', 'super_admin', 'ceo', 'hr_admin')
  AND p.name = 'hr:admin'
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 4. Link hr:read to all roles
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE p.name = 'hr:read'
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 5. Link hr:write to admin, super_admin, ceo, hr_admin, hr_manager, finance_manager
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name IN ('admin', 'super_admin', 'ceo', 'hr_admin', 'hr_manager', 'finance_manager')
  AND p.name = 'hr:write'
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- Show results
SELECT 'Roles and their permission counts:' as status;
SELECT r.name, COUNT(rp.permission_id) as permission_count 
FROM roles r 
LEFT JOIN role_permissions rp ON r.id = rp.role_id 
GROUP BY r.name 
ORDER BY r.name;
