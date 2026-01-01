"""
Tests for Approval Workflow endpoints
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_approvals_requires_auth(client: AsyncClient):
    """Test that listing approvals requires authentication"""
    response = await client.get("/api/v1/approvals/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_approval_requires_auth(client: AsyncClient):
    """Test that creating approvals requires authentication"""
    approval_data = {
        "request_type": "leave",
        "request_id": str(uuid4()),
        "approver_id": str(uuid4())
    }
    response = await client.post("/api/v1/approvals/", json=approval_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_approval_pending_endpoint_exists(client: AsyncClient):
    """Test that pending approvals endpoint exists"""
    response = await client.get("/api/v1/approvals/pending")
    # Should require auth
    assert response.status_code in [401, 200]

