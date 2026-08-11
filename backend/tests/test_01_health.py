"""
Test Suite 1: API Health & Connectivity Tests
Tests all health check and root endpoints
"""

import pytest


class TestHealthEndpoints:
    """Test all health check and connectivity endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """TC-1.1: Root endpoint returns server status"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "ai_status" in data
        assert data["ai_status"] in ["online", "fallback"]

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """TC-1.2: /health endpoint returns healthy status"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_connection_endpoint(self, client):
        """TC-1.3: /test/connection endpoint confirms API connectivity"""
        response = await client.get("/test/connection")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "timestamp" in data
        assert data["port"] == 8000

    @pytest.mark.asyncio
    async def test_ai_chat_health(self, client):
        """TC-1.4: AI chat health endpoint returns service status"""
        response = await client.get("/api/v1/ai/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ai_service"] in ["online", "fallback"]

    @pytest.mark.asyncio
    async def test_docs_endpoint(self, client):
        """TC-1.5: Swagger docs endpoint is accessible"""
        response = await client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_redoc_endpoint(self, client):
        """TC-1.6: ReDoc endpoint is accessible"""
        response = await client.get("/redoc")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_nonexistent_endpoint(self, client):
        """TC-1.7: Non-existent endpoint returns 404"""
        response = await client.get("/api/nonexistent")
        assert response.status_code == 404
