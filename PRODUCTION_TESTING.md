# Production Testing Guide - INARA HRIS

This document provides comprehensive testing procedures for the INARA HRIS approval workflow and 360-degree performance review systems before production deployment.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Email Configuration Testing](#email-configuration-testing)
3. [Approval Workflow Testing](#approval-workflow-testing)
4. [360-Degree Performance Review Testing](#360-degree-performance-review-testing)
5. [HR Admin Override Testing](#hr-admin-override-testing)
6. [Frontend Integration Testing](#frontend-integration-testing)
7. [Database Integrity Testing](#database-integrity-testing)
8. [Load Testing](#load-testing)

---

## Prerequisites

### Test Environment Setup
```bash
# 1. Ensure all services are running
docker-compose up -d

# 2. Check service status
docker-compose ps

# 3. Run database migrations
docker exec inara-api alembic upgrade head

# 4. Seed test data (if needed)
docker exec inara-api python scripts/seed_data.py
```

### Test User Accounts
Create the following test users:

1. **Employee (No Reports)**
   - Email: employee@test.com
   - Role: Employee
   - Has supervisor assigned

2. **Supervisor (Manages 3-5 employees)**
   - Email: supervisor@test.com
   - Role: Supervisor
   - Has subordinates

3. **HR Admin**
   - Email: hradmin@test.com
   - Role: HR Admin
   - Has `hr:admin` permission

4. **Delegate**
   - Email: delegate@test.com
   - Role: Employee/Supervisor
   - Will receive delegated approvals

---

## Email Configuration Testing

### Option 1: SMTP (Gmail) Configuration

#### Step 1: Generate Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Create new app password for "INARA HRIS"
3. Save the 16-character password

#### Step 2: Configure Environment Variables
Create `.env` file in `/apps/api/` directory:

```bash
# Email Configuration
EMAIL_PROVIDER=smtp
SEND_EMAILS=true

# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Sender Info
FROM_EMAIL=noreply@inarahr.org
FROM_NAME=INARA HR System

# Application URL
APP_URL=http://localhost:3000
```

#### Step 3: Test Email Service
```bash
# Restart API to load new environment variables
docker-compose restart api

# Check logs for email service initialization
docker logs inara-api | grep "Email service initialized"

# Expected output: "Email service initialized with provider: smtp"
```

#### Step 4: Send Test Email
Use Python script or API endpoint:

```python
# test_email.py
import asyncio
from core.email import email_service

async def test():
    result = await email_service.send_approval_request_notification(
        to_email="test@example.com",
        employee_name="Test Employee",
        request_type="leave",
        request_details={
            "Type": "Annual Leave",
            "Start Date": "2024-01-15",
            "End Date": "2024-01-20",
            "Days": "5",
            "Reason": "Family vacation"
        }
    )
    print(f"Email sent: {result}")

asyncio.run(test())
```

Run test:
```bash
docker exec inara-api python test_email.py
```

### Option 2: SendGrid Configuration

```bash
# Environment Variables
EMAIL_PROVIDER=sendgrid
SEND_EMAILS=true
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@inarahr.org
```

### Option 3: AWS SES Configuration

```bash
# Environment Variables
EMAIL_PROVIDER=aws_ses
SEND_EMAILS=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY=your-access-key
AWS_SECRET_KEY=your-secret-key
FROM_EMAIL=verified-email@inarahr.org
```

### Email Testing Checklist
- [ ] Configuration loaded successfully
- [ ] Test email sent without errors
- [ ] Email received in inbox (check spam folder)
- [ ] Email formatting looks correct (HTML rendering)
- [ ] Links in email are clickable and correct
- [ ] Sender name displays as "INARA HR System"

---

## Approval Workflow Testing

### Test Case 1: Leave Request Submission and Approval

#### Setup
- Login as Employee
- Ensure employee has supervisor assigned
- Check leave balance available

#### Test Steps

**1. Submit Leave Request**
```bash
# API Request
POST http://localhost:8000/api/v1/leave/requests
Authorization: Bearer <employee_token>
Content-Type: application/json

{
  "leave_type": "annual",
  "start_date": "2024-02-01",
  "end_date": "2024-02-05",
  "reason": "Family vacation"
}
```

**Expected Results:**
- ✅ Leave request created with status "pending"
- ✅ Approval request created in `approval_requests` table
- ✅ Email sent to supervisor
- ✅ Leave balance shows days in "pending"
- ✅ API returns 201 Created with leave request details

**2. Supervisor Receives Notification**
- ✅ Supervisor receives email notification
- ✅ Email contains request details
- ✅ Email has link to dashboard

**3. Supervisor Views Pending Approvals**
```bash
# Login as Supervisor
# Navigate to dashboard

GET http://localhost:8000/api/v1/approvals/pending
Authorization: Bearer <supervisor_token>
```

**Expected Results:**
- ✅ Leave request appears in pending approvals
- ✅ Shows employee name, dates, days, reason
- ✅ Shows in PendingApprovalsWidget on frontend

**4. Supervisor Approves Request**
```bash
POST http://localhost:8000/api/v1/approvals/requests/{approval_id}/approve
Authorization: Bearer <supervisor_token>
Content-Type: application/json

{
  "comments": "Approved. Enjoy your vacation!"
}
```

**Expected Results:**
- ✅ Approval status changes to "approved"
- ✅ Leave request status changes to "approved"
- ✅ Email sent to employee
- ✅ Leave balance updated (pending → used)
- ✅ Dashboard stats updated

**5. Employee Receives Approval Notification**
- ✅ Employee receives email
- ✅ Email shows status as "Approved"
- ✅ Comments visible in email

### Test Case 2: Leave Request Rejection

Follow same steps as Test Case 1, but at step 4:

```bash
POST http://localhost:8000/api/v1/approvals/requests/{approval_id}/reject
Authorization: Bearer <supervisor_token>
Content-Type: application/json

{
  "comments": "Overlaps with critical project deadline"
}
```

**Expected Results:**
- ✅ Approval status "rejected"
- ✅ Leave request status "rejected"
- ✅ Email sent to employee with rejection reason
- ✅ Leave balance restored (pending removed)

### Test Case 3: Travel Request Approval Flow

**1. Submit Travel Request**
```bash
POST http://localhost:8000/api/v1/travel/requests
Authorization: Bearer <employee_token>

{
  "destination": "Kabul, Afghanistan",
  "start_date": "2024-03-01",
  "end_date": "2024-03-05",
  "purpose": "Training workshop",
  "estimated_cost": 500.00,
  "currency": "USD"
}
```

**2. Verify Approval Routing**
- ✅ Approval request created
- ✅ Email sent to supervisor
- ✅ Appears in supervisor dashboard

**3. Approve/Reject Travel Request**
- Same approval endpoint as leave
- ✅ Status updates correctly
- ✅ Notifications sent

### Test Case 4: Timesheet Approval Flow

**1. Submit Monthly Timesheet**
```bash
POST http://localhost:8000/api/v1/timesheets/submit
Authorization: Bearer <employee_token>

{
  "year": 2024,
  "month": 1,
  "total_hours": 160,
  "overtime_hours": 10
}
```

**2. Verify Supervisor Approval**
- ✅ Timesheet requires approval
- ✅ Supervisor can review hours
- ✅ Approval/rejection updates timesheet status

### Test Case 5: Approval Delegation

**1. Create Delegation**
```bash
POST http://localhost:8000/api/v1/approvals/delegations
Authorization: Bearer <supervisor_token>

{
  "supervisor_id": "<supervisor_id>",
  "delegate_id": "<delegate_id>",
  "start_date": "2024-02-01",
  "end_date": "2024-02-14",
  "reason": "On leave"
}
```

**Expected Results:**
- ✅ Delegation created
- ✅ Email sent to delegate
- ✅ Delegate can see supervisor's pending approvals

**2. Submit Request During Delegation**
- ✅ New requests route to delegate
- ✅ Delegate receives notifications
- ✅ Delegate can approve/reject

**3. Delegation Expiry**
- ✅ After end_date, requests route back to supervisor
- ✅ Active delegation expires automatically

### Test Case 6: Request Cancellation

**1. Employee Cancels Pending Request**
```bash
POST http://localhost:8000/api/v1/approvals/requests/{approval_id}/cancel
Authorization: Bearer <employee_token>
```

**Expected Results:**
- ✅ Request status changes to "cancelled"
- ✅ Leave balance updated (pending removed)
- ✅ Cannot cancel already approved/rejected requests

---

## 360-Degree Performance Review Testing

### Test Case 1: Initiate 360-Degree Review

**1. HR Admin Creates Review Cycle**
```bash
POST http://localhost:8000/api/v1/performance/reviews/360
Authorization: Bearer <hradmin_token>

{
  "employee_id": "<employee_id>",
  "review_period_start": "2024-01-01",
  "review_period_end": "2024-12-31",
  "evaluators": [
    {
      "evaluator_id": "<supervisor_id>",
      "evaluator_type": "supervisor"
    },
    {
      "evaluator_id": "<peer1_id>",
      "evaluator_type": "peer"
    },
    {
      "evaluator_id": "<peer2_id>",
      "evaluator_type": "peer"
    },
    {
      "evaluator_id": "<subordinate_id>",
      "evaluator_type": "subordinate"
    },
    {
      "evaluator_id": "<employee_id>",
      "evaluator_type": "self"
    }
  ]
}
```

**Expected Results:**
- ✅ Review cycle created
- ✅ 5 evaluation records created (1 per evaluator)
- ✅ Status is "in_progress"
- ✅ All evaluators have "pending" evaluations

### Test Case 2: Evaluators Submit Reviews

**1. Supervisor Submits Evaluation**
```bash
POST http://localhost:8000/api/v1/performance/reviews/360/{cycle_id}/evaluate
Authorization: Bearer <supervisor_token>

{
  "technical_skills": 4,
  "communication": 5,
  "teamwork": 4,
  "leadership": 3,
  "problem_solving": 4,
  "strengths": "Excellent technical skills and communication",
  "areas_for_improvement": "Could develop leadership skills further",
  "overall_comments": "Strong performer, ready for senior role"
}
```

**Expected Results:**
- ✅ Evaluation status changes from "pending" to "completed"
- ✅ Scores saved (1-5 scale validation)
- ✅ Comments stored
- ✅ Can view pending evaluations for current user

**2. Peers Submit Evaluations**
- Repeat for each peer
- ✅ Different perspectives captured
- ✅ Anonymous or attributed (based on config)

**3. Subordinate Submits Upward Feedback**
- ✅ Can evaluate supervisor
- ✅ Leadership scores collected

**4. Self-Assessment**
- ✅ Employee completes self-evaluation
- ✅ Self-scores tracked separately

### Test Case 3: View 360-Review Summary

**1. Get Review Summary**
```bash
GET http://localhost:8000/api/v1/performance/reviews/360/{cycle_id}/summary
Authorization: Bearer <hradmin_token>
```

**Expected Results:**
- ✅ Shows all evaluations
- ✅ Aggregated scores by competency
- ✅ Breakdown by evaluator type
- ✅ Overall average ratings
- ✅ All comments compiled

**Example Summary:**
```json
{
  "cycle_id": "...",
  "employee_name": "John Doe",
  "status": "in_progress",
  "completion": "4/5 evaluations submitted",
  "scores": {
    "technical_skills": {
      "supervisor": 4,
      "peer_avg": 4.5,
      "subordinate": 4,
      "self": 3,
      "overall_avg": 4.1
    },
    "communication": { ... },
    ...
  },
  "evaluations": [...]
}
```

### Test Case 4: Finalize Review

**1. HR Admin Finalizes Review**
```bash
POST http://localhost:8000/api/v1/performance/reviews/360/{cycle_id}/finalize
Authorization: Bearer <hradmin_token>

{
  "final_rating": "Exceeds Expectations",
  "hr_comments": "Strong 360 feedback. Recommend for promotion consideration."
}
```

**Expected Results:**
- ✅ Status changes to "completed"
- ✅ Final rating recorded
- ✅ Can no longer submit evaluations
- ✅ Employee can view results

### Test Case 5: Employee Acknowledges Review

**1. Employee Views Final Review**
```bash
GET http://localhost:8000/api/v1/performance/reviews/360/{cycle_id}
Authorization: Bearer <employee_token>
```

**2. Employee Acknowledges**
```bash
POST http://localhost:8000/api/v1/performance/reviews/360/{cycle_id}/acknowledge
Authorization: Bearer <employee_token>

{
  "employee_comments": "Thank you for the feedback. I will work on leadership development."
}
```

**Expected Results:**
- ✅ Acknowledgment recorded
- ✅ Employee comments saved
- ✅ Review process complete

---

## HR Admin Override Testing

### Test Case 1: HR Admin Overrides Approval

**Scenario:** Supervisor is unavailable, critical request needs approval

**1. Submit Leave Request as Employee**
```bash
POST http://localhost:8000/api/v1/leave/requests
# Request pending, assigned to supervisor
```

**2. HR Admin Force Approves**
```bash
POST http://localhost:8000/api/v1/approvals/admin/requests/{approval_id}/approve
Authorization: Bearer <hradmin_token>

{
  "comments": "Approved due to supervisor absence and urgent nature"
}
```

**Expected Results:**
- ✅ Request approved by HR admin (not original approver)
- ✅ Comments prefixed with "[HR OVERRIDE]"
- ✅ Employee receives notification
- ✅ Audit trail shows HR admin override
- ✅ Requires `hr:admin` permission (403 without it)

### Test Case 2: HR Admin Force Rejects

```bash
POST http://localhost:8000/api/v1/approvals/admin/requests/{approval_id}/reject
Authorization: Bearer <hradmin_token>

{
  "comments": "Policy violation - insufficient notice period"
}
```

**Expected Results:**
- ✅ Request rejected by HR admin
- ✅ Override marked in comments
- ✅ Employee notified with HR comments

### Test Case 3: Permission Validation

**1. Regular Employee Attempts Override**
```bash
POST http://localhost:8000/api/v1/approvals/admin/requests/{approval_id}/approve
Authorization: Bearer <employee_token>
```

**Expected Result:**
- ✅ 403 Forbidden
- ✅ Error: "Missing required permission: hr:admin"

---

## Frontend Integration Testing

### Test Case 1: PendingApprovalsWidget Display

**1. Login as Supervisor**
- Navigate to Dashboard
- ✅ PendingApprovalsWidget visible
- ✅ Shows counts by type (leave, travel, timesheet, performance)
- ✅ Total pending count matches backend

**2. Widget Functionality**
- ✅ Click "View All" navigates correctly
- ✅ Recent approvals list shows last 5
- ✅ Employee names displayed
- ✅ Dates formatted correctly
- ✅ Status badges colored appropriately

### Test Case 2: Approve/Reject from Dashboard

**1. Click Approve Button**
- ✅ Shows confirmation dialog
- ✅ Can add comments
- ✅ On success, item disappears from list
- ✅ Count decrements
- ✅ Toast notification shown

**2. Click Reject Button**
- ✅ Shows rejection dialog with required comments
- ✅ On success, item disappears
- ✅ Count updates

### Test Case 3: Real-Time Updates

**1. Open Dashboard in Two Browsers**
- Browser A: Supervisor account
- Browser B: Employee submits request

**2. Verify Updates**
- ✅ Browser A shows new request (after refresh or websocket)
- ✅ Count increments
- ✅ Widget updates

### Test Case 4: Mobile Responsiveness

- ✅ Dashboard renders on mobile (< 768px)
- ✅ Widget layout adjusts (stacks vertically)
- ✅ Buttons remain clickable
- ✅ No horizontal scroll

---

## Database Integrity Testing

### Test Case 1: Foreign Key Constraints

**1. Orphaned Records Prevention**
```sql
-- Try to create approval with non-existent employee
INSERT INTO approval_requests (employee_id, approver_id, ...)
VALUES ('00000000-0000-0000-0000-000000000000', ...);
```
- ✅ Should fail with foreign key constraint error

**2. Cascade Deletes (if configured)**
```sql
-- Delete employee with pending approvals
DELETE FROM employees WHERE id = '<employee_with_approvals>';
```
- ✅ Check if approvals are handled correctly (cascade or restrict)

### Test Case 2: Data Consistency

**1. Leave Balance Accuracy**
```sql
-- After approval flow
SELECT 
  total_days,
  used_days,
  pending_days,
  available_days,
  (total_days - used_days - pending_days) as calculated_available
FROM leave_balances
WHERE employee_id = '<test_employee>';
```
- ✅ `calculated_available` = `available_days`
- ✅ No negative balances

**2. Approval Status Consistency**
```sql
-- No approvals in invalid state
SELECT * FROM approval_requests
WHERE status NOT IN ('pending', 'approved', 'rejected', 'cancelled');
```
- ✅ Should return 0 rows

### Test Case 3: Transaction Rollbacks

**1. Test Failed Approval**
- Cause approval to fail mid-transaction
- ✅ Leave balance not updated
- ✅ Approval status unchanged
- ✅ No partial updates

---

## Load Testing

### Test Case 1: Concurrent Approval Requests

**Setup: Apache Bench or k6**

```bash
# 100 concurrent leave requests
ab -n 100 -c 10 -H "Authorization: Bearer <token>" \
   -T application/json \
   -p leave_request.json \
   http://localhost:8000/api/v1/leave/requests
```

**Expected Results:**
- ✅ All requests processed
- ✅ No database deadlocks
- ✅ Response times < 1 second (p95)
- ✅ No approval routing errors

### Test Case 2: Email Queue Performance

**1. Submit 50 Requests Simultaneously**
- ✅ All emails queued
- ✅ Emails sent asynchronously
- ✅ API response not blocked by email sending
- ✅ No email duplicates

### Test Case 3: Dashboard Load with Many Approvals

**1. Create 100 Pending Approvals**
```bash
# Seed script
for i in {1..100}; do
  # Create leave request
done
```

**2. Load Supervisor Dashboard**
- ✅ Page loads in < 2 seconds
- ✅ Pagination works
- ✅ Filtering works
- ✅ No memory issues

---

## Acceptance Criteria Checklist

### Email System
- [ ] Emails configured with SMTP/SendGrid/SES
- [ ] All notification types tested (approval, status, delegation)
- [ ] HTML formatting renders correctly
- [ ] Links are clickable and correct
- [ ] Emails not sent when SEND_EMAILS=false

### Approval Workflow
- [ ] Leave requests create approvals
- [ ] Travel requests create approvals
- [ ] Timesheet submissions create approvals
- [ ] Approvals route to correct supervisor
- [ ] Delegations work during supervisor absence
- [ ] HR admin can override any approval
- [ ] Employees receive status notifications
- [ ] Leave balances update correctly

### 360-Degree Reviews
- [ ] Can create review cycle with multiple evaluators
- [ ] Each evaluator type can submit once
- [ ] Scores aggregate correctly
- [ ] Summary shows all perspectives
- [ ] Can finalize and lock reviews
- [ ] Employee can view and acknowledge

### Frontend
- [ ] PendingApprovalsWidget shows on supervisor dashboard
- [ ] Counts accurate
- [ ] Approve/reject buttons work
- [ ] Mobile responsive
- [ ] Loading states show
- [ ] Error handling works

### Security
- [ ] Regular employees cannot access HR override endpoints
- [ ] Employees can only cancel own requests
- [ ] Supervisors only see their team's requests
- [ ] JWT authentication required on all endpoints
- [ ] Permission checks enforced

### Performance
- [ ] Dashboard loads in < 2s with 100 approvals
- [ ] Email sending doesn't block API responses
- [ ] Database queries optimized (no N+1)
- [ ] Concurrent requests handled correctly

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passed
- [ ] Email credentials configured
- [ ] Database migrations run
- [ ] Seed data loaded (if needed)
- [ ] Environment variables set
- [ ] SSL certificates configured
- [ ] Backup strategy in place

### Deployment
- [ ] Deploy API with zero downtime
- [ ] Deploy frontend
- [ ] Verify health check endpoints
- [ ] Test email sending in production
- [ ] Test one complete approval flow

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check email delivery rates
- [ ] Monitor API performance
- [ ] Set up alerts (failed emails, slow queries)
- [ ] User acceptance testing with real users

### Rollback Plan
- [ ] Database rollback script ready
- [ ] Previous version images tagged
- [ ] Rollback procedure documented
- [ ] Communication plan for downtime

---

## Support Contacts

**Technical Issues:**
- Backend API: [Developer Email]
- Frontend: [Developer Email]
- Database: [DBA Email]

**Email Issues:**
- SMTP: [Email Admin]
- SendGrid: [SendGrid Account Owner]
- AWS SES: [AWS Admin]

**Emergency:**
- On-call: [Phone Number]
- Slack: #inara-hris-support

---

## Appendix: Common Issues and Solutions

### Issue: Emails Not Sending

**Symptoms:** Logs show "[EMAIL DISABLED]"

**Solution:**
```bash
# Check environment variable
docker exec inara-api env | grep SEND_EMAILS

# Should be: SEND_EMAILS=true

# If missing, add to docker-compose.yml:
services:
  api:
    environment:
      - SEND_EMAILS=true
      - EMAIL_PROVIDER=smtp
      # ... other vars

# Restart
docker-compose restart api
```

### Issue: Gmail "Less Secure Apps" Error

**Solution:**
- Use App Password instead of account password
- Enable 2FA on Gmail account
- Generate app-specific password

### Issue: Approval Not Routing to Supervisor

**Symptoms:** Error "Employee has no supervisor assigned"

**Solution:**
```sql
-- Check employee's manager_id
SELECT id, first_name, last_name, manager_id
FROM employees
WHERE id = '<employee_id>';

-- Set supervisor
UPDATE employees
SET manager_id = '<supervisor_id>'
WHERE id = '<employee_id>';
```

### Issue: Leave Balance Not Updating

**Check:**
```sql
SELECT * FROM leave_balances
WHERE employee_id = '<employee_id>';

-- Verify:
-- total_days = initial allocation
-- used_days = approved leaves
-- pending_days = pending requests
-- available_days = total - used - pending
```

### Issue: 360 Review Shows Incomplete When All Done

**Check:**
```sql
SELECT evaluator_type, status
FROM performance_evaluations
WHERE cycle_id = '<cycle_id>';

-- All should show 'completed'
```

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Next Review:** Before Production Launch
