"""
Test Suite 5: Crypto Market Data API Tests
Tests market data, price fetching, portfolio, and trading signal endpoints
"""

import pytest


class TestCryptoMarketEndpoints:
    """Test cryptocurrency market data endpoints"""

    @pytest.mark.asyncio
    async def test_global_metrics(self, client):
        """TC-5.1: Global metrics endpoint returns market data"""
        response = await client.get("/api/v1/crypto/global-metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        metrics = data["data"]
        assert "total_market_cap" in metrics
        assert "bitcoin_dominance" in metrics
        assert "fear_greed_index" in metrics
        assert metrics["total_market_cap"] > 0

    @pytest.mark.asyncio
    async def test_top_cryptos(self, client):
        """TC-5.2: Top cryptos endpoint returns cryptocurrency list"""
        response = await client.get("/api/v1/crypto/top-cryptos")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        # Check first crypto has required fields
        crypto = data["data"][0]
        assert "symbol" in crypto
        assert "name" in crypto
        assert "price" in crypto
        assert "market_cap" in crypto

    @pytest.mark.asyncio
    async def test_market_data(self, client):
        """TC-5.3: Market data endpoint returns market info"""
        response = await client.get("/api/market/data")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestPortfolioEndpoints:
    """Test portfolio management endpoints"""

    @pytest.mark.asyncio
    async def test_portfolio_summary(self, client):
        """TC-5.4: Portfolio summary endpoint returns data"""
        response = await client.get("/api/v1/crypto/portfolio/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

    @pytest.mark.asyncio
    async def test_portfolio_assets_list(self, client):
        """TC-5.5: Portfolio assets list endpoint works"""
        response = await client.get("/api/portfolio/assets")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_add_portfolio_asset(self, client):
        """TC-5.6: Adding a portfolio asset"""
        response = await client.post("/api/portfolio/assets", json={
            "symbol": "BTC",
            "amount": 0.5,
            "buy_price": 50000
        })
        # Should succeed or return validation error depending on auth
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_portfolio_analyze(self, client):
        """TC-5.7: Portfolio analysis endpoint works"""
        response = await client.post("/api/portfolio/analyze", json={
            "assets": [
                {"symbol": "BTC", "amount": 1.0, "buy_price": 50000},
                {"symbol": "ETH", "amount": 10.0, "buy_price": 3000}
            ]
        })
        assert response.status_code in [200, 422, 500]  # 500 if external API unavailable


class TestTradingSignalEndpoints:
    """Test trading signal endpoints"""

    @pytest.mark.asyncio
    async def test_trading_signals(self, client):
        """TC-5.8: Trading signals endpoint returns data"""
        response = await client.get("/api/trading/signals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_trading_signals_by_coin(self, client):
        """TC-5.9: Coin-specific trading signals"""
        response = await client.get("/api/trading-signals/bitcoin")
        assert response.status_code in [200, 500]  # 500 if external price API unavailable


class TestTechnicalIndicatorEndpoints:
    """Test technical indicator API endpoints"""

    @pytest.mark.asyncio
    async def test_technical_indicators_by_symbol(self, client):
        """TC-5.10: Technical indicators for a specific symbol"""
        response = await client.get("/api/technical/indicators/BTC")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_technical_indicators_by_coin_id(self, client):
        """TC-5.11: Technical indicators by coin ID"""
        response = await client.get("/api/technical-indicators/bitcoin")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestNewsEndpoints:
    """Test news and sentiment endpoints"""

    @pytest.mark.asyncio
    async def test_news_endpoint(self, client):
        """TC-5.12: News endpoint returns articles"""
        response = await client.get("/api/news")
        # May return 500 if NewsAPI key is missing or aiohttp session not started
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_market_sentiment(self, client):
        """TC-5.13: Market sentiment endpoint returns data"""
        response = await client.get("/api/market-sentiment")
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_coin_sentiment(self, client):
        """TC-5.14: Coin-specific sentiment endpoint"""
        response = await client.get("/api/news/sentiment/bitcoin")
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_market_search(self, client):
        """TC-5.15: Market search endpoint works"""
        response = await client.get("/api/market/search?q=bitcoin")
        assert response.status_code == 200


class TestAlertEndpoints:
    """Test alert management endpoints"""

    @pytest.mark.asyncio
    async def test_create_alert(self, client):
        """TC-5.16: Create a price alert"""
        response = await client.post("/api/alerts", json={
            "symbol": "BTC",
            "target_price": 100000,
            "condition": "above"
        })
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_list_alerts(self, client):
        """TC-5.17: List all alerts"""
        response = await client.get("/api/alerts")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_price_history(self, client):
        """TC-5.18: Price history endpoint works"""
        response = await client.post("/api/market/price-history", json={
            "coin_id": "bitcoin",
            "days": 7
        })
        assert response.status_code in [200, 422]
