"""
Performance Testing Suite
=========================
Tests for response time, throughput, and system behavior under load.
Measures API response times against acceptable thresholds.

QA Methodology: Performance / Load / Stress Testing
"""

import pytest
import time
import asyncio
import statistics


# ─────────────────────────────────────────────────────
# PERF-1: Response Time Benchmarks
# ─────────────────────────────────────────────────────

class TestResponseTimeBenchmarks:
    """Verify API endpoints respond within acceptable time limits."""

    @pytest.mark.asyncio
    async def test_perf01_health_endpoint_fast(self, client):
        """PERF-01: Health endpoint should respond in < 500ms."""
        start = time.perf_counter()
        response = await client.get("/health")
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"Health endpoint too slow: {elapsed:.3f}s (max 0.5s)"

    @pytest.mark.asyncio
    async def test_perf02_root_endpoint_fast(self, client):
        """PERF-02: Root endpoint should respond in < 500ms."""
        start = time.perf_counter()
        response = await client.get("/")
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"Root endpoint too slow: {elapsed:.3f}s"

    @pytest.mark.asyncio
    async def test_perf03_auth_login_time(self, client, test_user_data):
        """PERF-03: Login should complete in < 2 seconds."""
        await client.post("/api/auth/register", json=test_user_data)
        
        start = time.perf_counter()
        response = await client.post("/api/auth/login", json={
            "login": test_user_data["username"],
            "password": test_user_data["password"]
        })
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Login too slow: {elapsed:.3f}s (max 2.0s)"

    @pytest.mark.asyncio
    async def test_perf04_chat_response_time(self, client):
        """PERF-04: Chat should respond in < 15 seconds."""
        start = time.perf_counter()
        response = await client.post("/api/chat", json={
            "message": "What is Bitcoin?"
        })
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 15.0, f"Chat too slow: {elapsed:.3f}s (max 15s)"

    @pytest.mark.asyncio
    async def test_perf05_registration_time(self, client):
        """PERF-05: User registration should complete in < 2 seconds."""
        import random
        suffix = random.randint(100000, 999999)
        
        start = time.perf_counter()
        response = await client.post("/api/auth/register", json={
            "name": f"PerfTest {suffix}",
            "username": f"perf_{suffix}",
            "email": f"perf_{suffix}@test.com",
            "password": "PerfPass123!"
        })
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Registration too slow: {elapsed:.3f}s"

    @pytest.mark.asyncio
    async def test_perf06_alerts_endpoint_time(self, client):
        """PERF-06: Alerts list should respond in < 1 second."""
        start = time.perf_counter()
        response = await client.get("/api/alerts")
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"Alerts endpoint too slow: {elapsed:.3f}s"

    @pytest.mark.asyncio
    async def test_perf07_docs_endpoint_time(self, client):
        """PERF-07: API docs should load in < 2 seconds."""
        start = time.perf_counter()
        response = await client.get("/docs")
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Docs endpoint too slow: {elapsed:.3f}s"


# ─────────────────────────────────────────────────────
# PERF-2: Load Testing
# ─────────────────────────────────────────────────────

class TestLoadHandling:
    """Test system behavior under concurrent load."""

    @pytest.mark.asyncio
    async def test_perf08_concurrent_health_checks(self, client):
        """PERF-08: 50 concurrent health checks should all succeed."""
        async def single_request():
            return await client.get("/health")
        
        tasks = [single_request() for _ in range(50)]
        responses = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 50, f"Only {success_count}/50 requests succeeded"

    @pytest.mark.asyncio
    async def test_perf09_concurrent_chat_requests(self, client):
        """PERF-09: 10 concurrent chat requests should all respond."""
        async def chat_request(msg):
            return await client.post("/api/chat", json={"message": msg})
        
        messages = [
            "Bitcoin price", "Ethereum analysis", "Market trends",
            "Crypto news", "Investment tips", "DeFi overview",
            "NFT market", "Blockchain tech", "Trading strategies",
            "Portfolio advice"
        ]
        
        tasks = [chat_request(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 8, f"Only {success_count}/10 chat requests succeeded"

    @pytest.mark.asyncio
    async def test_perf10_concurrent_auth_operations(self, client):
        """PERF-10: Multiple concurrent registrations should not conflict."""
        import random
        
        async def register_user(i):
            suffix = random.randint(1000000, 9999999)
            return await client.post("/api/auth/register", json={
                "name": f"LoadTest User {suffix}",
                "username": f"load_{suffix}_{i}",
                "email": f"load_{suffix}_{i}@test.com",
                "password": "LoadPass123!"
            })
        
        tasks = [register_user(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 8, f"Only {success_count}/10 registrations succeeded"

    @pytest.mark.asyncio
    async def test_perf11_sustained_requests(self, client):
        """PERF-11: 100 sequential requests should maintain consistent timing."""
        times = []
        for _ in range(100):
            start = time.perf_counter()
            response = await client.get("/health")
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        p95_time = sorted(times)[94]  # 95th percentile
        
        # Average should be under 200ms, P95 under 500ms
        assert avg_time < 0.2, f"Average response time too high: {avg_time:.3f}s"
        assert p95_time < 0.5, f"P95 response time too high: {p95_time:.3f}s"


# ─────────────────────────────────────────────────────
# PERF-3: Stress Testing
# ─────────────────────────────────────────────────────

class TestStressHandling:
    """Test system behavior under extreme conditions."""

    @pytest.mark.asyncio
    async def test_perf12_large_payload_handling(self, client):
        """PERF-12: Large message payload should be handled without timeout."""
        large_message = "Analyze the Bitcoin market including all indicators, trends, " * 200
        
        start = time.perf_counter()
        response = await client.post("/api/chat", json={"message": large_message})
        elapsed = time.perf_counter() - start
        
        assert response.status_code in [200, 400, 413]
        assert elapsed < 30.0, f"Large payload took too long: {elapsed:.3f}s"

    @pytest.mark.asyncio
    async def test_perf13_rapid_fire_requests(self, client):
        """PERF-13: Rapid-fire requests should not cause cascading failures."""
        results = {"200": 0, "429": 0, "other": 0}
        
        for _ in range(30):
            response = await client.get("/")
            if response.status_code == 200:
                results["200"] += 1
            elif response.status_code == 429:
                results["429"] += 1
            else:
                results["other"] += 1
        
        # At least 80% should succeed (or be rate-limited)
        acceptable = results["200"] + results["429"]
        assert acceptable >= 24, f"Too many failures under rapid fire: {results}"

    @pytest.mark.asyncio
    async def test_perf14_memory_leak_check(self, client):
        """PERF-14: Repeated operations should not degrade performance."""
        # Run 50 operations and check that later ones aren't slower
        first_half_times = []
        second_half_times = []
        
        for i in range(50):
            start = time.perf_counter()
            await client.get("/health")
            elapsed = time.perf_counter() - start
            
            if i < 25:
                first_half_times.append(elapsed)
            else:
                second_half_times.append(elapsed)
        
        avg_first = statistics.mean(first_half_times)
        avg_second = statistics.mean(second_half_times)
        
        # Second half should not be more than 3x slower than first half
        assert avg_second < avg_first * 3, \
            f"Performance degradation detected: {avg_first:.3f}s → {avg_second:.3f}s"
