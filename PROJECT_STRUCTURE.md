# INARA HRIS - Complete Project Structure

## 📁 Full Directory Tree

```
inara-hris/
│
├── README.md                           # Main project documentation
├── DEPLOYMENT.md                       # Deployment guide
├── .gitignore                          # Git ignore rules
├── docker-compose.yml                  # Docker orchestration
│
├── apps/                               # Application code
│   ├── api/                           # FastAPI Backend
│   │   ├── core/                      # Core infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings & environment
│   │   │   ├── database.py           # Database connection
│   │   │   ├── security.py           # JWT & password hashing
│   │   │   ├── dependencies.py       # FastAPI dependencies
│   │   │   ├── exceptions.py         # Custom exceptions
│   │   │   └── models.py             # Base models & mixins
│   │   │
│   │   ├── modules/                   # HR Modules (15 total)
│   │   │   │
│   │   │   ├── auth/                 # 1. Authentication & RBAC
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py         # User, Role, Permission
│   │   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   │   ├── repositories.py   # Database operations
│   │   │   │   ├── services.py       # Business logic
│   │   │   │   └── routes.py         # API endpoints
│   │   │   │
│   │   │   ├── employees/            # 2. Employee Management
│   │   │   │   ├── models.py         # Employee, Contract, Document
│   │   │   │   ├── schemas.py
│   │   │   │   ├── repositories.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── recruitment/          # 3. ATS (Applicant Tracking)
│   │   │   │   ├── models.py         # JobPosting, Application, Interview
│   │   │   │   ├── schemas.py
│   │   │   │   ├── repositories.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── onboarding/           # 4. Onboarding
│   │   │   │   ├── models.py         # OnboardingChecklist
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── leave/                # 5. Leave & Attendance
│   │   │   │   ├── models.py         # LeaveRequest, LeaveBalance
│   │   │   │   ├── schemas.py
│   │   │   │   ├── repositories.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── timesheets/           # 6. Timesheets
│   │   │   │   ├── models.py         # Timesheet, TimesheetEntry
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── performance/          # 7. Performance Management
│   │   │   │   ├── models.py         # Goals, Reviews, PIPs
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── learning/             # 8. Learning & Development
│   │   │   │   ├── models.py         # TrainingCourse, Enrollment
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── compensation/         # 9. Compensation & Payroll
│   │   │   │   ├── models.py         # SalaryHistory
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── safeguarding/         # 10. Safeguarding Cases
│   │   │   │   ├── models.py         # SafeguardingCase
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── grievance/            # 11. Grievance & Disciplinary
│   │   │   │   ├── models.py         # Grievance, DisciplinaryAction
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── travel/               # 12. Travel & Deployment
│   │   │   │   ├── models.py         # TravelRequest, VisaRecord
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── analytics/            # 13. Analytics & Reports
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   ├── admin/                # 14. Admin Configuration
│   │   │   │   ├── models.py         # CountryConfig, SalaryBand
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   └── ess/                  # 15. Employee Self-Service
│   │   │       ├── schemas.py
│   │   │       ├── services.py
│   │   │       └── routes.py
│   │   │
│   │   ├── alembic/                   # Database Migrations
│   │   │   ├── versions/
│   │   │   │   └── 001_initial.py
│   │   │   └── env.py
│   │   │
│   │   ├── scripts/                   # Utility scripts
│   │   │   ├── seed_data.py
│   │   │   └── create_admin.py
│   │   │
│   │   ├── tests/                     # Test suite
│   │   │   ├── test_auth.py
│   │   │   ├── test_employees.py
│   │   │   └── ...
│   │   │
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── requirements.txt           # Python dependencies
│   │   ├── Dockerfile                 # Docker configuration
│   │   ├── alembic.ini               # Alembic configuration
│   │   ├── .env.example              # Environment template
│   │   └── README.md                 # API documentation
│   │
│   └── frontend/                      # Next.js Frontend
│       ├── app/                       # Next.js App Router
│       │   ├── (auth)/
│       │   │   └── login/
│       │   │       └── page.tsx
│       │   │
│       │   ├── dashboard/
│       │   │   ├── layout.tsx        # Dashboard layout
│       │   │   ├── page.tsx          # Dashboard home
│       │   │   │
│       │   │   ├── employees/
│       │   │   │   ├── page.tsx
│       │   │   │   └── [id]/page.tsx
│       │   │   │
│       │   │   ├── leave/
│       │   │   │   └── page.tsx
│       │   │   │
│       │   │   ├── timesheets/
│       │   │   │   └── page.tsx
│       │   │   │
│       │   │   └── ...              # Other modules
│       │   │
│       │   ├── layout.tsx            # Root layout
│       │   ├── page.tsx              # Home page
│       │   ├── providers.tsx         # React Query provider
│       │   └── globals.css           # Global styles
│       │
│       ├── components/                # Reusable components
│       │   ├── ui/                   # shadcn/ui components
│       │   │   ├── button.tsx
│       │   │   ├── card.tsx
│       │   │   ├── dialog.tsx
│       │   │   ├── input.tsx
│       │   │   ├── label.tsx
│       │   │   └── ...
│       │   │
│       │   ├── layout/
│       │   │   ├── header.tsx
│       │   │   ├── sidebar.tsx
│       │   │   └── footer.tsx
│       │   │
│       │   └── shared/
│       │       ├── loading.tsx
│       │       ├── error.tsx
│       │       └── empty-state.tsx
│       │
│       ├── modules/                   # Feature modules
│       │   ├── employees/
│       │   │   ├── components/
│       │   │   ├── hooks/
│       │   │   └── types.ts
│       │   │
│       │   ├── leave/
│       │   ├── timesheets/
│       │   └── ...
│       │
│       ├── services/                  # API client services
│       │   ├── auth.service.ts
│       │   ├── employee.service.ts
│       │   ├── leave.service.ts
│       │   └── ...
│       │
│       ├── hooks/                     # Custom React hooks
│       │   ├── use-auth.ts
│       │   ├── use-employees.ts
│       │   ├── use-leave.ts
│       │   └── ...
│       │
│       ├── state/                     # State management
│       │   ├── auth.store.ts         # Zustand stores
│       │   └── ...
│       │
│       ├── lib/                       # Utilities
│       │   ├── api-client.ts         # Axios instance
│       │   ├── utils.ts              # Helper functions
│       │   └── cn.ts                 # classNames utility
│       │
│       ├── types/                     # TypeScript types
│       │   ├── auth.ts
│       │   ├── employee.ts
│       │   └── ...
│       │
│       ├── public/                    # Static assets
│       │   ├── images/
│       │   └── icons/
│       │
│       ├── package.json
│       ├── tsconfig.json
│       ├── next.config.js
│       ├── tailwind.config.js
│       ├── postcss.config.js
│       ├── Dockerfile
│       ├── .env.local.example
│       └── README.md
│
├── infrastructure/                    # Infrastructure configs
│   ├── docker/
│   │   ├── api.Dockerfile
│   │   └── frontend.Dockerfile
│   │
│   ├── nginx/
│   │   ├── nginx.conf               # Nginx configuration
│   │   └── ssl/                     # SSL certificates
│   │
│   ├── terraform/                    # IaC (optional)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── k8s/                          # Kubernetes (optional)
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
│
├── packages/                          # Shared packages (future)
│   ├── ui-components/
│   ├── models/
│   ├── auth/
│   └── utils/
│
├── services/                          # Future microservices
│   └── (placeholder for future services)
│
└── docs/                             # Additional documentation
    ├── API.md
    ├── DATABASE.md
    ├── SECURITY.md
    └── DEVELOPMENT.md
```

## 📊 Key Statistics

- **Total Modules:** 15 HR modules
- **Backend Files:** ~120+ files
- **Frontend Files:** ~80+ files
- **Database Tables:** 30+ tables
- **API Endpoints:** 100+ endpoints
- **Technology Stack:**
  - Backend: Python, FastAPI, SQLAlchemy, PostgreSQL
  - Frontend: TypeScript, Next.js 14, React, TailwindCSS
  - Infrastructure: Docker, Nginx, Redis

## 🎯 Core Features Implemented

### Authentication & Authorization ✅
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Permission system
- Password reset & email verification

### Employee Management ✅
- Complete employee profiles
- Contract management
- Document storage
- Organizational structure

### Recruitment (ATS) ✅
- Job postings
- Application tracking
- Interview scheduling
- Offer letter management

### Leave & Attendance ✅
- Multi-country leave policies
- Leave balance tracking
- Approval workflows
- Attendance records

### Timesheets ✅
- Project-based time tracking
- Donor allocation
- Approval workflows

### Performance Management ✅
- Goal setting
- Performance reviews
- PIPs (Performance Improvement Plans)

### Learning & Development ✅
- Training course catalog
- Enrollment tracking
- Certificate management

### Compensation ✅
- Salary history
- Payroll support

### Safeguarding ✅
- Case management
- Investigation tracking
- Confidential handling

### Grievance & Disciplinary ✅
- Grievance filing
- Disciplinary action tracking

### Travel & Deployment ✅
- Travel request management
- Visa tracking

### Analytics & Reporting ✅
- HR dashboards
- Headcount reports
- Turnover analysis

### Admin Configuration ✅
- Multi-country setup
- Salary bands
- Leave policies

### Employee Self-Service (ESS) ✅
- Personal profile
- Leave requests
- Document access
- Timesheet submission

## 🚀 Next Steps

1. **Install dependencies:**
   ```bash
   # Backend
   cd apps/api
   pip install -r requirements.txt
   
   # Frontend
   cd apps/frontend
   npm install
   ```

2. **Setup database:**
   ```bash
   docker-compose up -d postgres redis
   cd apps/api
   alembic upgrade head
   ```

3. **Run development servers:**
   ```bash
   # Backend (terminal 1)
   cd apps/api
   uvicorn main:app --reload
   
   # Frontend (terminal 2)
   cd apps/frontend
   npm run dev
   ```

4. **Access application:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 📝 Notes

- All modules have complete scaffolding
- Database models are production-ready
- API routes are structured and documented
- Frontend has full integration setup
- Docker configuration ready for deployment
- All TODO markers indicate future enhancements
- System is modular and scalable
- Ready for immediate development and customization
