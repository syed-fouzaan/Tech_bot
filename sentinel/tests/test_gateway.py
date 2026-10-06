"""Tests for AI Gateway: $0 budget enforcement, quota ledger, circuit breaker, and failover."""

import pytest
from sentinel.app.config import Settings
from sentinel.app.providers.base import TaskType
from sentinel.app.providers.gateway import AIGateway, CircuitBreaker, QuotaLedger


def test_hard_zero_dollar_budget_violation():
    # Attempting a non-zero budget while paid providers are forbidden must fail validation
    with pytest.raises(ValueError):
        Settings(DAILY_AI_BUDGET=10.0, ALLOW_PAID_PROVIDERS=False)


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=2, recovery_time_s=10.0)
    assert cb.state == "CLOSED"
    assert cb.can_attempt()

    cb.record_failure()
    assert cb.state == "CLOSED"
    assert cb.can_attempt()

    cb.record_failure()
    assert cb.state == "OPEN"
    assert not cb.can_attempt()

    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.can_attempt()


def test_quota_ledger_rpm_limiting():
    ledger = QuotaLedger()
    pid = "test_provider"

    # Allow up to 3 calls
    for _ in range(3):
        assert ledger.can_call(pid, rpm_limit=3)
        ledger.record_call(pid)

    # 4th call must be blocked by rate limit
    assert not ledger.can_call(pid, rpm_limit=3)


@pytest.mark.asyncio
async def test_gateway_fallback_to_deterministic_mock():
    # Configure gateway with empty API keys so all external providers are unavailable
    settings = Settings(
        DAILY_AI_BUDGET=0.0,
        ALLOW_PAID_PROVIDERS=False,
        GEMINI_API_KEY="",
        GROQ_API_KEY="",
    )
    gateway = AIGateway(settings)

    # Gateway should automatically fall back to mock provider
    resp = await gateway.generate(
        prompt="Analyze vLLM v0.6 release",
        task=TaskType.TECHNICAL_ANALYSIS,
    )
    assert resp is not None
    assert resp.provider == "mock_deterministic"
    assert resp.is_fallback
    assert "Technical Breakdown" in resp.content
