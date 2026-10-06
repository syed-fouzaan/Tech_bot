"""Security utilities: PII/Secret detection, SSRF protection, and Telegram auth guards."""

import ipaddress
import re
import urllib.parse
from typing import Tuple, List

# Compiled regex patterns for detecting secrets, tokens, credentials, connection strings
SECRET_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE), "OpenAI/API Key"),
    (re.compile(r"gh[pousr]_[a-zA-Z0-9]{20,}", re.IGNORECASE), "GitHub Token"),
    (re.compile(r"AIza[0-9A-Za-z-_]{35}", re.IGNORECASE), "Google API Key"),
    (re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "AWS Access Key"),
    (re.compile(r"bearer\s+[a-zA-Z0-9\-_\.]{20,}", re.IGNORECASE), "Bearer Token"),
    (re.compile(r"(?:postgres|postgresql|mysql|mongodb(?:\+srv)?):\/\/[^\s:]+:[^\s@]+@[^\s\/]+", re.IGNORECASE), "Database Connection String"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "Private Key"),
    (re.compile(r"password\s*[:=]\s*['\"][^'\"]{6,}['\"]", re.IGNORECASE), "Password Assignment"),
]

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / Cloud metadata (e.g. AWS 169.254.169.254)
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]


def scan_for_secrets(text: str) -> Tuple[bool, List[str]]:
    """
    Checks if text contains credentials, tokens, or connection strings.
    Returns: (is_safe: bool, detected_types: list[str])
    """
    if not text:
        return True, []
    
    detected = []
    for pattern, name in SECRET_PATTERNS:
        if pattern.search(text):
            detected.append(name)
            
    is_safe = len(detected) == 0
    return is_safe, detected


def redact_secrets(text: str) -> str:
    """Replaces detected sensitive tokens with [REDACTED]."""
    if not text:
        return text
    result = text
    for pattern, name in SECRET_PATTERNS:
        result = pattern.sub(f"[REDACTED {name}]", result)
    return result


def is_safe_url(url: str) -> bool:
    """
    SSRF guard: verifies the URL scheme is HTTP(S) and does not point to internal/private IPs.
    """
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Check against localhost string
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
            return False
            
        # If hostname is an IP, check if it's in a private network
        try:
            ip = ipaddress.ip_address(hostname)
            for net in BLOCKED_IP_NETWORKS:
                if ip in net:
                    return False
        except ValueError:
            # Hostname is a domain name, not a raw IP
            pass
            
        return True
    except Exception:
        return False
