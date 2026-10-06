"""Tests for new addons: Dependency Impact Radar, Personal AI Lab, and Web Radar Dashboard."""

import pytest
from httpx import AsyncClient, ASGITransport
from sentinel.app.main import app
from sentinel.app.domain.dependencies import parse_dependency_manifest, check_dependency_impact, PinnedDependency
from sentinel.app.domain.lab import LabEngine
from sentinel.app.bot.handlers import BotCommandHandler


def test_dependency_radar_manifest_parsing():
    manifest = """
    # Project dependencies
    vllm==0.5.4
    apache-airflow>=2.9.1
    dbt-core~=1.7.0
    transformers==4.41.0
    duckdb==0.10.0
    """
    pinned = parse_dependency_manifest(manifest)
    assert len(pinned) == 5
    names = [p.name for p in pinned]
    assert "vllm" in names
    assert "apache-airflow" in names
    assert "dbt-core" in names
    assert "transformers" in names
    assert "duckdb" in names


def test_dependency_impact_detection_alerts():
    pinned = [
        PinnedDependency(name="vllm", version="0.5.4", raw_spec="vllm==0.5.4"),
        PinnedDependency(name="apache-airflow", version="2.9.1", raw_spec="apache-airflow==2.9.1"),
    ]

    # Test security advisory detection
    cve_alerts = check_dependency_impact(
        pinned=pinned,
        incoming_item_title="vLLM v0.6.0 Released: Critical CVE-2024-9999 Fixed",
        incoming_content="Security patch addressing memory corruption vulnerability.",
    )
    assert len(cve_alerts) == 1
    assert cve_alerts[0].package_name == "vllm"
    assert cve_alerts[0].severity == "CRITICAL"
    assert "CVE" in cve_alerts[0].message

    # Test breaking change detection
    breaking_alerts = check_dependency_impact(
        pinned=pinned,
        incoming_item_title="Apache Airflow 3.0 Alpha with Breaking Architecture Changes",
        incoming_content="Deprecated older execution providers and removed legacy operators.",
    )
    assert len(breaking_alerts) == 1
    assert breaking_alerts[0].package_name == "apache-airflow"
    assert breaking_alerts[0].severity == "WARNING"


@pytest.mark.asyncio
async def test_personal_ai_lab_generation():
    lab = LabEngine()
    
    # Test pre-calibrated template for AWQ
    code_awq = await lab.generate_lab("awq", user_vram_gb=8.0)
    assert "AWQ 4-bit Quantization" in code_awq
    assert "RTX 4060 (8GB VRAM)" in code_awq
    assert "def benchmark_memory_and_latency" in code_awq

    # Test pre-calibrated template for vLLM
    code_vllm = await lab.generate_lab("vllm", user_vram_gb=8.0)
    assert "PagedAttention" in code_vllm
    assert "Continuous Batching" in code_vllm


@pytest.mark.asyncio
async def test_bot_deps_and_lab_handlers():
    handler = BotCommandHandler()
    
    # Test /deps
    deps_msg = await handler.handle_deps()
    assert "Dependency Impact Radar" in deps_msg
    assert "vllm" in deps_msg

    # Test /deps add
    add_msg = await handler.handle_deps("add torch==2.4.0")
    assert "Added 1 package(s)" in add_msg

    # Test /lab
    lab_msg = await handler.handle_lab("awq")
    assert "Personal AI Lab Script: awq" in lab_msg
    assert "```python" in lab_msg


@pytest.mark.asyncio
async def test_web_dashboard_serves_html():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/dashboard")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        html = resp.text
        assert "Sentinel AI Engineering Radar" in html
        assert "Dependency Impact Radar" in html
        assert "Living Roadmap Progress" in html
        assert "Personal AI Lab" in html
        assert "$0.00 / ₹0 HARD BUDGET" in html
