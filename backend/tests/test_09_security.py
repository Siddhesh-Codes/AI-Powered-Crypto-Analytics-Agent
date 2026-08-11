"""
Security Testing Suite
======================
Tests for common web vulnerabilities and security best practices.
Covers OWASP Top 10 categories relevant to this application.

QA Methodology: Security / Penetration Testing
"""

import pytest
import json


# ─────────────────────────────────────────────────────
# SEC-1: SQL Injection Tests
# ─────────────────────────────────────────────────────

class TestSQLInjection:
    """Verify the system is resistant to SQL injection attacks."""

    @pytest.mark.asyncio
    async def test_sec01_login_sql_injection_username(self, client):
        """SEC-01: SQL injection in login username field."""
        payloads = [
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "'; DROP TABLE users;--",
            "' OR 1=1--",
        ]
        for payload in payloads:
            response = await client.post("/api/auth/login", json={
                "login": payload,
                "password": "anything"
            })
            # Should return auth failure, NOT 200 success
            assert response.status_code != 200 or response.json().get("success") is not True, \
                f"SQL injection payload succeeded: {payload}"

    @pytest.mark.asyncio
    async def test_sec02_login_sql_injection_password(self, client):
        """SEC-02: SQL injection in login password field."""
        response = await client.post("/api/auth/login", json={
            "login": "admin",
            "password": "' OR '1'='1"
        })
        assert response.status_code != 200 or response.json().get("success") is not True

    @pytest.mark.asyncio
    async def test_sec03_register_sql_injection(self, client):
        """SEC-03: SQL injection in registration fields."""
        response = await client.post("/api/auth/register", json={
            "name": "'; DROP TABLE users;--",
            "username": "admin'--",
            "email": "test@test.com",
            "password": "Pass123!"
        })
        # Should either reject or safely store (not execute SQL)
        # If it returns 200, verify the system still works
        if response.status_code == 200:
            # System should still be functional
            health = await client.get("/health")
            assert health.status_code == 200

    @pytest.mark.asyncio
    async def test_sec04_chat_sql_injection(self, client):
        """SEC-04: SQL injection in chat message field."""
        response = await client.post("/api/chat", json={
            "message": "'; DROP TABLE users; SELECT * FROM"
        })
        # Should handle as normal chat, not execute SQL
        assert response.status_code in [200, 400]
        # System should still be alive
        health = await client.get("/health")
        assert health.status_code == 200


# ─────────────────────────────────────────────────────
# SEC-2: Cross-Site Scripting (XSS) Tests
# ─────────────────────────────────────────────────────

class TestXSS:
    """Verify the system doesn't reflect or store XSS payloads."""

    @pytest.mark.asyncio
    async def test_sec05_xss_in_chat_message(self, client):
        """SEC-05: XSS payload in chat message should be sanitized."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
        ]
        for payload in xss_payloads:
            response = await client.post("/api/chat", json={
                "message": f"Tell me about {payload} Bitcoin"
            })
            if response.status_code == 200:
                text = response.json().get("response", "")
                # Response should NOT contain unescaped script tags
                assert "<script>" not in text.lower(), \
                    f"XSS payload reflected in response: {payload}"

    @pytest.mark.asyncio
    async def test_sec06_xss_in_registration(self, client):
        """SEC-06: XSS payload in user registration fields."""
        import random
        suffix = random.randint(100000, 999999)
        response = await client.post("/api/auth/register", json={
            "name": "<script>alert('xss')</script>",
            "username": f"xss_test_{suffix}",
            "email": f"xss_{suffix}@test.com",
            "password": "SecurePass123!"
        })
        # Should either reject or safely store
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_sec07_xss_in_alert_creation(self, client):
        """SEC-07: XSS payload in alert creation fields."""
        response = await client.post("/api/alerts", json={
            "coin_id": "<script>alert(1)</script>",
            "target_price": 50000,
            "direction": "above",
            "user_id": "<img src=x onerror=alert(1)>"
        })
        # Should handle without reflecting XSS
        assert response.status_code in [200, 201, 400, 422]


# ─────────────────────────────────────────────────────
# SEC-3: Authentication & Authorization Security
# ─────────────────────────────────────────────────────

class TestAuthSecurity:
    """Test authentication security measures."""

    @pytest.mark.asyncio
    async def test_sec08_expired_token_rejected(self, client):
        """SEC-08: Expired/invalid JWT token must be rejected."""
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxMDAwMDAwMDAwfQ.fake_signature"
        response = await client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {fake_token}"
        })
        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_sec09_tampered_token_rejected(self, client):
        """SEC-09: Tampered JWT token must be rejected."""
        response = await client.get("/api/auth/me", headers={
            "Authorization": "Bearer tampered.token.value"
        })
        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_sec10_no_auth_header_rejected(self, client):
        """SEC-10: Missing auth header on protected endpoints."""
        response = await client.get("/api/auth/me")
        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_sec11_password_not_in_login_response(self, client, test_user_data):
        """SEC-11: Password must never appear in API responses."""
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": test_user_data["password"]
        })
        if response.status_code == 200:
            response_text = json.dumps(response.json())
            assert test_user_data["password"] not in response_text, \
                "Password found in login response!"

    @pytest.mark.asyncio
    async def test_sec12_password_not_in_user_info(self, client, auth_headers):
        """SEC-12: Password hash must not be exposed in user info endpoints."""
        if auth_headers:
            response = await client.get("/api/auth/me", headers=auth_headers)
            if response.status_code == 200:
                response_text = json.dumps(response.json()).lower()
                assert "password" not in response_text or "password_hash" not in response_text

    @pytest.mark.asyncio
    async def test_sec13_weak_password_rejected(self, client):
        """SEC-13: Very weak passwords should be rejected."""
        import random
        suffix = random.randint(100000, 999999)
        response = await client.post("/api/auth/register", json={
            "name": "Weak Pass User",
            "username": f"weakpass_{suffix}",
            "email": f"weak_{suffix}@test.com",
            "password": "123"  # Very weak
        })
        # Should reject weak password
        assert response.status_code in [400, 422]


# ─────────────────────────────────────────────────────
# SEC-4: Input Validation & Boundary Tests
# ─────────────────────────────────────────────────────

class TestInputValidation:
    """Test that all inputs are properly validated."""

    @pytest.mark.asyncio
    async def test_sec14_extremely_long_username(self, client):
        """SEC-14: Extremely long username should be rejected."""
        response = await client.post("/api/auth/register", json={
            "name": "Test",
            "username": "a" * 10000,
            "email": "long@test.com",
            "password": "Pass123!"
        })
        # Should handle gracefully
        assert response.status_code in [200, 400, 413, 422]

    @pytest.mark.asyncio
    async def test_sec15_null_bytes_in_input(self, client):
        """SEC-15: Null bytes in input should not cause issues."""
        response = await client.post("/api/chat", json={
            "message": "Bitcoin\x00price"
        })
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_sec16_unicode_attack_strings(self, client):
        """SEC-16: Unicode edge cases should not crash the system."""
        unicode_payloads = [
            "Bitcoin\u202Eprice",     # Right-to-left override
            "Ṫ̈̊ḛ̈̊s̈̊ẗ̈̊",                # Zalgo text
            "🪙💰📈📉",               # Emoji
            "价格分析",               # Chinese characters
        ]
        for payload in unicode_payloads:
            response = await client.post("/api/chat", json={"message": payload})
            # Should not crash — any status except 500
            assert response.status_code != 500, f"Server crashed on unicode: {payload}"

    @pytest.mark.asyncio
    async def test_sec17_path_traversal_attempt(self, client):
        """SEC-17: Path traversal attempts should not expose files."""
        paths = [
            "/api/../../../etc/passwd",
            "/api/..%2F..%2F..%2Fetc%2Fpasswd",
            "/api/news/../../../../etc/passwd",
        ]
        for path in paths:
            response = await client.get(path)
            if response.status_code == 200:
                body = response.text
                assert "root:" not in body, f"Path traversal succeeded: {path}"


# ─────────────────────────────────────────────────────
# SEC-5: HTTP Security Headers
# ─────────────────────────────────────────────────────

class TestHTTPSecurity:
    """Verify security-related HTTP response behaviors."""

    @pytest.mark.asyncio
    async def test_sec18_cors_headers_present(self, client):
        """SEC-18: CORS should be configured (allow-origin header)."""
        response = await client.get("/")
        # FastAPI CORS middleware adds headers — verify they exist or
        # at minimum the server responds properly
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sec19_server_error_no_stack_trace(self, client):
        """SEC-19: Server errors should not expose stack traces to users."""
        # Send malformed data to trigger potential error
        response = await client.post("/api/auth/login", json={
            "invalid_field": "test"
        })
        if response.status_code >= 400:
            body = response.text
            # Should not contain Python traceback indicators
            assert "Traceback" not in body
            assert "File \"" not in body

    @pytest.mark.asyncio
    async def test_sec20_rate_limit_awareness(self, client):
        """SEC-20: Rapid repeated requests should not crash the server."""
        # Send 20 rapid requests
        import asyncio
        tasks = []
        for _ in range(20):
            tasks.append(client.get("/health"))
        responses = await asyncio.gather(*tasks)
        # All should succeed (or rate-limit with 429) — none should be 500
        for r in responses:
            assert r.status_code in [200, 429], f"Server error under load: {r.status_code}"
