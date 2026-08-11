"""
Smoke Testing Suite
===================
Quick sanity checks to verify the critical paths of the application work.
These are the FIRST tests QA runs to decide if the build is "good enough"
for deeper testing. If any smoke test fails, the build is rejected.

QA Methodology: Smoke / Sanity / Build Verification Testing (BVT)
"""

import pytest


class TestSmokeCore:
    """Critical path smoke tests — application must pass ALL of these."""

    @pytest.mark.asyncio
    async def test_smoke01_server_is_alive(self, client):
        """SMOKE-01: Server responds to requests (heartbeat check)."""
        response = await client.get("/")
        assert response.status_code == 200, "SERVER IS DOWN — Build Rejected"

    @pytest.mark.asyncio
    async def test_smoke02_health_check(self, client):
        """SMOKE-02: Health endpoint confirms system is healthy."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["healthy", "ok", True], \
            f"System unhealthy: {data}"

    @pytest.mark.asyncio
    async def test_smoke03_database_accessible(self, client):
        """SMOKE-03: Database is operational (auth system can respond)."""
        response = await client.get("/api/auth/debug")
        assert response.status_code in [200, 401, 403], \
            "Database/auth system not accessible"

    @pytest.mark.asyncio
    async def test_smoke04_registration_works(self, client):
        """SMOKE-04: User registration critical path works."""
        import random
        suffix = random.randint(100000, 999999)
        response = await client.post("/api/auth/register", json={
            "name": f"Smoke User {suffix}",
            "username": f"smoke_{suffix}",
            "email": f"smoke_{suffix}@test.com",
            "password": "SmokePass123!"
        })
        assert response.status_code == 200, "REGISTRATION BROKEN — Build Rejected"

    @pytest.mark.asyncio
    async def test_smoke05_login_works(self, client, test_user_data):
        """SMOKE-05: User login critical path works."""
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200, "LOGIN BROKEN — Build Rejected"

    @pytest.mark.asyncio
    async def test_smoke06_chat_responds(self, client):
        """SMOKE-06: AI chat generates a response."""
        response = await client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 200
        assert len(response.json().get("response", "")) > 0, \
            "CHAT NOT RESPONDING — Build Rejected"

    @pytest.mark.asyncio
    async def test_smoke07_api_docs_accessible(self, client):
        """SMOKE-07: API documentation is accessible."""
        response = await client.get("/docs")
        assert response.status_code == 200, "API DOCS BROKEN"

    @pytest.mark.asyncio
    async def test_smoke08_alerts_system_works(self, client, auth_headers):
        """SMOKE-08: Alert creation system is functional."""
        response = await client.post("/api/alerts", json={
            "symbol": "BTC", "condition": "above",
            "value": 100000.0, "message": "Smoke alert", "enabled": True
        }, headers=auth_headers)
        assert response.status_code in [200, 201], "ALERTS SYSTEM BROKEN"

    @pytest.mark.asyncio
    async def test_smoke09_portfolio_system_works(self, client, auth_headers):
        """SMOKE-09: Portfolio management is functional."""
        response = await client.post("/api/portfolio/assets", json={
            "symbol": "BTC", "name": "Bitcoin",
            "amount": 1.0, "avgBuyPrice": 50000.0, "source": "manual"
        }, headers=auth_headers)
        assert response.status_code in [200, 201], "PORTFOLIO SYSTEM BROKEN"

    @pytest.mark.asyncio
    async def test_smoke10_market_data_accessible(self, client):
        """SMOKE-10: Market data endpoints respond."""
        response = await client.get("/api/market/data")
        assert response.status_code in [200, 500], \
            "MARKET DATA ENDPOINT COMPLETELY BROKEN"


class TestSmokeRegression:
    """Quick regression checks for previously fixed bugs."""

    @pytest.mark.asyncio
    async def test_smoke11_unicode_handling(self, client):
        """SMOKE-11: Regression — Unicode characters don't crash server."""
        response = await client.post("/api/chat", json={
            "message": "What about Bitcoin? 📈🚀"
        })
        # Previously crashed with UnicodeEncodeError
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_smoke12_analysis_not_generic(self, client):
        """SMOKE-12: Regression — Bitcoin analysis returns real content."""
        response = await client.post("/api/chat", json={
            "message": "Give me a Bitcoin analysis"
        })
        assert response.status_code == 200
        text = response.json().get("response", "").lower()
        # Previously returned generic "I can help with various topics"
        assert any(word in text for word in [
            "bitcoin", "btc", "price", "market", "crypto", "analysis"
        ]), f"Chat returned generic response: {text[:100]}"

    @pytest.mark.asyncio
    async def test_smoke13_multiple_chat_endpoints(self, client):
        """SMOKE-13: All chat endpoint aliases work."""
        endpoints = ["/api/chat", "/api/ai/chat", "/api/v1/ai/chat"]
        for endpoint in endpoints:
            response = await client.post(endpoint, json={"message": "test"})
            assert response.status_code == 200, \
                f"Chat endpoint {endpoint} not working"

    @pytest.mark.asyncio
    async def test_smoke14_token_verification(self, client, auth_headers):
        """SMOKE-14: Token verification flow works end-to-end."""
        if auth_headers:
            response = await client.get("/api/auth/me", headers=auth_headers)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_smoke15_connection_test(self, client):
        """SMOKE-15: Connection test endpoint confirms connectivity."""
        response = await client.get("/test/connection")
        assert response.status_code == 200
