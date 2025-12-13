# INARA HRIS - API Documentation

## 🏗️ Backend Architecture

The backend follows a **clean, modular architecture** with clear separation of concerns:

```
/apps/api
├── core/                    # Core infrastructure
│   ├── config.py           # Configuration management
│   ├── database.py         # Database setup
│   ├── security.py         # Authentication & security
│   ├── dependencies.py     # FastAPI dependencies
│   ├── exceptions.py       # Custom exceptions
│   └── models.py           # Base database models
│
├── modules/                # HR modules (15 total)
│   ├── auth/              # Authentication & RBAC
│   ├── employees/         # Employee management
│   ├── recruitment/       # ATS - Applicant tracking
│   ├── onboarding/        # Onboarding checklists
│   ├── leave/             # Leave & attendance
│   ├── timesheets/        # Time tracking
│   ├── performance/       # Performance management
│   ├── learning/          # L&D
│   ├── compensation/      # Payroll support
│   ├── safeguarding/      # Case management
│   ├── grievance/         # Grievance & disciplinary
│   ├── travel/            # Travel & deployment
│   ├── analytics/         # HR analytics
│   ├── admin/             # Configuration
│   └── ess/               # Employee self-service
│
├── alembic/               # Database migrations
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
└── Dockerfile            # Container configuration
```

## 📊 Database Schema

### Core Tables

**Authentication:**
- `users` - User accounts
- `roles` - RBAC roles
- `permissions` - Granular permissions
- `user_roles` - Many-to-many relationship
- `role_permissions` - Many-to-many relationship

**Employee Management:**
- `employees` - Employee master data
- `departments` - Organizational structure
- `positions` - Job positions/titles
- `contracts` - Employment contracts
- `employee_documents` - Document storage

**Leave Management:**
- `leave_policies` - Country-specific policies
- `leave_balances` - Employee balances
- `leave_requests` - Leave applications
- `attendance_records` - Daily attendance

**Performance:**
- `performance_goals` - Employee goals
- `performance_reviews` - Appraisals
- `performance_improvement_plans` - PIPs

**And 20+ more tables for all HR functions...**

## 🔐 Authentication & Authorization

### JWT-Based Authentication

```python
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Role-Based Access Control (RBAC)

**Default Roles:**
- `super_admin` - Full system access
- `hr_admin` - HR operations
- `hr_manager` - Team management
- `line_manager` - Team oversight
- `employee` - Self-service only

**Permission Format:** `resource:action`
- `employees:read`, `employees:write`
- `leave:approve`, `payroll:admin`
- `safeguarding:investigate`

### Protecting Routes

```python
from core.dependencies import require_hr_write

@router.post("/employees")
async def create_employee(
    data: EmployeeCreate,
    current_user = Depends(require_hr_write)
):
    # Only users with hr:write permission can access
    pass
```

## 🚀 API Endpoints

### Employee Management

```
GET    /api/v1/employees              # List employees
POST   /api/v1/employees              # Create employee
GET    /api/v1/employees/{id}         # Get employee
PATCH  /api/v1/employees/{id}         # Update employee
DELETE /api/v1/employees/{id}         # Delete employee
```

### Leave Management

```
GET    /api/v1/leave/balance          # Get leave balance
GET    /api/v1/leave/requests         # List leave requests
POST   /api/v1/leave/requests         # Submit leave request
POST   /api/v1/leave/requests/{id}/approve  # Approve/reject
```

### Timesheets

```
GET    /api/v1/timesheets             # List timesheets
POST   /api/v1/timesheets             # Create timesheet
POST   /api/v1/timesheets/{id}/entries  # Add entry
POST   /api/v1/timesheets/{id}/submit   # Submit for approval
```

## 🗄️ Database Setup

### Initial Setup

```bash
# Navigate to API directory
cd apps/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# (Optional) Create migration after model changes
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Seed Data

To create initial admin user and permissions, run:

```python
python scripts/seed_data.py
```

This creates:
- Super admin user: `admin@inara.org` / `Admin@123`
- All default roles and permissions
- Sample departments and positions

## 📝 Development Guide

### Adding a New Module

1. **Create module directory:**
```bash
mkdir apps/api/modules/new_module
```

2. **Create module files:**
- `models.py` - Database models
- `schemas.py` - Pydantic schemas
- `repositories.py` - Database operations
- `services.py` - Business logic
- `routes.py` - API endpoints

3. **Register routes in main.py:**
```python
from modules.new_module.routes import router as new_module_router
app.include_router(new_module_router, prefix="/api/v1/new-module", tags=["New Module"])
```

4. **Create migration:**
```bash
alembic revision --autogenerate -m "Add new module tables"
alembic upgrade head
```

### Code Style

- Follow PEP 8
- Use type hints
- Document all functions with docstrings
- Keep functions small and focused
- Use meaningful variable names

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## 🔧 Configuration

Key configuration in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/inara_hris

# Security
SECRET_KEY=your-super-secret-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000

# File Storage
S3_BUCKET_NAME=inara-hris-files
```

## 📚 Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Pydantic Docs: https://docs.pydantic.dev
