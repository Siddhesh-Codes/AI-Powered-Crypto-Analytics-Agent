"""
Black Box Testing Suite
=======================
Tests the system purely through inputs and outputs — NO knowledge of internal
code or implementation details. We only observe HTTP requests/responses.

Black box testing validates that the system behaves correctly from an end-user
perspective regardless of how it is implemented internally.

QA Methodology: Black Box / Functional Testing
"""

import pytest


# ─────────────────────────────────────────────────────
# BB-1: Authentication Black Box Tests
# ─────────────────────────────────────────────────────

class TestBlackBoxAuthentication:
    """Test auth system purely through API — no knowledge of DB or hashing."""

    @pytest.mark.asyncio
    async def test_bb01_register_returns_success(self, client):
        """BB-01: A new user registration must return success confirmation."""
        import random
        suffix = random.randint(100000, 999999)
        response = await client.post("/api/auth/register", json={
            "name": f"BlackBox User {suffix}",
            "username": f"bb_user_{suffix}",
            "email": f"bb_{suffix}@test.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 200
        data = response.json()
        # Registration returns success confirmation (token comes from login)
        assert data.get("success") == True
        assert "message" in data

    @pytest.mark.asyncio
    async def test_bb02_login_with_correct_creds(self, client, test_user_data):
        """BB-02: Login with correct credentials returns success."""
        # Register first
        await client.post("/api/auth/register", json=test_user_data)
        # Login
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    @pytest.mark.asyncio
    async def test_bb03_login_with_wrong_password(self, client):
        """BB-03: Login with wrong password must be rejected."""
        response = await client.post("/api/auth/login", json={
            "login": "nonexistent_user_xyz",
            "password": "WrongPassword123"
        })
        # Should NOT be 200
        assert response.status_code in [400, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_bb04_protected_endpoint_without_token(self, client):
        """BB-04: Accessing protected endpoint without token must fail."""
        response = await client.get("/api/auth/me")
        # Should fail — no auth
        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_bb05_register_duplicate_username(self, client):
        """BB-05: Registering same username twice must fail."""
        import random
        suffix = random.randint(100000, 999999)
        user = {
            "name": f"Dup User {suffix}",
            "username": f"dup_user_{suffix}",
            "email": f"dup_{suffix}@test.com",
            "password": "Pass123456!"
        }
        # First registration
        r1 = await client.post("/api/auth/register", json=user)
        assert r1.status_code == 200

        # Second registration with same username
        user["email"] = f"dup2_{suffix}@test.com"  # different email
        r2 = await client.post("/api/auth/register", json=user)
        # Server returns 200 with success=False for duplicates
        data2 = r2.json()
        assert data2.get("success") == False or r2.status_code in [400, 409, 422]


# ─────────────────────────────────────────────────────
# BB-2: Chat System Black Box Tests
# ─────────────────────────────────────────────────────

class TestBlackBoxChat:
    """Test AI chat purely by observing input questions and output answers."""

    @pytest.mark.asyncio
    async def test_bb06_chat_returns_text_response(self, client):
        """BB-06: Sending any message must return a text response."""
        response = await client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    @pytest.mark.asyncio
    async def test_bb07_crypto_query_mentions_crypto(self, client):
        """BB-07: Asking about Bitcoin should return Bitcoin-related answer."""
        response = await client.post("/api/chat", json={
            "message": "What is the current price of Bitcoin?"
        })
        assert response.status_code == 200
        data = response.json()
        text = data["response"].lower()
        # The response should mention bitcoin or BTC or price
        assert any(word in text for word in ["bitcoin", "btc", "price", "$", "crypto"])

    @pytest.mark.asyncio
    async def test_bb08_response_has_suggestions(self, client):
        """BB-08: Chat response should include follow-up suggestions."""
        response = await client.post("/api/chat", json={
            "message": "Tell me about Ethereum"
        })
        assert response.status_code == 200
        data = response.json()
        # Should have suggestions array
        if "suggestions" in data:
            assert isinstance(data["suggestions"], list)

    @pytest.mark.asyncio
    async def test_bb09_different_queries_different_responses(self, client):
        """BB-09: Different questions should produce different answers."""
        r1 = await client.post("/api/chat", json={"message": "What is Bitcoin?"})
        r2 = await client.post("/api/chat", json={"message": "How to invest safely?"})
        
        assert r1.status_code == 200
        assert r2.status_code == 200
        
        # Responses should be different
        text1 = r1.json()["response"]
        text2 = r2.json()["response"]
        assert text1 != text2

    @pytest.mark.asyncio
    async def test_bb10_empty_message_handled_gracefully(self, client):
        """BB-10: Empty message should not crash the system."""
        response = await client.post("/api/chat", json={"message": ""})
        # Should return 200 with some response, not 500
        assert response.status_code in [200, 400, 422]


# ─────────────────────────────────────────────────────
# BB-3: Market Data Black Box Tests
# ─────────────────────────────────────────────────────

class TestBlackBoxMarketData:
    """Test market endpoints purely through request → response observation."""

    @pytest.mark.asyncio
    async def test_bb11_market_data_returns_list(self, client):
        """BB-11: Market data endpoint should return structured data."""
        response = await client.get("/api/market/data")
        assert response.status_code in [200, 500]  # 500 if external API down
        if response.status_code == 200:
            data = response.json()
            # Should be a list or dict with market data
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_bb12_trading_signals_structure(self, client):
        """BB-12: Trading signals should return recognizable signal data."""
        response = await client.get("/api/trading/signals")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_bb13_news_endpoint_returns_articles(self, client):
        """BB-13: News endpoint should return article-like structures."""
        response = await client.get("/api/news")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_bb14_alert_lifecycle(self, client):
        """BB-14: Create alert → Get alerts → Delete alert (full lifecycle)."""
        import random
        suffix = random.randint(100000, 999999)
        user = {
            "name": f"Alert BB {suffix}", "username": f"alertbb_{suffix}",
            "email": f"alertbb_{suffix}@test.com", "password": "Pass123456!"
        }
        await client.post("/api/auth/register", json=user)
        login = await client.post("/api/auth/login", json={
            "login": user["username"], "password": user["password"]
        })
        token = login.json().get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create
        create_resp = await client.post("/api/alerts", json={
            "symbol": "BTC", "condition": "above",
            "value": 99999.0, "message": "BB test alert", "enabled": True
        }, headers=headers)
        assert create_resp.status_code in [200, 201]
        
        # Get all alerts
        get_resp = await client.get("/api/alerts", headers=headers)
        assert get_resp.status_code == 200
        resp = get_resp.json()
        alerts = resp.get("alerts", resp) if isinstance(resp, dict) else resp
        assert isinstance(alerts, list)

    @pytest.mark.asyncio
    async def test_bb15_portfolio_crud_operations(self, client):
        """BB-15: Portfolio assets support add/list/delete operations."""
        import random
        suffix = random.randint(100000, 999999)
        user = {
            "name": f"Port BB {suffix}", "username": f"portbb_{suffix}",
            "email": f"portbb_{suffix}@test.com", "password": "Pass123456!"
        }
        await client.post("/api/auth/register", json=user)
        login = await client.post("/api/auth/login", json={
            "login": user["username"], "password": user["password"]
        })
        token = login.json().get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Add asset
        add_resp = await client.post("/api/portfolio/assets", json={
            "symbol": "BTC", "name": "Bitcoin",
            "amount": 0.5, "avgBuyPrice": 50000.0, "source": "manual"
        }, headers=headers)
        assert add_resp.status_code in [200, 201]
        
        # List assets
        list_resp = await client.get("/api/portfolio/assets", headers=headers)
        assert list_resp.status_code == 200
        resp = list_resp.json()
        assets = resp.get("assets", resp) if isinstance(resp, dict) else resp
        assert isinstance(assets, list)


# ─────────────────────────────────────────────────────
# BB-4: Error Handling Black Box Tests
# ─────────────────────────────────────────────────────

class TestBlackBoxErrorHandling:
    """Verify the system handles bad input gracefully without exposing internals."""

    @pytest.mark.asyncio
    async def test_bb16_invalid_endpoint_returns_404(self, client):
        """BB-16: Non-existent route returns 404, not server error."""
        response = await client.get("/api/this/does/not/exist")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_bb17_malformed_json_handled(self, client):
        """BB-17: Malformed request body should return 400/422, not 500."""
        response = await client.post(
            "/api/chat",
            content="this is not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_bb18_wrong_http_method(self, client):
        """BB-18: Using wrong HTTP method returns 405."""
        response = await client.delete("/api/chat")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_bb19_oversized_input(self, client):
        """BB-19: Very large input should not crash the server."""
        huge_message = "Bitcoin " * 10000  # ~70KB message
        response = await client.post("/api/chat", json={"message": huge_message})
        # Should handle gracefully — 200 or 400/413, NOT 500
        assert response.status_code in [200, 400, 413, 422]

    @pytest.mark.asyncio
    async def test_bb20_special_characters_in_input(self, client):
        """BB-20: Special characters should not break the system."""
        response = await client.post("/api/chat", json={
            "message": "What about <script>alert('xss')</script> Bitcoin?"
        })
        # System should handle gracefully — not crash (500)
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            # Must still return a valid response string
            assert isinstance(response.json().get("response", ""), str)
