# INARA HRIS API - Email Configuration Guide

This file provides detailed instructions for configuring email notifications in the INARA HRIS system.

## Quick Start

1. **Copy the environment template:**
   ```bash
   cp apps/api/.env.example apps/api/.env
   ```

2. **Edit the `.env` file with your email provider settings**

3. **Set `SEND_EMAILS=true` to enable email notifications**

4. **Restart the API:**
   ```bash
   docker-compose restart api
   ```

## Email Configuration Options

### Option 1: SMTP (Gmail - Recommended for Testing)

**Advantages:**
- Easy to set up
- Works with any SMTP server
- No additional service required

**Setup Steps:**

1. **Enable 2-Factor Authentication on Gmail**
   - Go to Google Account → Security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "INARA HRIS"
   - Copy the 16-character password

3. **Update `.env` file:**
   ```bash
   EMAIL_PROVIDER=smtp
   SEND_EMAILS=true
   
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Your app password
   SMTP_USE_TLS=true
   
   FROM_EMAIL=noreply@inarahr.org
   FROM_NAME=INARA HR System
   APP_URL=http://localhost:3000
   ```

4. **Test:**
   ```bash
   docker-compose restart api
   docker logs inara-api | grep "Email service initialized"
   ```

**Expected Output:**
```
Email service initialized with provider: smtp
```

---

### Option 2: Office 365 / Outlook SMTP

**Setup:**

```bash
EMAIL_PROVIDER=smtp
SEND_EMAILS=true

SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yourcompany.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true

FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=INARA HR System
```

**Note:** Some Office 365 configurations require modern authentication. Contact your IT admin if you encounter issues.

---

### Option 3: SendGrid (Recommended for Production)

**Advantages:**
- High deliverability rates
- Built-in analytics
- No SMTP complexity
- Free tier: 100 emails/day

**Setup Steps:**

1. **Create SendGrid Account**
   - Go to https://sendgrid.com/
   - Sign up for free account

2. **Verify Sender Identity**
   - Settings → Sender Authentication
   - Verify a single email OR verify your domain (recommended)

3. **Create API Key**
   - Settings → API Keys → Create API Key
   - Name: "INARA HRIS"
   - Permissions: "Mail Send" (Full Access)
   - Copy the API key (shown only once!)

4. **Update `.env` file:**
   ```bash
   EMAIL_PROVIDER=sendgrid
   SEND_EMAILS=true
   
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   FROM_EMAIL=noreply@inarahr.org  # Must be verified in SendGrid
   FROM_NAME=INARA HR System
   APP_URL=http://localhost:3000
   ```

5. **Install SendGrid SDK (if not already installed):**
   ```bash
   # Add to requirements.txt
   sendgrid==6.11.0
   
   # Rebuild container
   docker-compose build api
   docker-compose up -d
   ```

6. **Uncomment SendGrid code in `core/email.py`:**
   - Find the `_send_sendgrid` method
   - Uncomment the SendGrid import and implementation

---

### Option 4: AWS SES (Best for Large Scale)

**Advantages:**
- Lowest cost at scale ($0.10 per 1000 emails)
- High reliability
- Integrates with AWS ecosystem

**Setup Steps:**

1. **AWS Console Setup**
   - Go to Amazon SES service
   - Choose your region (e.g., us-east-1)

2. **Verify Email or Domain**
   - Identities → Create Identity
   - Choose "Email address" or "Domain"
   - For domain: Add DNS records (DKIM, SPF)
   - Wait for verification

3. **Move Out of Sandbox (Production)**
   - By default, SES is in sandbox mode (limited to verified emails)
   - Request production access: Account dashboard → Request production access
   - Fill out the form explaining your use case

4. **Create IAM User**
   - IAM → Users → Create User
   - Attach policy: `AmazonSESFullAccess`
   - Create access key

5. **Update `.env` file:**
   ```bash
   EMAIL_PROVIDER=aws_ses
   SEND_EMAILS=true
   
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   
   FROM_EMAIL=noreply@inarahr.org  # Must be verified in SES
   FROM_NAME=INARA HR System
   APP_URL=https://hris.inarahr.org
   ```

6. **Install Boto3 (if not already installed):**
   ```bash
   # Add to requirements.txt
   boto3==1.34.0
   
   # Rebuild
   docker-compose build api
   docker-compose up -d
   ```

7. **Uncomment AWS SES code in `core/email.py`**

---

## Email Notification Types

The system sends emails for the following events:

### 1. Approval Request Notification
**Sent to:** Supervisor  
**When:** Employee submits a request (leave, travel, timesheet)  
**Contains:**
- Employee name
- Request type
- Request details (dates, reason, etc.)
- Link to dashboard

### 2. Approval Status Notification
**Sent to:** Employee  
**When:** Supervisor approves or rejects a request  
**Contains:**
- Request type
- Status (approved/rejected)
- Approver comments
- Link to dashboard

### 3. Delegation Notification
**Sent to:** Delegate  
**When:** Supervisor delegates approval authority  
**Contains:**
- Supervisor name
- Delegation period
- Link to pending approvals

### 4. Timesheet Reminder
**Sent to:** All employees (bulk)  
**When:** Scheduled (end of month)  
**Contains:**
- Period end date
- Link to timesheet submission

---

## Testing Email Configuration

### Method 1: Direct Python Test

Create `test_email.py` in `/apps/api/`:

```python
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.email import email_service

async def test_email():
    print("Testing email configuration...")
    
    # Test approval request notification
    result = await email_service.send_approval_request_notification(
        to_email="your-test-email@example.com",
        employee_name="John Doe",
        request_type="leave",
        request_details={
            "Type": "Annual Leave",
            "Start Date": "2024-02-01",
            "End Date": "2024-02-05",
            "Days": "5",
            "Reason": "Family vacation"
        }
    )
    
    if result:
        print("✅ Email sent successfully!")
    else:
        print("❌ Email failed to send. Check logs.")

if __name__ == "__main__":
    asyncio.run(test_email())
```

Run the test:
```bash
docker exec inara-api python test_email.py
```

### Method 2: API Endpoint Test

After submitting a leave request via API, check:

1. **API logs for email confirmation:**
   ```bash
   docker logs inara-api | grep -i email
   ```

2. **Check your email inbox** (and spam folder)

3. **Verify email content:**
   - HTML renders correctly
   - Links work
   - Employee/supervisor names correct
   - Dates formatted properly

---

## Troubleshooting

### Issue: "Email service initialized in DISABLED mode"

**Cause:** `SEND_EMAILS` is not set to `true`

**Solution:**
```bash
# Check current setting
docker exec inara-api env | grep SEND_EMAILS

# Update .env file
SEND_EMAILS=true

# Restart
docker-compose restart api
```

---

### Issue: Gmail "Username and Password not accepted"

**Cause:** Using regular password instead of app password, or 2FA not enabled

**Solution:**
1. Enable 2-Factor Authentication
2. Generate App Password (not your regular password)
3. Use the 16-character app password in SMTP_PASSWORD

---

### Issue: "SMTPAuthenticationError"

**Cause:** Incorrect SMTP credentials

**Solution:**
- Verify SMTP_USERNAME is the full email address
- Check SMTP_PASSWORD is correct
- For Gmail, ensure you're using an app password

---

### Issue: SendGrid "Unauthorized"

**Cause:** Invalid API key or insufficient permissions

**Solution:**
1. Verify API key is copied correctly (no extra spaces)
2. Check API key permissions include "Mail Send"
3. Regenerate API key if needed

---

### Issue: AWS SES "Email address not verified"

**Cause:** Sending from unverified email or still in sandbox mode

**Solution:**
1. Verify the FROM_EMAIL in AWS SES console
2. If in sandbox, also verify recipient email
3. Request production access for unrestricted sending

---

### Issue: Emails go to spam

**Cause:** No SPF/DKIM records or suspicious content

**Solution:**
1. **For SendGrid/SES:** Complete domain verification with DNS records
2. **Add SPF record:**
   ```
   TXT @ "v=spf1 include:sendgrid.net ~all"
   ```
3. **Add DKIM records** (provided by SendGrid/SES)
4. **Test spam score:** https://www.mail-tester.com/

---

### Issue: Emails not sending in production

**Checklist:**
- [ ] SEND_EMAILS=true in production .env
- [ ] EMAIL_PROVIDER correctly set
- [ ] Credentials valid and not expired
- [ ] API can reach SMTP server (firewall rules)
- [ ] FROM_EMAIL verified with provider
- [ ] No rate limiting from provider
- [ ] Check API logs for errors:
  ```bash
  docker logs inara-api | grep -i "email\|error"
  ```

---

## Email Templates Customization

To customize email templates, edit `/apps/api/core/email.py`:

```python
# Example: Change email colors
html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #your-brand-color;">New Approval Request</h2>
        <!-- Your custom content -->
    </div>
</body>
</html>
"""
```

**Restart after changes:**
```bash
docker-compose restart api
```

---

## Production Recommendations

### For Small Organizations (< 100 employees)
- **Provider:** Gmail SMTP or SendGrid Free Tier
- **Cost:** Free
- **Setup Time:** 15 minutes

### For Medium Organizations (100-1000 employees)
- **Provider:** SendGrid Growth plan or AWS SES
- **Cost:** $15-50/month
- **Setup Time:** 1 hour

### For Large Organizations (1000+ employees)
- **Provider:** AWS SES with verified domain
- **Cost:** $10-100/month (depending on volume)
- **Setup Time:** 2-4 hours (including DNS verification)

---

## Security Best Practices

1. **Never commit `.env` file to git**
   - Already in `.gitignore`
   - Use environment variables in production

2. **Use app-specific passwords**
   - Don't use your main account password
   - Gmail: app passwords
   - AWS: IAM users with minimal permissions

3. **Rotate credentials regularly**
   - Change API keys every 90 days
   - Use secret management (AWS Secrets Manager, Azure Key Vault)

4. **Monitor email sending**
   - Set up alerts for failed emails
   - Track delivery rates
   - Watch for bounce/complaint rates

5. **Verify sender domain**
   - Reduces spam likelihood
   - Builds trust with recipients
   - Required for production use

---

## Support and Resources

### Documentation
- SendGrid: https://docs.sendgrid.com/
- AWS SES: https://docs.aws.amazon.com/ses/
- Gmail SMTP: https://support.google.com/a/answer/176600

### Rate Limits
- **Gmail:** 500 emails/day (free), 2000/day (Workspace)
- **SendGrid Free:** 100 emails/day
- **SendGrid Essentials:** 40,000 emails/month ($15)
- **AWS SES:** 62,000 emails/month free (first year)

### Getting Help
- Check logs: `docker logs inara-api`
- Search issues: GitHub repository
- Contact support: [your-email@example.com]

---

**Last Updated:** 2024  
**Document Version:** 1.0
