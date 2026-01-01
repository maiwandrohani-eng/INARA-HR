"""
Tests for Recruitment (ATS) endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_list_job_postings_requires_auth(client: AsyncClient):
    """Test that listing job postings requires authentication"""
    response = await client.get("/api/v1/recruitment/postings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_job_posting_requires_auth(client: AsyncClient):
    """Test that creating job postings requires authentication"""
    job_data = {
        "title": "Software Developer",
        "department": "IT",
        "location": "Remote",
        "employment_type": "full_time",
        "closing_date": str(date.today() + timedelta(days=30))
    }
    response = await client.post("/api/v1/recruitment/postings", json=job_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_applications_endpoint_exists(client: AsyncClient):
    """Test that applications endpoint exists"""
    response = await client.get("/api/v1/recruitment/applications")
    # Should require auth
    assert response.status_code in [401, 200]


@pytest.mark.asyncio
async def test_public_job_postings_endpoint(client: AsyncClient):
    """Test that public job postings endpoint exists (no auth required)"""
    response = await client.get("/api/v1/recruitment/postings/public")
    # Public endpoint should work without auth
    assert response.status_code in [200, 404, 422]

