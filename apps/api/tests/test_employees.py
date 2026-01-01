"""
Tests for Employee Management endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_employees_requires_auth(client: AsyncClient):
    """Test that listing employees requires authentication"""
    response = await client.get("/api/v1/employees/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_employee_endpoint_exists(client: AsyncClient):
    """Test that employee detail endpoint exists"""
    employee_id = str(uuid4())
    response = await client.get(f"/api/v1/employees/{employee_id}")
    # Should require auth
    assert response.status_code in [401, 404]


@pytest.mark.asyncio
async def test_create_employee_requires_auth(client: AsyncClient):
    """Test that creating employees requires authentication"""
    employee_data = {
        "first_name": "Test",
        "last_name": "Employee",
        "email": "test@example.com",
        "employee_number": "EMP001"
    }
    response = await client.post("/api/v1/employees/", json=employee_data)
    assert response.status_code == 401

