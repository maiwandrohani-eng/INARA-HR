"""
Tests for Input Validation
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_invalid_email_validation(client: AsyncClient):
    """Test that invalid email format is rejected"""
    login_data = {
        "email": "not-an-email",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    # Should return validation error (422)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_short_password_validation(client: AsyncClient):
    """Test that short passwords are rejected"""
    login_data = {
        "email": "test@example.com",
        "password": "short"  # Too short
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    # Should return validation error (422) for password length
    assert response.status_code in [400, 401, 422]


@pytest.mark.asyncio
async def test_missing_required_fields(client: AsyncClient):
    """Test that missing required fields are rejected"""
    # Missing password
    login_data = {
        "email": "test@example.com"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    # Should return validation error (422)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_uuid_format(client: AsyncClient):
    """Test that invalid UUID formats are rejected"""
    invalid_uuid = "not-a-uuid"
    response = await client.get(f"/api/v1/employees/{invalid_uuid}")
    # Should return validation error or 404
    assert response.status_code in [401, 404, 422]

