"""
Test Suite 2: Authentication System Tests
Tests user registration, login, token verification, and logout
"""

import pytest


class TestUserRegistration:
    """Test user registration flow"""

    @pytest.mark.asyncio
    async def test_register_success(self, client, test_user_data):
        """TC-2.1: Successful user registration"""
        response = await client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "created" in data["message"].lower() or "success" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client, test_user_data):
        """TC-2.2: Duplicate username registration is rejected"""
        # First registration
        await client.post("/api/auth/register", json=test_user_data)
        # Duplicate attempt
        response = await client.post("/api/auth/register", json=test_user_data)
        data = response.json()
        assert data["success"] is False
        assert "exists" in data["message"].lower() or "already" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        """TC-2.3: Short password is rejected (min 6 chars)"""
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "username": "shortpwduser",
            "email": "shortpwd@example.com",
            "password": "12345"
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_username(self, client):
        """TC-2.4: Short username is rejected (min 3 chars)"""
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "username": "ab",
            "email": "shortname@example.com",
            "password": "ValidPass123"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """TC-2.5: Invalid email format is rejected"""
        response = await client.post("/api/auth/register", json={
            "name": "Test User",
            "username": "invalidemail",
            "email": "notanemail",
            "password": "ValidPass123"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        """TC-2.6: Missing required fields returns error"""
        response = await client.post("/api/auth/register", json={
            "username": "incomplete"
        })
        assert response.status_code == 422


class TestUserLogin:
    """Test user login flow"""

    @pytest.mark.asyncio
    async def test_login_with_username(self, client, test_user_data):
        """TC-2.7: Login with valid username and password"""
        # Register first
        await client.post("/api/auth/register", json=test_user_data)
        # Login
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["token"] is not None
        assert "user" in data

    @pytest.mark.asyncio
    async def test_login_with_email(self, client, test_user_data):
        """TC-2.8: Login with email address"""
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["token"] is not None

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user_data):
        """TC-2.9: Login with wrong password is rejected"""
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": "WrongPassword123"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """TC-2.10: Login with non-existent user is rejected"""
        response = await client.post("/api/auth/login", json={
            "login": "nonexistentuser999",
            "password": "SomePassword123"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_returns_user_info(self, client, test_user_data):
        """TC-2.11: Successful login returns user profile info"""
        await client.post("/api/auth/register", json=test_user_data)
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": test_user_data["password"]
        })
        data = response.json()
        user = data.get("user", {})
        assert user.get("username") == test_user_data["username"]
        assert user.get("email") == test_user_data["email"].lower()
        assert user.get("name") == test_user_data["name"]


class TestTokenVerification:
    """Test JWT token verification"""

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, client, auth_headers):
        """TC-2.12: Valid JWT token is accepted"""
        if not auth_headers:
            pytest.skip("Auth headers not available")
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Response wraps user info: {"success": true, "user": {...}}
        assert data.get("success") is True
        user = data.get("user", data)
        assert "username" in user

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, client):
        """TC-2.13: Invalid JWT token is rejected"""
        response = await client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_no_token_provided(self, client):
        """TC-2.14: Request without token is rejected"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401


class TestLogout:
    """Test logout functionality"""

    @pytest.mark.asyncio
    async def test_logout_success(self, client, auth_headers):
        """TC-2.15: Successful logout"""
        if not auth_headers:
            pytest.skip("Auth headers not available")
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
