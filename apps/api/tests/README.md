# INARA HRIS - Test Suite

Comprehensive test suite for all system functions and modules.

## Test Coverage

### ✅ Authentication Tests (`test_auth.py`)
- User registration
- Login functionality
- Password validation
- Rate limiting on auth endpoints
- Health check endpoints

### ✅ Employee Management Tests (`test_employees.py`)
- List employees (requires auth)
- Get employee details
- Create employee (requires auth)
- Employee CRUD operations

### ✅ Leave Management Tests (`test_leave.py`)
- List leave requests
- Create leave requests
- Leave policies
- Leave balance tracking
- Attendance records

### ✅ Timesheet Tests (`test_timesheets.py`)
- List timesheets
- Create timesheets
- Project listing
- Timesheet submission
- Approval workflow

### ✅ Performance Management Tests (`test_performance.py`)
- Performance reviews
- Performance goals
- 360-degree reviews
- PIP (Performance Improvement Plans)

### ✅ Payroll Tests (`test_payroll.py`)
- Payroll listing
- Payroll creation
- Payroll stats
- Payslip generation

### ✅ Approval Workflow Tests (`test_approvals.py`)
- List approvals
- Create approval requests
- Pending approvals
- Approval status updates

### ✅ Recruitment Tests (`test_recruitment.py`)
- Job postings
- Applications
- Public job board
- Interview scheduling

### ✅ Dashboard Tests (`test_dashboard.py`)
- Employee dashboard
- Supervisor dashboard
- User role detection
- Dashboard data endpoints

### ✅ File Upload Tests (`test_file_uploads.py`)
- Document upload
- File size validation
- File extension validation
- Document listing

### ✅ Rate Limiting Tests (`test_rate_limiting.py`)
- Rate limit enforcement
- Rate limit headers
- Auth endpoint rate limiting

### ✅ Validation Tests (`test_validation.py`)
- Email validation
- Password validation
- Required field validation
- UUID format validation

### ✅ Integration Tests (`test_integration.py`)
- Complete workflow testing
- End-to-end scenarios
- Module integration

## Running Tests

### Run All Tests
```bash
cd apps/api
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_auth.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run All Tests with Report
```bash
cd apps/api
./tests/run_all_tests.sh
```

### Run Specific Test
```bash
pytest tests/test_auth.py::test_login_endpoint_exists -v
```

## Test Configuration

Tests use:
- In-memory SQLite database (fast, isolated)
- Async test client (httpx)
- Fixtures for common setup (users, employees, etc.)
- Test database isolation per test

## Test Environment Variables

Tests automatically use test-specific configuration:
- `ENVIRONMENT=test`
- `DATABASE_URL=sqlite+aiosqlite:///:memory:`
- `RATE_LIMIT_ENABLED=false` (for faster tests)

## Adding New Tests

1. Create test file in `tests/` directory
2. Use `@pytest.mark.asyncio` for async tests
3. Use `client` fixture for API requests
4. Use `db_session` fixture for database operations
5. Follow naming convention: `test_<functionality>`

## Test Structure Example

```python
@pytest.mark.asyncio
async def test_function_name(client: AsyncClient):
    """Test description"""
    response = await client.get("/api/v1/endpoint")
    assert response.status_code == expected_code
```

## Notes

- Most tests verify authentication requirements (should return 401)
- Some tests verify endpoint existence and structure
- Integration tests verify complete workflows
- All tests are isolated and can run independently

