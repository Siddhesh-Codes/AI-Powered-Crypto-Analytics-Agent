"""
Test Configuration and Fixtures
Shared fixtures for all backend tests

Uses httpx.AsyncClient with ASGITransport for httpx 0.28+ compatibility.
All API tests must be async (pytest-asyncio handles this automatically).
"""

import pytest
import sys
import os
import asyncio

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from httpx import ASGITransport, AsyncClient
from simple_backend import app
from auth_database import init_auth_database, auth_system


# Initialize auth database for tests (since ASGITransport doesn't trigger startup events)
init_auth_database()


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create an httpx AsyncClient with ASGITransport for API testing"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_prices():
    """Sample price data for technical indicator tests"""
    return [
        100, 102, 101, 105, 107, 106, 110, 108, 112, 115,
        113, 117, 120, 118, 122, 125, 123, 127, 130, 128,
        132, 135, 133, 137, 140, 138, 142, 145, 143, 147,
        150, 148, 152, 155, 153, 157, 160, 158, 162, 165
    ]


@pytest.fixture
def sample_ohlc_data():
    """Sample OHLC data for analysis tests"""
    data = []
    prices = [
        100, 102, 101, 105, 107, 106, 110, 108, 112, 115,
        113, 117, 120, 118, 122, 125, 123, 127, 130, 128,
        132, 135, 133, 137, 140, 138, 142, 145, 143, 147,
        150, 148, 152, 155, 153, 157, 160, 158, 162, 165
    ]
    for i, price in enumerate(prices):
        data.append({
            'timestamp': 1700000000000 + i * 86400000,
            'open': price - 1,
            'high': price + 2,
            'low': price - 2,
            'close': price,
            'volume': 1000000 + i * 10000
        })
    return data


@pytest.fixture
def test_user_data():
    """Test user registration data"""
    import random
    suffix = random.randint(10000, 99999)
    return {
        "name": f"Test User {suffix}",
        "username": f"testuser_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "TestPass123!"
    }


@pytest.fixture
async def auth_headers(client, test_user_data):
    """Register a user and return auth headers with JWT token"""
    # Register
    await client.post("/api/auth/register", json=test_user_data)
    
    # Login
    login_response = await client.post("/api/auth/login", json={
        "login": test_user_data["username"],
        "password": test_user_data["password"]
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        if token:
            return {"Authorization": f"Bearer {token}"}
    
    return {}
