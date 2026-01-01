# Safeguarding Reporting System

## Overview
The safeguarding reporting system allows employees to report sensitive cases (safeguarding, misconduct, harassment, discrimination, etc.) and automatically notifies administrators and HR managers.

## How It Works

### 1. Submitting a Report
Any authenticated employee can submit a safeguarding report through:
- **Endpoint**: `POST /api/v1/safeguarding/cases`
- **Access**: All authenticated users

**Report Fields:**
- `case_type`: Type of case (safeguarding, misconduct, harassment, discrimination, etc.)
- `severity`: Severity level (low, medium, high, critical)
- `incident_date`: When the incident occurred (optional)
- `description`: Detailed description of the incident
- `location`: Where the incident occurred (optional)
- `subject_id`: ID of person accused (optional)
- `is_anonymous`: Submit anonymously (default: false)

### 2. Who Receives the Report
When a safeguarding report is submitted, **automated email notifications** are sent to:
- ✅ **All Admin users** (super_admin, admin roles)
- ✅ **All HR Managers** (hr_manager role)

The emails include:
- Case number (auto-generated: SG-YYYY-####)
- Case type and severity
- Reported date and incident date
- Location (if provided)
- Direct link to view case details
- Confidentiality notice

### 3. Viewing & Managing Cases
**Who can view cases:**
- Admin users (super_admin, admin)
- HR Managers (hr_manager)

**Available Actions:**
- View all cases: `GET /api/v1/safeguarding/cases`
- Filter by status: `GET /api/v1/safeguarding/cases?status=open`
- View specific case: `GET /api/v1/safeguarding/cases/{case_id}`
- Update case: `PATCH /api/v1/safeguarding/cases/{case_id}`

**Case Statuses:**
- `open` - Newly reported, awaiting review
- `investigating` - Under investigation
- `resolved` - Investigation complete, actions taken
- `closed` - Case closed

**Investigation Statuses:**
- `pending` - Not yet started
- `ongoing` - Investigation in progress
- `completed` - Investigation finished

### 4. Case Management
Admins and HR Managers can update cases with:
- `investigator_id`: Assign an investigator
- `investigation_status`: Update investigation progress
- `investigation_findings`: Add findings
- `status`: Change case status
- `actions_taken`: Document actions taken
- `outcome`: Record final outcome

### 5. Security & Confidentiality
- All cases have `confidentiality_level: high` by default
- Anonymous reporting available (reporter identity not stored)
- Only admin and HR manager roles can access cases
- Email notifications include confidentiality warnings

## Email Configuration
To enable email notifications, configure in `docker-compose.yml` or `.env`:

```yaml
SEND_EMAILS: "true"
EMAIL_PROVIDER: "smtp"  # or 'sendgrid', 'aws_ses'
SMTP_HOST: "smtp.gmail.com"
SMTP_PORT: "587"
SMTP_USERNAME: "your-email@gmail.com"
SMTP_PASSWORD: "your-app-password"
FROM_EMAIL: "noreply@inara.org"
APP_URL: "https://hr.inara.org"
```

## Database Table
Cases are stored in the `safeguarding_cases` table with fields:
- `id`, `case_number` - Unique identifiers
- `case_type`, `severity` - Classification
- `reported_date`, `incident_date` - Dates
- `description`, `location` - Details
- `reporter_id`, `subject_id`, `investigator_id` - People involved
- `investigation_status`, `investigation_findings` - Investigation
- `status`, `resolution_date`, `actions_taken`, `outcome` - Resolution
- `confidentiality_level` - Security classification

## Example Usage

### Submit a Report (Anonymous)
```json
POST /api/v1/safeguarding/cases
{
  "case_type": "harassment",
  "severity": "high",
  "incident_date": "2025-12-15",
  "description": "Detailed description of the incident...",
  "location": "Office Building, 3rd Floor",
  "is_anonymous": true
}
```

### Update a Case (Admin/HR)
```json
PATCH /api/v1/safeguarding/cases/{case_id}
{
  "investigator_id": "some-user-id",
  "investigation_status": "ongoing",
  "status": "investigating"
}
```

## Current Users Who Receive Notifications
Based on your system setup, notifications will be sent to:
- **maiwand@inara.org** (CEO/Admin)
- **admin@inara.org** (Admin)
- Any other users with `admin` or `hr_manager` roles

---

**System Status**: ✅ Fully Implemented and Active
**Last Updated**: December 18, 2025
