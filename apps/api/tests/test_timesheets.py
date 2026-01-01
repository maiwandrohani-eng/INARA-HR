"""
Tests for Timesheet Management endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
async def test_list_timesheets_requires_auth(client: AsyncClient):
    """Test that listing timesheets requires authentication"""
    response = await client.get("/api/v1/timesheets/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_timesheet_requires_auth(client: AsyncClient):
    """Test that creating timesheets requires authentication"""
    timesheet_data = {
        "period_start": str(date.today()),
        "period_end": str(date.today()),
        "entries": []
    }
    response = await client.post("/api/v1/timesheets/", json=timesheet_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_projects_endpoint_exists(client: AsyncClient):
    """Test that projects endpoint exists"""
    response = await client.get("/api/v1/timesheets/projects")
    # Should require auth
    assert response.status_code in [401, 200]

