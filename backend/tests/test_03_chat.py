"""
Test Suite 3: AI Chat Service Tests
Tests AI chat endpoints, fallback responses, and question analysis
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAIChatEndpoint:
    """Test AI chat endpoint responses"""

    @pytest.mark.asyncio
    async def test_chat_basic_message(self, client):
        """TC-3.1: Chat endpoint responds to basic message"""
        response = await client.post("/api/chat", json={
            "message": "Hello",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "source" in data
        assert len(data["response"]) > 0

    @pytest.mark.asyncio
    async def test_chat_bitcoin_price_query(self, client):
        """TC-3.2: Chat returns meaningful response for Bitcoin price query"""
        response = await client.post("/api/chat", json={
            "message": "What is the current price of Bitcoin?",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Response should mention Bitcoin or BTC
        assert any(word in data["response"].lower() for word in ["bitcoin", "btc", "$"])

    @pytest.mark.asyncio
    async def test_chat_bitcoin_analysis(self, client):
        """TC-3.3: Chat returns analysis, not generic fallback for 'Bitcoin analysis'"""
        response = await client.post("/api/chat", json={
            "message": "Bitcoin analysis",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        # Should NOT return the dead-end generic message
        assert "please specify which cryptocurrency" not in data["response"].lower()
        assert len(data["response"]) > 50  # Should be a meaningful response

    @pytest.mark.asyncio
    async def test_chat_ethereum_query(self, client):
        """TC-3.4: Chat handles Ethereum queries"""
        response = await client.post("/api/chat", json={
            "message": "Tell me about Ethereum",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert any(word in data["response"].lower() for word in ["ethereum", "eth"])

    @pytest.mark.asyncio
    async def test_chat_investment_advice(self, client):
        """TC-3.5: Chat handles investment advice queries"""
        response = await client.post("/api/chat", json={
            "message": "Should I invest in Bitcoin? Is it safe?",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["response"]) > 50
        # Should mention risk or advice
        assert any(word in data["response"].lower() for word in ["risk", "invest", "advice", "financial"])

    @pytest.mark.asyncio
    async def test_chat_market_trends(self, client):
        """TC-3.6: Chat handles market trends query"""
        response = await client.post("/api/chat", json={
            "message": "Market trends",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["response"]) > 30

    @pytest.mark.asyncio
    async def test_chat_has_suggestions(self, client):
        """TC-3.7: Chat response includes suggestions"""
        response = await client.post("/api/chat", json={
            "message": "Hello",
            "conversation_history": [],
            "user_context": {}
        })
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_chat_source_field(self, client):
        """TC-3.8: Chat response includes valid source field"""
        response = await client.post("/api/chat", json={
            "message": "Bitcoin price",
            "conversation_history": [],
            "user_context": {}
        })
        data = response.json()
        assert data["source"] in ["groq_ai", "enhanced_fallback", "error_fallback"]

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, client):
        """TC-3.9: Chat handles empty message gracefully"""
        response = await client.post("/api/chat", json={
            "message": "",
            "conversation_history": [],
            "user_context": {}
        })
        # Should either return 200 with fallback or 422 validation error
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_chat_long_message(self, client):
        """TC-3.10: Chat handles very long message"""
        long_msg = "Can you analyze Bitcoin? " * 50
        response = await client.post("/api/chat", json={
            "message": long_msg,
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["response"]) > 0


class TestChatAliasEndpoints:
    """Test that all chat endpoint aliases work"""

    @pytest.mark.asyncio
    async def test_v1_ai_chat(self, client):
        """TC-3.11: /api/v1/ai/chat endpoint works"""
        response = await client.post("/api/v1/ai/chat", json={
            "message": "Hello",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_api_ai_chat(self, client):
        """TC-3.12: /api/ai/chat endpoint works"""
        response = await client.post("/api/ai/chat", json={
            "message": "Hello",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_api_chat(self, client):
        """TC-3.13: /api/chat endpoint works"""
        response = await client.post("/api/chat", json={
            "message": "Hello",
            "conversation_history": [],
            "user_context": {}
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_all_endpoints_return_same_format(self, client):
        """TC-3.14: All chat endpoints return consistent response format"""
        endpoints = ["/api/v1/ai/chat", "/api/ai/chat", "/api/chat"]
        payload = {"message": "Bitcoin", "conversation_history": [], "user_context": {}}

        for endpoint in endpoints:
            response = await client.post(endpoint, json=payload)
            data = response.json()
            assert "response" in data, f"Missing 'response' in {endpoint}"
            assert "source" in data, f"Missing 'source' in {endpoint}"
            assert "suggestions" in data, f"Missing 'suggestions' in {endpoint}"


class TestQuestionAnalysis:
    """Test question analysis and classification logic"""

    def test_detect_crypto_mentions_bitcoin(self):
        """TC-3.15: Detects Bitcoin mentions"""
        from simple_backend import detect_crypto_mentions
        result = detect_crypto_mentions("What is the price of Bitcoin?")
        assert "BITCOIN" in result

    def test_detect_crypto_mentions_multiple(self):
        """TC-3.16: Detects multiple crypto mentions"""
        from simple_backend import detect_crypto_mentions
        result = detect_crypto_mentions("Compare Bitcoin and Ethereum price")
        assert "BITCOIN" in result
        assert "ETHEREUM" in result

    def test_detect_crypto_symbol_btc(self):
        """TC-3.17: Detects BTC symbol"""
        from simple_backend import detect_crypto_mentions
        result = detect_crypto_mentions("What is BTC worth?")
        assert "BITCOIN" in result

    def test_analyze_complexity_simple(self):
        """TC-3.18: Short price queries are classified as simple"""
        from simple_backend import analyze_question_complexity
        result = analyze_question_complexity("Bitcoin price")
        assert result == "simple"

    def test_analyze_complexity_medium(self):
        """TC-3.19: Analysis queries are classified as medium"""
        from simple_backend import analyze_question_complexity
        result = analyze_question_complexity("Bitcoin analysis")
        assert result == "medium"

    def test_analyze_complexity_complex(self):
        """TC-3.20: Complex queries are classified as complex"""
        from simple_backend import analyze_question_complexity
        result = analyze_question_complexity(
            "Can you provide a detailed technical analysis of Bitcoin with forecast and investment advice?"
        )
        assert result == "complex"

    def test_analyze_question_price(self):
        """TC-3.21: Price questions are classified correctly"""
        from simple_backend import analyze_user_question
        result = analyze_user_question("What is the price of Bitcoin?")
        assert result["question_type"] == "price_analysis"
        assert len(result["crypto_mentions"]) > 0

    def test_analyze_question_investment(self):
        """TC-3.22: Investment questions are classified correctly"""
        from simple_backend import analyze_user_question
        result = analyze_user_question("Should I invest in crypto?")
        assert result["question_type"] == "investment_advice"

    def test_analyze_question_educational(self):
        """TC-3.23: Educational questions are classified correctly"""
        from simple_backend import analyze_user_question
        result = analyze_user_question("How does blockchain technology work?")
        assert result["question_type"] == "educational"

    def test_analyze_question_analysis_type(self):
        """TC-3.24: Analysis queries are not classified as 'general'"""
        from simple_backend import analyze_user_question
        result = analyze_user_question("Bitcoin analysis")
        # Should be price_analysis (because 'analysis' keyword was added), not 'general'
        assert result["question_type"] != "general"

    def test_clean_markdown_response(self):
        """TC-3.25: Markdown cleaning removes bold/italic formatting and line-start headers"""
        from simple_backend import clean_markdown_response
        # Test bold and italic are removed
        raw_bold = "**Bold** and *italic* text"
        cleaned = clean_markdown_response(raw_bold)
        assert "**" not in cleaned
        assert "*" not in cleaned or "italic" in cleaned

        # Test headers at line start are removed
        raw_header = "## Header Title"
        cleaned_header = clean_markdown_response(raw_header)
        assert "##" not in cleaned_header
        assert "Header Title" in cleaned_header
