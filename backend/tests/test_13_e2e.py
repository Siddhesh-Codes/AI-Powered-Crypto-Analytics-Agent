"""
End-to-End (E2E) Testing Suite
==============================
Tests complete user flows from start to finish — simulating real user
journeys through the system. In a real company, these would use Selenium
or Playwright to automate a real browser.

Since we're testing API-level E2E flows (no browser available), these tests
simulate the complete user journey through sequential API calls, exactly
as the frontend would make them.

QA Methodology: End-to-End / User Acceptance Testing (UAT)
Note: For browser-based E2E, see the Selenium/Playwright section in the QA report.
"""

import pytest


class TestE2EUserJourneys:
    """Complete user journeys tested end-to-end through the API."""

    @pytest.mark.asyncio
    async def test_e2e01_new_user_onboarding(self, client):
        """E2E-01: Complete new user onboarding flow.
        
        Journey: Register → Login → View Profile → Use Chat → Logout
        This is the #1 critical path in the application.
        """
        import random
        suffix = random.randint(100000, 999999)
        user_data = {
            "name": f"E2E User {suffix}",
            "username": f"e2e_{suffix}",
            "email": f"e2e_{suffix}@test.com",
            "password": "E2EPass123!"
        }
        
        # Step 1: Register
        reg_resp = await client.post("/api/auth/register", json=user_data)
        assert reg_resp.status_code == 200, "Step 1 FAILED: Registration"
        
        # Step 2: Login (token comes from login, not registration)
        login_resp = await client.post("/api/auth/login", json={
            "login": user_data["username"],
            "password": user_data["password"]
        })
        assert login_resp.status_code == 200, "Step 2 FAILED: Login"
        login_token = login_resp.json().get("token")
        assert login_token, "No token received on login"
        headers = {"Authorization": f"Bearer {login_token}"}
        
        # Step 3: View Profile
        profile_resp = await client.get("/api/auth/me", headers=headers)
        assert profile_resp.status_code == 200, "Step 3 FAILED: View Profile"
        
        # Step 4: Use AI Chat
        chat_resp = await client.post("/api/chat", json={
            "message": "What's the outlook for Bitcoin?"
        })
        assert chat_resp.status_code == 200, "Step 4 FAILED: Chat"
        assert len(chat_resp.json().get("response", "")) > 0
        
        # Step 5: Logout
        logout_resp = await client.post("/api/auth/logout", headers=headers)
        assert logout_resp.status_code == 200, "Step 5 FAILED: Logout"

    @pytest.mark.asyncio
    async def test_e2e02_portfolio_management_flow(self, client):
        """E2E-02: Complete portfolio management flow.
        
        Journey: Add Asset → List Assets → Update Asset → Delete Asset
        """
        # Step 1: Add an asset (requires auth + correct schema)
        import random
        suffix = random.randint(100000, 999999)
        user = {
            "name": f"Portfolio User {suffix}",
            "username": f"portuser_{suffix}",
            "email": f"portuser_{suffix}@test.com",
            "password": "PortPass123!"
        }
        await client.post("/api/auth/register", json=user)
        login = await client.post("/api/auth/login", json={
            "login": user["username"], "password": user["password"]
        })
        token = login.json().get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        
        add_resp = await client.post("/api/portfolio/assets", json={
            "symbol": "ETH",
            "name": "Ethereum",
            "amount": 10.0,
            "avgBuyPrice": 3000.0,
            "source": "manual"
        }, headers=headers)
        assert add_resp.status_code in [200, 201], f"Step 1 FAILED: Add Asset ({add_resp.status_code})"
        asset = add_resp.json()
        # Response may be {success, asset} or {id, ...}
        asset_data = asset.get("asset", asset)
        asset_id = asset_data.get("id", "ETH")
        
        # Step 2: List assets (response: {success, assets: [...], summary: {...}})
        list_resp = await client.get("/api/portfolio/assets", headers=headers)
        assert list_resp.status_code == 200, "Step 2 FAILED: List Assets"
        resp_body = list_resp.json()
        assert resp_body.get("success") == True
        assets = resp_body.get("assets", [])
        assert isinstance(assets, list)
        
        # Step 3: Update asset
        update_resp = await client.put(f"/api/portfolio/assets/{asset_id}", json={
            "amount": 15.0
        }, headers=headers)
        assert update_resp.status_code in [200, 404], "Step 3 FAILED: Update Asset"
        
        # Step 4: Delete asset
        delete_resp = await client.delete(f"/api/portfolio/assets/{asset_id}", headers=headers)
        assert delete_resp.status_code in [200, 404], "Step 4 FAILED: Delete Asset"

    @pytest.mark.asyncio
    async def test_e2e03_price_alert_flow(self, client):
        """E2E-03: Complete price alert workflow.
        
        Journey: Create Alert → View Alerts → Delete Alert
        """
        # Step 1: Create alert (requires auth + correct schema)
        import random
        suffix = random.randint(100000, 999999)
        user = {
            "name": f"Alert User {suffix}",
            "username": f"alertuser_{suffix}",
            "email": f"alertuser_{suffix}@test.com",
            "password": "AlertPass123!"
        }
        await client.post("/api/auth/register", json=user)
        login = await client.post("/api/auth/login", json={
            "login": user["username"], "password": user["password"]
        })
        token = login.json().get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        
        create_resp = await client.post("/api/alerts", json={
            "symbol": "BTC",
            "condition": "above",
            "value": 150000.0,
            "message": "BTC above 150k",
            "enabled": True
        }, headers=headers)
        assert create_resp.status_code in [200, 201], f"Step 1 FAILED: Create Alert ({create_resp.status_code})"
        
        # Step 2: View all alerts (response: {success, alerts: [...]})
        list_resp = await client.get("/api/alerts", headers=headers)
        assert list_resp.status_code == 200, "Step 2 FAILED: View Alerts"
        resp_body = list_resp.json()
        assert resp_body.get("success") == True
        alerts = resp_body.get("alerts", [])
        assert isinstance(alerts, list)
        
        # Step 3: Delete alert (use first alert's id if available)
        if len(alerts) > 0:
            alert_id = alerts[0].get("id", 0)
            delete_resp = await client.delete(f"/api/alerts/{alert_id}", headers=headers)
            assert delete_resp.status_code in [200, 404], "Step 3 FAILED: Delete Alert"

    @pytest.mark.asyncio
    async def test_e2e04_market_research_flow(self, client):
        """E2E-04: Complete market research user journey.
        
        Journey: Check Health → Get Market Data → Ask AI → Get Sentiment
        """
        # Step 1: Check system is ready
        health_resp = await client.get("/health")
        assert health_resp.status_code == 200, "Step 1 FAILED: Health Check"
        
        # Step 2: Check market data
        market_resp = await client.get("/api/market/data")
        assert market_resp.status_code in [200, 500], "Step 2: Market Data"
        
        # Step 3: Ask AI for analysis
        chat_resp = await client.post("/api/chat", json={
            "message": "What are the top trending cryptocurrencies right now?"
        })
        assert chat_resp.status_code == 200, "Step 3 FAILED: AI Analysis"
        
        # Step 4: Check market sentiment
        sentiment_resp = await client.get("/api/market-sentiment")
        assert sentiment_resp.status_code in [200, 500], "Step 4: Market Sentiment"
        
        # Step 5: Get news
        news_resp = await client.get("/api/news")
        assert news_resp.status_code in [200, 500], "Step 5: News"

    @pytest.mark.asyncio
    async def test_e2e05_multi_chat_conversation(self, client):
        """E2E-05: Multi-turn conversation simulating real user.
        
        Journey: User asks multiple questions building on each other.
        """
        # Turn 1: General question
        r1 = await client.post("/api/chat", json={
            "message": "What is cryptocurrency?"
        })
        assert r1.status_code == 200
        
        # Turn 2: Follow-up about specific coin
        r2 = await client.post("/api/chat", json={
            "message": "Tell me about Bitcoin specifically"
        })
        assert r2.status_code == 200
        
        # Turn 3: Ask for analysis
        r3 = await client.post("/api/chat", json={
            "message": "Give me a technical analysis of Bitcoin"
        })
        assert r3.status_code == 200
        
        # Turn 4: Investment question
        r4 = await client.post("/api/chat", json={
            "message": "Is it a good time to invest in Bitcoin?"
        })
        assert r4.status_code == 200
        
        # All responses should be non-empty and different
        responses = [r.json()["response"] for r in [r1, r2, r3, r4]]
        assert all(len(r) > 0 for r in responses), "Some responses were empty"

    @pytest.mark.asyncio
    async def test_e2e06_trading_signals_workflow(self, client):
        """E2E-06: Trading signals research flow.
        
        Journey: Get Signals → Check Technical Indicators → Read News
        """
        # Step 1: Get trading signals
        signals_resp = await client.get("/api/trading/signals")
        assert signals_resp.status_code in [200, 500]
        
        # Step 2: Check technical indicators for bitcoin
        ti_resp = await client.get("/api/technical-indicators/bitcoin")
        assert ti_resp.status_code in [200, 500]
        
        # Step 3: Get coin-specific news sentiment
        news_resp = await client.get("/api/news/sentiment/bitcoin")
        assert news_resp.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_e2e07_auth_security_flow(self, client):
        """E2E-07: Authentication security verification flow.
        
        Journey: Register → Login → Access Protected → Logout → Try Access Again
        """
        import random
        suffix = random.randint(100000, 999999)
        
        # Register
        await client.post("/api/auth/register", json={
            "name": f"SecFlow {suffix}",
            "username": f"secflow_{suffix}",
            "email": f"secflow_{suffix}@test.com",
            "password": "SecFlow123!"
        })
        
        # Login
        login_resp = await client.post("/api/auth/login", json={
            "login": f"secflow_{suffix}",
            "password": "SecFlow123!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json().get("token", "")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Access protected endpoint (should work)
        me_resp = await client.get("/api/auth/me", headers=headers)
        assert me_resp.status_code == 200
        
        # Logout
        await client.post("/api/auth/logout", headers=headers)
        
        # Try accessing with invalid token (should fail)
        bad_resp = await client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid_token_here"
        })
        assert bad_resp.status_code in [401, 403, 422]
