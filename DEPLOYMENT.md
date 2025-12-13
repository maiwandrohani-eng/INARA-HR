# INARA HRIS - Deployment Guide

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd inara-hris

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Environment Configuration

Create `.env` file in project root:

```bash
# Database
POSTGRES_USER=inara_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=inara_hris

# API
SECRET_KEY=generate-a-secure-random-key-min-32-chars
ENVIRONMENT=production

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## ☁️ Cloud Deployment

### DigitalOcean

#### App Platform (Recommended for quick deployment)

1. **Create App:**
   - Go to DigitalOcean App Platform
   - Connect GitHub repository
   - Select branch

2. **Configure Components:**

   **Backend (API):**
   - Type: Web Service
   - Source: apps/api
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
   - Port: 8080

   **Frontend:**
   - Type: Web Service
   - Source: apps/frontend
   - Build Command: `npm install && npm run build`
   - Run Command: `npm start`
   - Port: 3000

   **Database:**
   - Type: Managed PostgreSQL Database
   - Plan: Production (recommended)

3. **Environment Variables:**
   Set in App Platform console

4. **Deploy:**
   Click "Deploy"

#### Droplet (Manual deployment)

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Clone and deploy
git clone <repository-url>
cd inara-hris
docker-compose up -d
```

### AWS

#### Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
eb init -p docker inara-hris
```

3. Create environment:
```bash
eb create inara-hris-prod
```

4. Deploy:
```bash
eb deploy
```

#### ECS (Elastic Container Service)

1. **Build and push images:**
```bash
# Build images
docker build -t inara-api apps/api
docker build -t inara-frontend apps/frontend

# Tag images
docker tag inara-api:latest <account-id>.dkr.ecr.region.amazonaws.com/inara-api:latest
docker tag inara-frontend:latest <account-id>.dkr.ecr.region.amazonaws.com/inara-frontend:latest

# Push to ECR
aws ecr get-login-password --region region | docker login --username AWS --password-stdin <account-id>.dkr.ecr.region.amazonaws.com
docker push <account-id>.dkr.ecr.region.amazonaws.com/inara-api:latest
docker push <account-id>.dkr.ecr.region.amazonaws.com/inara-frontend:latest
```

2. **Create ECS Task Definition**
3. **Create ECS Service**
4. **Configure Load Balancer**

### Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create apps
heroku create inara-hris-api
heroku create inara-hris-frontend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev --app inara-hris-api

# Add Redis
heroku addons:create heroku-redis:hobby-dev --app inara-hris-api

# Deploy API
cd apps/api
git subtree push --prefix apps/api heroku main

# Deploy Frontend
cd apps/frontend
git subtree push --prefix apps/frontend heroku main
```

## 🔒 Production Checklist

### Security

- [ ] Change default passwords
- [ ] Generate secure SECRET_KEY (min 32 characters)
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database encryption
- [ ] Implement rate limiting
- [ ] Set up WAF (Web Application Firewall)

### Database

- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Enable query logging
- [ ] Set up read replicas (if needed)
- [ ] Run migrations: `alembic upgrade head`
- [ ] Seed initial data: `python scripts/seed_data.py`

### Monitoring

- [ ] Set up application monitoring (Sentry, New Relic)
- [ ] Configure log aggregation (ELK, Datadog)
- [ ] Set up uptime monitoring
- [ ] Configure alerts
- [ ] Enable error tracking

### Performance

- [ ] Enable CDN for static assets
- [ ] Configure caching (Redis)
- [ ] Optimize database queries
- [ ] Enable gzip compression
- [ ] Implement request throttling

### Backup Strategy

```bash
# Database backup
pg_dump -U inara_user inara_hris > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * pg_dump -U inara_user inara_hris > /backups/inara_$(date +%Y%m%d).sql
```

## 📊 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
    
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing

Configure Nginx as load balancer:

```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location /api/ {
        proxy_pass http://api_backend;
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker images
      run: |
        docker-compose build
        docker-compose push
    
    - name: Deploy to production
      run: |
        ssh user@server 'cd /app && docker-compose pull && docker-compose up -d'
```

## 📝 Post-Deployment

1. **Create admin user:**
```bash
docker-compose exec api python scripts/create_admin.py
```

2. **Verify services:**
```bash
# Check API
curl http://your-domain.com/api/v1/health

# Check frontend
curl http://your-domain.com
```

3. **Monitor logs:**
```bash
docker-compose logs -f
```

4. **Set up SSL (Let's Encrypt):**
```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🆘 Troubleshooting

### Database Connection Issues

```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U inara_user inara_hris
```

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api

# Check database migrations
docker-compose exec api alembic current
docker-compose exec api alembic upgrade head
```

### Frontend Build Errors

```bash
# Clear cache and rebuild
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

## 📞 Support

For deployment issues:
- Email: tech@inara.org
- Documentation: https://docs.inara.org
