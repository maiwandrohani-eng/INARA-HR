# Organization Chart Feature

## Overview
The Organization Chart feature provides a visual hierarchical view of all employees in the organization, allowing HR administrators and supervisors to view and manage the reporting structure.

## Features

### 1. **Visual Hierarchy Display**
- Tree-like structure showing reporting relationships
- Expandable/collapsible nodes for easy navigation
- Color-coded levels (top leadership highlighted)
- Direct report counts displayed on each node

### 2. **Employee Information**
Each employee node displays:
- Full name and profile
- Position title
- Department
- Contact information (email, phone)
- Employment status badge
- Number of direct reports

### 3. **Edit Hierarchy**
Supervisors and HR admins can:
- Change an employee's manager (reporting structure)
- Reassign employees to different departments
- Prevent circular reporting relationships (validated)

### 4. **Statistics Dashboard**
- Total number of employees
- Number of departments
- Number of leadership positions

## User Interface

### Access
1. Login as a supervisor or HR admin
2. Navigate to Dashboard
3. Click on the "Organization Chart" tab

### Navigation
- **Expand All**: Shows the complete hierarchy
- **Collapse All**: Collapses all nodes for overview
- **Individual Toggle**: Click chevron icons to expand/collapse specific branches

### Editing Hierarchy
1. Click the **Edit** button (pencil icon) on any employee card
2. In the dialog:
   - Select new manager from dropdown
   - Select department from dropdown
3. Click **Save Changes**

## API Endpoints

### Get Organization Chart
```http
GET /api/v1/employees/organization-chart
Authorization: Bearer {token}
```

Returns all active employees with their department, position, and manager relationships.

**Response:**
```json
[
  {
    "id": "uuid",
    "employee_number": "EMP001",
    "first_name": "John",
    "last_name": "Doe",
    "work_email": "john.doe@inara.org",
    "phone": "+93123456789",
    "status": "active",
    "position": {
      "id": "uuid",
      "title": "Chief Executive Officer",
      "code": "CEO"
    },
    "department": {
      "id": "uuid",
      "name": "Executive",
      "code": "EXEC"
    },
    "manager_id": null
  }
]
```

### Update Employee Hierarchy
```http
PATCH /api/v1/employees/{employee_id}/hierarchy
Authorization: Bearer {token}
Content-Type: application/json

{
  "manager_id": "uuid",
  "department_id": "uuid"
}
```

Updates an employee's reporting manager and/or department.

**Validations:**
- Employee cannot be their own manager
- Manager must exist
- Prevents circular reporting relationships
- Department must exist if provided

**Response:**
```json
{
  "id": "uuid",
  "employee_number": "EMP002",
  "first_name": "Jane",
  "last_name": "Smith",
  "manager_id": "uuid",
  "department_id": "uuid",
  "department": {...},
  "position": {...}
}
```

### Get Departments
```http
GET /api/v1/employees/departments
Authorization: Bearer {token}
```

Returns all active departments.

### Get Positions
```http
GET /api/v1/employees/positions
Authorization: Bearer {token}
```

Returns all active positions.

## Database Schema

### Tables Used

**employees**
- `id` - Employee UUID
- `first_name`, `last_name` - Name
- `work_email` - Email
- `manager_id` - Foreign key to employees (self-referential)
- `department_id` - Foreign key to departments
- `position_id` - Foreign key to positions
- `status` - Employment status

**departments**
- `id` - Department UUID
- `name` - Department name
- `code` - Department code

**positions**
- `id` - Position UUID
- `title` - Position title
- `code` - Position code

## Security

### Permissions Required
- **View Organization Chart**: `hr:read` permission
- **Edit Hierarchy**: `hr:write` permission

### Access Control
- Regular employees cannot access organization chart
- Supervisors can view but may have limited edit capabilities
- HR admins have full access to view and edit

## Business Rules

1. **Circular Reference Prevention**: The system prevents creating circular reporting structures where employee A reports to B, B reports to C, and C reports back to A.

2. **Top-Level Employees**: Employees with `manager_id = null` are considered top-level (CEO, President, etc.)

3. **Validation on Update**:
   - Cannot set self as manager
   - Manager must be an active employee
   - Department must exist
   - Validates against circular references

4. **Hierarchy Depth**: No limit on hierarchy depth, but recommended to keep organizational structure reasonable (4-6 levels)

## Visual Design

### Color Scheme
- **Leadership Level** (no manager): Pink/Cyan gradient background
- **Regular Employees**: White background
- **Status Badges**: 
  - Active: Green
  - On Leave: Yellow
  - Terminated: Gray

### Icons
- 👤 User profile
- 🏢 Department/Position
- 📧 Email
- 📞 Phone
- 👥 Direct reports count
- ✏️ Edit button

## Testing

### Test Scenarios

1. **View Full Hierarchy**
   - Login as HR admin
   - Navigate to Organization Chart
   - Verify all employees displayed
   - Verify hierarchy structure correct

2. **Edit Reporting Structure**
   - Click edit on an employee
   - Change manager
   - Save changes
   - Verify hierarchy updates

3. **Prevent Circular Reference**
   - Try to create circular reporting
   - System should reject with error message

4. **Expand/Collapse Nodes**
   - Click expand/collapse buttons
   - Verify nodes show/hide correctly

5. **Department Reassignment**
   - Edit employee
   - Change department
   - Verify update reflects in chart

## Future Enhancements

1. **Export Organization Chart**: PDF/PNG export of hierarchy
2. **Search/Filter**: Find employees by name, department, or position
3. **Bulk Updates**: Move multiple employees at once
4. **Org Chart Templates**: Pre-defined structures for new departments
5. **Historical View**: See organizational changes over time
6. **Drag-and-Drop**: Drag employees to new positions in hierarchy
7. **Print View**: Printer-friendly format
8. **Department View**: Filter by specific department
9. **Position Level Indicators**: Show organizational levels/bands
10. **Vacancy Indicators**: Show open positions in org chart

## Troubleshooting

### Issue: Organization Chart Empty
**Cause**: No employees in database or all marked as deleted
**Solution**: 
- Check database: `SELECT COUNT(*) FROM employees WHERE is_deleted = false;`
- Import employees if needed

### Issue: Cannot Edit Hierarchy
**Cause**: Insufficient permissions
**Solution**: Ensure user has `hr:write` permission

### Issue: "Circular Reference" Error
**Cause**: Attempted update would create loop in reporting structure
**Solution**: Review reporting chain and select different manager

### Issue: Changes Not Saving
**Cause**: Network error or validation failure
**Solution**: 
- Check browser console for errors
- Verify manager and department exist
- Check API logs for error details

## Support

For issues or questions about the Organization Chart feature:
- Check API documentation: http://localhost:8000/api/v1/docs
- Review logs: `docker logs inara-api`
- Contact: [support email]

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Feature Status**: ✅ Production Ready
