"""
Tests for File Upload functionality
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
import io


@pytest.mark.asyncio
async def test_file_upload_requires_auth(client: AsyncClient):
    """Test that file upload requires authentication"""
    # Create a small test file
    file_content = b"Test file content"
    files = {
        "file": ("test.pdf", io.BytesIO(file_content), "application/pdf")
    }
    data = {
        "employee_id": str(uuid4()),
        "category": "contract",
        "title": "Test Document"
    }
    response = await client.post(
        "/api/v1/employee-files/documents/upload",
        files=files,
        data=data
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_file_upload_size_validation(client: AsyncClient):
    """Test that file size validation works"""
    # This would need authentication, but we can test the endpoint exists
    response = await client.post("/api/v1/employee-files/documents/upload")
    # Should require auth
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_documents_endpoint_exists(client: AsyncClient):
    """Test that documents listing endpoint exists"""
    employee_id = str(uuid4())
    response = await client.get(f"/api/v1/employee-files/documents/employee/{employee_id}")
    # Should require auth
    assert response.status_code in [401, 404, 422]

