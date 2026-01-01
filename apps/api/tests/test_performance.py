"""
Tests for Performance Management endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_performance_reviews_requires_auth(client: AsyncClient):
    """Test that listing performance reviews requires authentication"""
    response = await client.get("/api/v1/performance/reviews")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_performance_review_requires_auth(client: AsyncClient):
    """Test that creating performance reviews requires authentication"""
    review_data = {
        "employee_id": str(uuid4()),
        "review_type": "annual",
        "review_period_start": "2024-01-01",
        "review_period_end": "2024-12-31"
    }
    response = await client.post("/api/v1/performance/reviews", json=review_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_performance_goals_endpoint_exists(client: AsyncClient):
    """Test that performance goals endpoint exists"""
    response = await client.get("/api/v1/performance/goals")
    # Should require auth
    assert response.status_code in [401, 200]

