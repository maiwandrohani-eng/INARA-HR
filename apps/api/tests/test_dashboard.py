"""
Tests for Dashboard endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_employee_dashboard_requires_auth(client: AsyncClient):
    """Test that employee dashboard requires authentication"""
    response = await client.get("/api/v1/dashboard/employee")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_supervisor_dashboard_requires_auth(client: AsyncClient):
    """Test that supervisor dashboard requires authentication"""
    response = await client.get("/api/v1/dashboard/supervisor")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_role_endpoint_exists(client: AsyncClient):
    """Test that user role endpoint exists"""
    response = await client.get("/api/v1/dashboard/role")
    # Should require auth
    assert response.status_code in [401, 200]

