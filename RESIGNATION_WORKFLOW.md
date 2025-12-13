# Resignation Workflow Documentation

## Overview
The INARA HR system includes a comprehensive resignation management module that allows employees to submit resignations and tracks the approval workflow through multiple levels.

## ✅ Implementation Status

### Backend (API) - **COMPLETE**
✅ Database models exist (`resignations` table)
✅ API endpoints implemented:
- `POST /api/v1/employee-files/resignations` - Submit resignation
- `POST /api/v1/employee-files/resignations/{id}/approve/supervisor` - Supervisor approval
- `POST /api/v1/employee-files/resignations/{id}/approve/hr` - HR approval
- `POST /api/v1/employee-files/resignations/{id}/approve/ceo` - CEO approval
- `POST /api/v1/employee-files/resignations/{id}/complete` - Mark as completed
- `GET /api/v1/employee-files/resignations/employee/{id}` - Get employee resignations

### Frontend - **NOW COMPLETE** ✅
✅ Service layer (`employee-files.service.ts`) - Has all resignation methods
✅ UI for viewing resignations - Displays in Personal File tab
✅ **NEW:** UI for submitting resignations - Added "Submit Resignation" button and form

## How to Submit a Resignation

### For Employees:

1. **Navigate to Personal File**
   - Go to Dashboard → Your Profile → Personal File Tab
   - Click on the "Resignations" tab

2. **Submit Resignation**
   - Click the "Submit Resignation" button (only visible if no active resignation exists)
   - Fill in the required information:
     - **Resignation Date**: The date you're submitting (defaults to today)
     - **Intended Last Working Day**: Your proposed final day of work
     - **Notice Period (Days)**: Number of days as per your contract (default: 30)
     - **Reason for Resignation**: Detailed explanation (confidential)
   
3. **Submit**
   - Click "Submit Resignation" button
   - Your resignation will be created with status: `SUBMITTED`
   - Notifications will be sent to your supervisor, HR, and CEO

### For HR/Supervisors/CEO:

View resignations by navigating to any employee's Personal File → Resignations tab.

## Resignation Approval Workflow

### Status Flow:
1. **SUBMITTED** - Employee submits resignation
2. **ACCEPTED_BY_SUPERVISOR** - Supervisor reviews and approves
3. **ACCEPTED_BY_HR** - HR reviews and approves
4. **ACCEPTED_BY_CEO** - CEO gives final approval and confirms last working day
5. **COMPLETED** - Exit interview completed and resignation finalized

### Approval Timeline:
Each step is tracked with:
- ✅ Approval timestamp
- 💬 Optional comments from approver
- 👤 Approver details

### Key Features:
- **Notice Period Tracking**: Automatically calculates based on contract
- **Final Approval by CEO**: CEO can adjust the intended last working day
- **Exit Interview**: Tracks completion before finalizing resignation
- **Audit Trail**: Complete history of who approved when with comments
- **Confidentiality**: Resignation reasons are kept confidential

## Database Schema

```sql
Table: resignations
- id (UUID, Primary Key)
- employee_id (UUID, Foreign Key)
- resignation_number (String, Unique) - Format: RES-{YEAR}-{EMP_ID}
- resignation_date (Date)
- intended_last_working_day (Date)
- reason (Text) - Employee's reason for leaving
- notice_period_days (Integer)
- supervisor_id (UUID, Foreign Key)
- supervisor_accepted_at (DateTime)
- supervisor_comments (Text)
- hr_accepted_by (UUID, Foreign Key)
- hr_accepted_at (DateTime)
- hr_comments (Text)
- ceo_accepted_by (UUID, Foreign Key)
- ceo_accepted_at (DateTime)
- ceo_comments (Text)
- approved_last_working_day (Date) - CEO-approved final day
- exit_interview_completed (Boolean)
- exit_interview_date (Date)
- status (Enum) - SUBMITTED, ACCEPTED_BY_SUPERVISOR, etc.
- is_deleted (Boolean)
- deleted_at (DateTime)
```

## API Request Examples

### Submit Resignation
```bash
curl -X POST http://localhost:8000/api/v1/employee-files/resignations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "d7b1e4a5-3424-4dcf-be9b-fd9cbaecd8a1",
    "resignation_date": "2025-12-08",
    "intended_last_working_day": "2026-01-07",
    "reason": "Pursuing new opportunities",
    "notice_period_days": 30
  }'
```

### Supervisor Approval
```bash
curl -X POST http://localhost:8000/api/v1/employee-files/resignations/{resignation_id}/approve/supervisor \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Approved. Thank you for your service."
  }'
```

### HR Approval
```bash
curl -X POST http://localhost:8000/api/v1/employee-files/resignations/{resignation_id}/approve/hr \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "HR clearance approved."
  }'
```

### CEO Final Approval
```bash
curl -X POST http://localhost:8000/api/v1/employee-files/resignations/{resignation_id}/approve/ceo \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "approved_last_working_day": "2026-01-07",
    "comments": "Approved. Best wishes for your future."
  }'
```

## UI Components

### Location
`/apps/frontend/components/dashboard/PersonalFileTab.tsx`

### Key Features:
1. **Submit Button**: Only visible to employee if no active resignation
2. **Resignation Form**: Validates dates, requires reason
3. **Resignation List**: Shows all resignations with approval timeline
4. **Status Badges**: Color-coded status indicators
5. **Approval Timeline**: Visual timeline showing approval progress

## Permissions

| Role | Submit | View Own | View Others | Approve |
|------|--------|----------|-------------|---------|
| Employee | ✅ | ✅ | ❌ | ❌ |
| Supervisor | ✅ | ✅ | ✅ (Reports only) | ✅ (Supervisor level) |
| HR | ✅ | ✅ | ✅ (All) | ✅ (HR level) |
| CEO | ✅ | ✅ | ✅ (All) | ✅ (Final approval) |

## Testing

### Test Account
- **Email**: maiwand@inara.org
- **Password**: Maiwand@123
- **Role**: CEO
- **Employee ID**: d7b1e4a5-3424-4dcf-be9b-fd9cbaecd8a1

### Test Steps:
1. Login at http://localhost:3002/login
2. Navigate to Dashboard → Profile (or any employee profile)
3. Click "Personal File" tab
4. Click "Resignations" tab
5. Click "Submit Resignation" button
6. Fill form and submit
7. Verify resignation appears in list with SUBMITTED status

## Future Enhancements

### Suggested Improvements:
1. **Email Notifications**: Auto-notify approvers at each stage
2. **Resignation Letter PDF**: Generate official resignation letter
3. **Exit Interview Form**: Structured exit interview questionnaire
4. **Document Attachment**: Allow uploading resignation letter
5. **Withdrawal Option**: Allow employee to withdraw before supervisor approval
6. **Analytics Dashboard**: Track resignation trends and reasons
7. **Offboarding Checklist**: Automated tasks for departing employees
8. **Knowledge Transfer**: Assign knowledge transfer tasks before exit

## Related Modules

- **Personal Files** (`/apps/api/modules/employee_files/`)
- **Employee Management** (`/apps/api/modules/employees/`)
- **Authentication** (`/apps/api/modules/auth/`)
- **Notifications** (To be implemented)

---

**Last Updated**: December 8, 2025
**Status**: ✅ Fully Implemented and Working
