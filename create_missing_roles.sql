-- Create missing roles with their permissions

-- 1. Create employee role
INSERT INTO roles (id, name, display_name, description, is_system, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'employee',
    'Employee',
    'Regular Employee - basic access',
    FALSE,
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'employee');

-- 2. Create finance_manager role
INSERT INTO roles (id, name, display_name, description, is_system, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'finance_manager',
    'Finance Manager',
    'Finance Manager - payroll and finance access',
    TRUE,
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'finance_manager');

-- 3. Create hr_admin role
INSERT INTO roles (id, name, display_name, description, is_system, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'hr_admin',
    'HR Administrator',
    'HR Administrator - full HR access',
    TRUE,
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'hr_admin');

-- 4. Create hr_manager role
INSERT INTO roles (id, name, display_name, description, is_system, is_deleted, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'hr_manager',
    'HR Manager',
    'HR Manager - read/write access',
    TRUE,
    FALSE,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'hr_manager');

-- 5. Assign permissions to employee role (hr:read only)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'employee'
  AND p.name = 'hr:read'
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 6. Assign permissions to finance_manager role (hr:read, hr:write)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'finance_manager'
  AND p.name IN ('hr:read', 'hr:write')
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 7. Assign permissions to hr_admin role (hr:admin, hr:read, hr:write)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'hr_admin'
  AND p.name IN ('hr:admin', 'hr:read', 'hr:write')
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- 8. Assign permissions to hr_manager role (hr:read, hr:write)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'hr_manager'
  AND p.name IN ('hr:read', 'hr:write')
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
  );

-- Show all roles with their permission counts
SELECT 'All roles with permission counts:' as status;
SELECT r.name as role, r.display_name, COUNT(rp.permission_id) as permission_count
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
GROUP BY r.name, r.display_name
ORDER BY r.name;

-- Show detailed permissions per role
SELECT 'Detailed permissions per role:' as status;
SELECT r.name as role, p.name as permission
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
ORDER BY r.name, p.name;
