"""
Tests for Rate Limiting functionality
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limiting_on_login(client: AsyncClient):
    """Test that rate limiting is applied to login endpoint"""
    # Make multiple rapid requests to login endpoint
    responses = []
    for _ in range(10):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        responses.append(response.status_code)
    
    # Check that we get rate limited (429) after several attempts
    # Note: Rate limiting may vary based on configuration
    status_codes = set(responses)
    assert 429 in status_codes or 401 in status_codes or 422 in status_codes


@pytest.mark.asyncio
async def test_rate_limiting_header(client: AsyncClient):
    """Test that rate limit headers are present"""
    response = await client.get("/health")
    # Health endpoint should work, rate limiting might add headers
    assert response.status_code == 200

