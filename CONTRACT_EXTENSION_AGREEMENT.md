# Contract Extension Agreement Documentation

## Overview
The INARA HR system supports contract extensions, allowing HR/CEO to extend employee contracts beyond their original end date. Employees must digitally sign/accept extensions before they become active.

## ✅ Current Implementation Status

### Backend (API) - **COMPLETE**
✅ Database model (`contract_extensions` table)
✅ API endpoints:
- `POST /api/v1/employee-files/extensions` - Create extension
- `POST /api/v1/employee-files/extensions/{id}/accept` - Employee accepts
- `GET /api/v1/employee-files/extensions/pending` - Get pending extensions
- `GET /api/v1/employee-files/extensions/{id}` - Get specific extension

### Frontend - **COMPLETE**
✅ Service layer has all extension methods
✅ UI displays pending extensions in Personal File tab
✅ Employee can accept extensions via button

### ❌ MISSING: Agreement PDF Generation
The system currently does **NOT** generate a PDF agreement document for contract extensions. This should be added.

## How Contract Extensions Work

### Current Flow:

1. **HR/CEO Creates Extension** (via API or admin panel)
   - Selects existing contract
   - Specifies new start/end dates
   - Optional: New salary, position, location
   - System generates extension number (e.g., Extension #1, #2)
   - Status: `PENDING`
   - Sets expiry date (7 days before new start date)

2. **Employee Receives Notification** (UI notification - email not yet implemented)
   - Extension appears in Personal File → Extensions tab
   - Shows all changes: dates, salary changes, position changes
   - Status badge shows "PENDING"

3. **Employee Accepts Extension**
   - Clicks "Accept Extension" button
   - Digital signature captured (IP address + timestamp)
   - Status changes to: `ACCEPTED`

4. **Contract Updated**
   - Original contract end date is extended
   - Salary/position updated if changed
   - Contract status remains `ACTIVE`

### Extension Expiration:
- If employee doesn't accept by expiry date → Status: `EXPIRED`
- Extension can no longer be accepted
- HR must create new extension

## Database Schema

```sql
Table: contract_extensions
- id (UUID, Primary Key)
- contract_id (UUID, Foreign Key → employment_contracts)
- employee_id (UUID, Foreign Key → employees)
- extension_number (Integer) - Sequential: 1, 2, 3...
- new_start_date (Date) - When extension period starts
- new_end_date (Date) - New contract end date
- new_monthly_salary (Decimal) - Optional salary change
- salary_change_reason (Text) - Why salary changed
- new_position_title (String) - Optional position change
- new_location (String) - Optional location change
- terms_changes (Text) - Other changes to contract terms
- document_id (UUID, Foreign Key) - Link to signed agreement PDF (not used yet)
- status (Enum) - PENDING, ACCEPTED, EXPIRED, REJECTED
- expires_at (DateTime) - Deadline for employee acceptance
- employee_accepted_at (DateTime) - When employee signed
- employee_signature_ip (String) - IP for audit trail
- created_by (UUID, Foreign Key)
- created_at (DateTime)
- updated_at (DateTime)
- is_deleted (Boolean)
- deleted_at (DateTime)
- country_code (String)
```

## API Usage Examples

### Create Extension (HR/CEO)
```bash
curl -X POST http://localhost:8000/api/v1/employee-files/extensions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "abc-123-def-456",
    "employee_id": "d7b1e4a5-3424-4dcf-be9b-fd9cbaecd8a1",
    "new_start_date": "2026-01-01",
    "new_end_date": "2026-12-31",
    "new_monthly_salary": 12000,
    "salary_change_reason": "Annual performance increase",
    "new_position_title": "Senior CEO",
    "terms_changes": "Additional vacation days: 30"
  }'
```

### Employee Accepts Extension
```bash
curl -X POST http://localhost:8000/api/v1/employee-files/extensions/{extension_id}/accept \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_signature_ip": "192.168.1.100"
  }'
```

### Get Pending Extensions
```bash
# For specific employee
curl -X GET http://localhost:8000/api/v1/employee-files/extensions/pending?employee_id={id} \
  -H "Authorization: Bearer {token}"

# All pending (HR/CEO view)
curl -X GET http://localhost:8000/api/v1/employee-files/extensions/pending \
  -H "Authorization: Bearer {token}"
```

## UI Location

**File**: `/apps/frontend/components/dashboard/PersonalFileTab.tsx`

**Tab**: Extensions

**Features**:
- Lists all pending extensions for employee
- Shows extension details (dates, salary, position)
- "Accept Extension" button (green) - only for PENDING status
- Status badges (PENDING, ACCEPTED, EXPIRED)
- Displays all changes in readable format

## ⚠️ Missing Features

### 1. PDF Agreement Generation ❌
**Status**: NOT IMPLEMENTED

**What's Needed**:
- Generate PDF document with extension terms
- Include:
  - Original contract details
  - Extension details (dates, salary, position)
  - Terms and conditions
  - Signature section
  - Employee acceptance timestamp
- Store PDF in `personal_file_documents` table
- Link via `document_id` in `contract_extensions`

**Implementation Plan**:
```python
# Add to /apps/api/core/pdf_generator.py
def generate_extension_agreement(
    employee_name: str,
    employee_number: str,
    original_contract: dict,
    extension: dict
) -> BytesIO:
    """Generate contract extension agreement PDF"""
    # Use reportlab to create professional agreement
    # Include all extension terms
    # Add signature block
    # Return PDF buffer
```

### 2. Email Notifications ❌
**Status**: NOT IMPLEMENTED

**What's Needed**:
- Notify employee when extension is created
- Reminder emails before expiry
- Confirmation email when accepted

### 3. Rejection Option ❌
**Status**: NOT IMPLEMENTED

**What's Needed**:
- Allow employee to reject extension
- Add rejection reason field
- Update status to `REJECTED`

### 4. HR/Admin UI for Creating Extensions ❌
**Status**: NOT IMPLEMENTED

**What's Needed**:
- Form for HR to create extensions
- Currently only API is available
- Should be in Employee Management → Contracts section

## Permissions

| Role | Create Extension | View | Accept | Reject |
|------|-----------------|------|--------|--------|
| Employee | ❌ | ✅ (Own only) | ✅ (Own only) | ❌ (Not yet implemented) |
| HR | ✅ | ✅ (All) | ❌ | ❌ |
| CEO | ✅ | ✅ (All) | ❌ | ❌ |
| Supervisor | ❌ | ✅ (Reports only) | ❌ | ❌ |

## Testing

### Test Data
You currently have 1 pending extension in the database:
```sql
SELECT * FROM contract_extensions 
WHERE employee_id = 'd7b1e4a5-3424-4dcf-be9b-fd9cbaecd8a1';
```

### Test Steps:
1. Login as maiwand@inara.org
2. Go to Personal File → Extensions tab
3. View pending extension details
4. Click "Accept Extension"
5. Verify status changes to ACCEPTED

## Comparison: Resignations vs Extensions

| Feature | Resignations | Extensions |
|---------|-------------|-----------|
| Employee Initiates | ✅ | ❌ |
| Employee Accepts | N/A | ✅ |
| Multi-level Approval | ✅ (Supervisor→HR→CEO) | ❌ (Just employee acceptance) |
| PDF Generation | ❌ | ❌ |
| Email Notifications | ❌ | ❌ |
| UI for Submission | ✅ **NEW** | ❌ (API only) |
| UI for Viewing | ✅ | ✅ |
| UI for Approval | ❌ | ✅ (Accept button) |

## Recommended Implementation Priority

### High Priority:
1. **PDF Agreement Generation** - Create professional extension agreement document
2. **HR UI for Creating Extensions** - Form in admin panel to create extensions
3. **Email Notifications** - Notify employees of pending extensions

### Medium Priority:
4. **Rejection Option** - Allow employees to decline extensions
5. **Extension History** - Show all past extensions with audit trail
6. **Bulk Extensions** - Create extensions for multiple employees

### Low Priority:
7. **Template System** - Customizable agreement templates
8. **Digital Signature** - More robust signature capture (not just IP)
9. **Expiry Reminders** - Auto-remind employees before expiry

---

**Last Updated**: December 8, 2025
**Status**: ⚠️ Partially Implemented (Backend complete, PDF generation missing)
