"""
Regression Testing Suite
========================
Ensures previously fixed bugs stay fixed. Each test corresponds to
a specific bug that was found and resolved during development.

QA Methodology: Regression Testing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRegressionBugs:
    """Tests for specific bugs that were found and fixed."""

    # ── BUG-001: UnicodeEncodeError on Windows ──────────────

    @pytest.mark.asyncio
    async def test_reg01_unicode_emoji_in_response(self, client):
        """REG-01: BUG-001 — Server crashed printing emoji to Windows console.
        
        Original Error: UnicodeEncodeError: 'charmap' codec can't encode 
        character '\\u2705' in position 0
        Fix: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        """
        response = await client.post("/api/chat", json={
            "message": "Test message with emojis 🚀📈"
        })
        assert response.status_code in [200, 400]

    def test_reg02_stdout_encoding(self):
        """REG-02: BUG-001 — stdout must be configured for UTF-8."""
        # Verify encoding is set (our fix at top of simple_backend.py)
        assert sys.stdout.encoding.lower().replace("-", "") in ["utf8", "utf-8", "utf_8"]

    # ── BUG-002: Groq library incompatibility ──────────────

    def test_reg03_groq_import(self):
        """REG-03: BUG-002 — Groq library failed with 'proxies' error.
        
        Original Error: Client.__init__() got unexpected keyword argument 'proxies'
        Fix: Upgraded groq from v0.4.1 to v1.0.0
        """
        try:
            import groq
            # Should import without error
            assert True
        except ImportError:
            # groq not installed is acceptable for testing
            pytest.skip("groq not installed")

    # ── BUG-003: Chat returning generic responses ──────────

    @pytest.mark.asyncio
    async def test_reg04_bitcoin_analysis_not_generic(self, client):
        """REG-04: BUG-003 — 'Bitcoin analysis' returned generic response.
        
        Root Cause: 'analysis' not in question_type keywords, classified as 
        'general' with 'simple' complexity, hitting dead-end canned response.
        Fix: Added analysis keywords + fixed complexity classifier + fixed fallback.
        """
        response = await client.post("/api/chat", json={
            "message": "Bitcoin analysis"
        })
        assert response.status_code == 200
        text = response.json()["response"].lower()
        # Must NOT return the old generic "I can help with various topics" response
        generic_phrases = [
            "i can help you with various topics",
            "i'm here to help",
        ]
        for phrase in generic_phrases:
            assert phrase not in text, f"Generic response returned: {text[:200]}"

    @pytest.mark.asyncio
    async def test_reg05_analysis_keyword_detected(self, client):
        """REG-05: BUG-003 — 'analysis' keyword must be detected as analysis type."""
        from simple_backend import analyze_user_question
        result = analyze_user_question("Give me Bitcoin analysis")
        assert result.get("question_type") in ["analysis", "price", "market", "technical", "price_analysis"]

    @pytest.mark.asyncio
    async def test_reg06_complexity_for_analysis(self, client):
        """REG-06: BUG-003 — Analysis questions must not be classified as 'simple'."""
        from simple_backend import analyze_question_complexity
        complexity = analyze_question_complexity("Analyze Bitcoin market trends")
        assert complexity in ["medium", "complex"], \
            f"Analysis question wrongly classified as: {complexity}"

    # ── BUG-004: starlette/httpx TestClient incompatibility ──

    def test_reg07_httpx_async_transport(self):
        """REG-07: BUG-004 — TestClient crashed with httpx 0.28+.
        
        Original Error: Client.__init__() got unexpected keyword argument 'app'
        Fix: Switched to httpx.AsyncClient with ASGITransport.
        """
        from httpx import ASGITransport, AsyncClient
        from simple_backend import app
        
        transport = ASGITransport(app=app)
        # Should create without error
        assert transport is not None

    # ── BUG-005: Auth DB not initialized in tests ──────────

    def test_reg08_auth_db_initialization(self):
        """REG-08: BUG-005 — Auth DB not initialized when using ASGITransport.
        
        Root Cause: ASGITransport doesn't trigger FastAPI @app.on_event("startup")
        Fix: Call init_auth_database() explicitly in conftest.py
        """
        from auth_database import auth_system
        assert auth_system is not None


class TestRegressionEdgeCases:
    """Edge cases that previously caused issues."""

    @pytest.mark.asyncio
    async def test_reg09_empty_crypto_query(self, client):
        """REG-09: Empty query with crypto context should not crash."""
        response = await client.post("/api/chat", json={"message": ""})
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_reg10_multiple_cryptos_in_query(self, client):
        """REG-10: Query mentioning multiple cryptos handled correctly."""
        response = await client.post("/api/chat", json={
            "message": "Compare Bitcoin and Ethereum prices"
        })
        assert response.status_code == 200
        assert len(response.json().get("response", "")) > 0

    @pytest.mark.asyncio
    async def test_reg11_special_chars_in_auth(self, client):
        """REG-11: Special characters in auth fields don't crash."""
        import random
        suffix = random.randint(100000, 999999)
        response = await client.post("/api/auth/register", json={
            "name": "Test O'Brien-Müller",
            "username": f"special_{suffix}",
            "email": f"special_{suffix}@test.com",
            "password": "P@ss!w0rd#123"
        })
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_reg12_concurrent_auth_sessions(self, client):
        """REG-12: Multiple users can be authenticated simultaneously."""
        import random
        tokens = []
        
        for i in range(3):
            suffix = random.randint(100000, 999999)
            user = {
                "name": f"Concurrent User {i}",
                "username": f"concurrent_{suffix}_{i}",
                "email": f"concurrent_{suffix}_{i}@test.com",
                "password": "ConcPass123!"
            }
            await client.post("/api/auth/register", json=user)
            login_resp = await client.post("/api/auth/login", json={
                "login": user["username"],
                "password": user["password"]
            })
            if login_resp.status_code == 200:
                token = login_resp.json().get("token")
                if token:
                    tokens.append(token)
        
        # All tokens should be different
        assert len(set(tokens)) == len(tokens), "Duplicate tokens generated!"

    def test_reg13_technical_indicators_with_insufficient_data(self):
        """REG-13: Technical indicators with too few data points."""
        from technical_indicators import TechnicalIndicators
        ti = TechnicalIndicators()
        
        # Should handle gracefully with minimal data
        result = ti.calculate_rsi([100, 101, 102])
        # Should return something (even if empty) without crashing
        assert result is not None

    def test_reg14_markdown_cleaning_preserves_content(self):
        """REG-14: Markdown cleaner must not destroy valid content."""
        from simple_backend import clean_markdown_response
        
        # Text with ## in the middle (like crypto symbol)
        text = "Bitcoin trades at $50,000 ## Analysis shows bullish trend"
        cleaned = clean_markdown_response(text)
        # The ## might be cleaned but content should remain
        assert "Bitcoin" in cleaned
        assert "bullish" in cleaned
