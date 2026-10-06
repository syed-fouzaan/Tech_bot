import pytest
from httpx import AsyncClient, ASGITransport
from sentinel.app.main import app
from sentinel.app.db import init_db


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sentinel"


@pytest.mark.asyncio
async def test_ready_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["database"] is True
        assert data["budget_invariant_passed"] is True


@pytest.mark.asyncio
async def test_metrics_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_items_indexed" in data
        assert data["cost_incurred_usd"] == 0.0
