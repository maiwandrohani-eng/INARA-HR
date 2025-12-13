# INARA HR Management System (HRIS)

A comprehensive, production-ready HR Management System built for multi-country NGO operations.

## 🏗️ Architecture

**Modular Monolith** with microservice-ready domain separation.

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL (Primary Database)
- Redis (Caching & Pub/Sub)
- SQLAlchemy (ORM)
- Alembic (Migrations)
- Pydantic (Validation)

**Frontend:**
- Next.js 14 (React, TypeScript)
- TailwindCSS
- shadcn/ui
- Zustand (State Management)
- React Query (Data Fetching)

**Infrastructure:**
- Docker & Docker Compose
- S3-Compatible Storage (DigitalOcean Spaces / AWS S3)
- Nginx (Reverse Proxy)
- Redis (Cache & Events)

## 📁 Project Structure

```
/inara-hris
├── /apps
│   ├── /api              # FastAPI Backend
│   └── /frontend         # Next.js Frontend
├── /services             # Future microservices
├── /packages
│   ├── /ui-components    # Shared UI library
│   ├── /models           # Shared data models
│   ├── /auth             # Auth utilities
│   └── /utils            # Common utilities
├── /infrastructure
│   ├── /docker           # Docker configs
│   ├── /nginx            # Nginx configs
│   ├── /terraform        # IaC (optional)
│   └── /k8s              # Kubernetes (optional)
└── /docs                 # Documentation
```

## 🎯 Core HR Modules

1. **Auth & User Management** - JWT, RBAC, SSO ready
2. **Employee Management** - Profiles, contracts, positions, documents
3. **Recruitment (ATS)** - Applicants, interviews, offer letters
4. **Onboarding** - Checklists, probation tracking, policy acknowledgment
5. **Employee Self-Service (ESS)** - Personal portal
6. **Leave & Attendance** - Multi-country leave policies
7. **Timesheets** - Donor/project time allocation
8. **Performance Management** - Goals, reviews, PIPs
9. **Learning & Development** - Training, certifications
10. **Compensation & Payroll** - Salary history, payroll support
11. **Safeguarding** - Misconduct case management
12. **Grievance & Disciplinary** - Case tracking and resolution
13. **Travel & Deployment** - Travel requests, visa tracking
14. **Analytics & Dashboards** - HR metrics and insights
15. **Admin Config Panel** - Multi-country HR rules configuration

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Development Setup

1. **Clone and setup:**
```bash
cd inara-hris
```

2. **Backend setup:**
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
alembic upgrade head
uvicorn main:app --reload
```

3. **Frontend setup:**
```bash
cd apps/frontend
npm install
cp .env.local.example .env.local
npm run dev
```

4. **Docker setup (recommended):**
```bash
docker-compose up -d
```

## 🔐 Authentication & Authorization

- JWT-based authentication
- Role-Based Access Control (RBAC)
- Permissions: `employees:read`, `employees:write`, `payroll:admin`, etc.
- Multi-tenant ready (country-level separation)

### Default Roles
- **Super Admin** - Full system access
- **HR Admin** - HR operations management
- **HR Manager** - Team management
- **Line Manager** - Team oversight
- **Employee** - Self-service access

## 📊 Database Schema

PostgreSQL with UUID primary keys. Main tables:

- `users`, `roles`, `permissions`
- `employees`, `contracts`, `positions`
- `leave_requests`, `leave_balances`, `leave_policies`
- `timesheets`, `timesheet_entries`
- `performance_goals`, `performance_reviews`
- `training_courses`, `training_enrollments`
- `safeguarding_cases`, `grievances`, `disciplinary_actions`
- `travel_requests`, `visa_records`
- And more...

## 🌍 Multi-Country Support

- Country-specific leave policies
- Currency management
- Timezone handling
- Compliance requirements
- Localized workflows

## 📈 Development Roadmap

- [x] Core architecture setup
- [x] Module scaffolding
- [ ] API implementation
- [ ] Frontend UI development
- [ ] Testing suite
- [ ] CI/CD pipeline
- [ ] Production deployment

## 🧪 Testing

```bash
# Backend tests
cd apps/api
pytest

# Frontend tests
cd apps/frontend
npm test
```

## 📝 API Documentation

Once running, access:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

Proprietary - INARA Organization

## 📧 Support

For support, email: hr-tech@inara.org
