"""Tests for security guards: secret detection, PII sanitization, and SSRF filtering."""

import pytest
from sentinel.app.security import scan_for_secrets, redact_secrets, is_safe_url


def test_scan_for_secrets_detects_credentials():
    # OpenAI key pattern
    is_safe, detected = scan_for_secrets("Here is my key: sk-abcdef1234567890abcdef1234567890")
    assert not is_safe
    assert "OpenAI/API Key" in detected

    # AWS Key pattern
    is_safe, detected = scan_for_secrets("AWS key is AKIAIOSFODNN7EXAMPLE")
    assert not is_safe
    assert "AWS Access Key" in detected

    # Postgres connection string
    is_safe, detected = scan_for_secrets("connect to postgres://user:secretpass@db.example.com/production")
    assert not is_safe
    assert "Database Connection String" in detected


def test_scan_for_secrets_clean_text():
    is_safe, detected = scan_for_secrets("Today vLLM released a new KV cache optimization with 35% memory reduction.")
    assert is_safe
    assert len(detected) == 0


def test_redact_secrets():
    raw = "My test token is ghp_1234567890abcdef1234567890abcdef"
    redacted = redact_secrets(raw)
    assert "ghp_" not in redacted
    assert "[REDACTED GitHub Token]" in redacted


def test_ssrf_protection_blocks_internal_and_metadata():
    # Loopback
    assert not is_safe_url("http://127.0.0.1:8000/internal")
    assert not is_safe_url("http://localhost:8080")

    # Private IP classes
    assert not is_safe_url("http://10.0.1.5/admin")
    assert not is_safe_url("http://192.168.1.1/router")
    assert not is_safe_url("http://172.16.0.2/api")

    # Cloud metadata endpoint
    assert not is_safe_url("http://169.254.169.254/latest/meta-data/")

    # Non-http scheme
    assert not is_safe_url("file:///etc/passwd")
    assert not is_safe_url("gopher://bad.com")

    # Safe external URLs
    assert is_safe_url("https://huggingface.co/models")
    assert is_safe_url("https://arxiv.org/abs/2401.00001")
