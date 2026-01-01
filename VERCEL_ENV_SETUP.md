# Vercel Environment Variables Setup

This document lists all environment variables needed for Vercel deployment.

## Frontend Environment Variables (Vercel)

Set these in **Vercel Dashboard → Your Project → Settings → Environment Variables**

### Required

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
```

Replace `your-api-domain.com` with your actual backend API domain (e.g., from Railway, Render, or Fly.io).

### Production vs Preview

You can set different values for:
- **Production**: Production deployments
- **Preview**: Pull request previews
- **Development**: Local development (use `.env.local`)

## Backend API Environment Variables

Set these in your **backend hosting platform** (Railway, Render, Fly.io, etc.)

### Database (Neon.tech)

```bash
DATABASE_URL=postgresql://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

DATABASE_ASYNC_URL=postgresql+asyncpg://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Redis

For serverless-friendly Redis, use Upstash:
```bash
REDIS_URL=redis://default:your-password@your-redis-url.upstash.io:6379
```

Or if using Redis Cloud or self-hosted:
```bash
REDIS_URL=redis://your-redis-host:6379
```

### Security

**IMPORTANT**: Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

```bash
SECRET_KEY=your-generated-secret-key-here-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Environment

```bash
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1
```

### CORS

**IMPORTANT**: Replace with your actual Vercel domains:

```bash
CORS_ORIGINS=["https://your-app.vercel.app","https://your-custom-domain.com"]
```

If you have multiple domains, format as JSON array:
```bash
CORS_ORIGINS=["https://inara-hr.vercel.app","https://hr.inara.ngo","https://www.hr.inara.ngo"]
```

### Cloudflare R2 File Storage

```bash
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo
```

### Email Configuration

```bash
SEND_EMAILS=True
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_USE_TLS=True
FROM_EMAIL=noreply@inara.org
FROM_NAME=INARA HR System
APP_URL=https://your-vercel-domain.vercel.app
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### Rate Limiting

```bash
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_AUTH_PER_MINUTE=5
```

### File Upload Limits

```bash
MAX_FILE_SIZE_MB=10
```

### Request Timeouts

```bash
REQUEST_TIMEOUT_SECONDS=30
UPLOAD_TIMEOUT_SECONDS=300
```

### Error Tracking (Sentry - Optional)

```bash
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Organization Configuration

```bash
ORG_NAME=INARA
ORG_TIMEZONE=UTC
DEFAULT_COUNTRY=US
```

### Pagination

```bash
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## Quick Setup Checklist

### Vercel (Frontend)

- [ ] `NEXT_PUBLIC_API_URL` set to backend API URL

### Backend Platform (Railway/Render/Fly.io)

- [ ] `DATABASE_URL` and `DATABASE_ASYNC_URL` configured
- [ ] `REDIS_URL` configured (Upstash recommended)
- [ ] `SECRET_KEY` generated and set
- [ ] `CORS_ORIGINS` includes Vercel domain(s)
- [ ] `R2_*` variables configured for Cloudflare R2
- [ ] `SMTP_*` variables configured for emails
- [ ] `ENVIRONMENT=production` and `DEBUG=False`
- [ ] `APP_URL` set to Vercel frontend URL

## Testing Environment Variables

### Frontend

Check that API URL is accessible:
```bash
curl https://your-api-domain.com/api/v1/health
```

### Backend

1. Check health endpoint:
   ```bash
   curl https://your-api-domain.com/health
   ```

2. Check database connection (in backend logs)

3. Test file upload to verify R2 configuration

4. Test email sending (password reset flow)

## Security Notes

1. **Never commit `.env` files** to Git
2. Use environment variables in Vercel/backend platform, not in code
3. Rotate `SECRET_KEY` periodically
4. Use App Passwords for email, not regular passwords
5. Keep R2 credentials secure
6. Use different credentials for development and production

## Troubleshooting

### "API URL not defined" errors
- Check `NEXT_PUBLIC_API_URL` is set (must start with `NEXT_PUBLIC_`)
- Verify variable is set for correct environment (Production/Preview)

### CORS errors
- Verify `CORS_ORIGINS` includes exact frontend URL
- Check for trailing slashes (should not have trailing slash)
- Ensure HTTPS is used in production

### Database connection errors
- Verify `DATABASE_ASYNC_URL` uses `postgresql+asyncpg://`
- Check SSL mode is `require` for Neon
- Verify database credentials are correct

### R2 upload errors
- Check all `R2_*` variables are set
- Verify R2 credentials are correct
- Ensure bucket exists and is accessible

