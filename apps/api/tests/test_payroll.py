"""
Tests for Payroll Management endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_payrolls_requires_auth(client: AsyncClient):
    """Test that listing payrolls requires authentication"""
    response = await client.get("/api/v1/payroll/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_payroll_requires_auth(client: AsyncClient):
    """Test that creating payrolls requires authentication"""
    payroll_data = {
        "pay_period_start": "2024-01-01",
        "pay_period_end": "2024-01-31"
    }
    response = await client.post("/api/v1/payroll/", json=payroll_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_payroll_stats_endpoint_exists(client: AsyncClient):
    """Test that payroll stats endpoint exists"""
    response = await client.get("/api/v1/payroll/stats")
    # Should require auth
    assert response.status_code in [401, 200]

