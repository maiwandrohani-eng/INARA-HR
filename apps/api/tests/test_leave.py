"""
Tests for Leave Management endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_list_leave_requests_requires_auth(client: AsyncClient):
    """Test that listing leave requests requires authentication"""
    response = await client.get("/api/v1/leave/requests")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_leave_request_requires_auth(client: AsyncClient):
    """Test that creating leave requests requires authentication"""
    leave_data = {
        "leave_type": "annual",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=5)),
        "reason": "Vacation"
    }
    response = await client.post("/api/v1/leave/requests", json=leave_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_leave_policies_endpoint_exists(client: AsyncClient):
    """Test that leave policies endpoint exists"""
    response = await client.get("/api/v1/leave/policies")
    # Should require auth
    assert response.status_code in [401, 200]


@pytest.mark.asyncio
async def test_leave_balance_endpoint_exists(client: AsyncClient):
    """Test that leave balance endpoint exists"""
    response = await client.get("/api/v1/leave/balance")
    # Should require auth
    assert response.status_code in [401, 200]

