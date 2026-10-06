"""Dependency Radar domain engine: parses manifests and checks version alerts."""

import re
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field


class PinnedDependency(BaseModel):
    name: str
    version: str
    raw_spec: str


class DependencyAlert(BaseModel):
    package_name: str
    current_version: str
    latest_version: str
    severity: str  # CRITICAL | WARNING | INFO
    message: str
    advisory_url: Optional[str] = None


def parse_dependency_manifest(manifest_text: str) -> List[PinnedDependency]:
    """
    Parses requirements.txt or pyproject.toml style lines.
    Handles lines like: vllm==0.5.4, apache-airflow>=2.9.0, dbt-core~=1.7.0
    """
    results: List[PinnedDependency] = []
    lines = manifest_text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue

        # Match package name and version operator
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([=><~^!]+)\s*([0-9a-zA-Z_\-\.]+)", line)
        if match:
            pkg_name = match.group(1).lower().replace("_", "-")
            version = match.group(3)
            results.append(PinnedDependency(name=pkg_name, version=version, raw_spec=line))
        else:
            # Simple package name without version
            pkg_name = re.match(r"^([a-zA-Z0-9_\-\.]+)", line)
            if pkg_name:
                results.append(PinnedDependency(
                    name=pkg_name.group(1).lower().replace("_", "-"),
                    version="latest",
                    raw_spec=line,
                ))

    return results


def check_dependency_impact(
    pinned: List[PinnedDependency],
    incoming_item_title: str,
    incoming_content: str,
) -> List[DependencyAlert]:
    """
    Correlates an ingested release or security advisory against pinned dependencies.
    """
    alerts: List[DependencyAlert] = []
    full_text = f"{incoming_item_title} {incoming_content}".lower()

    for dep in pinned:
        # Check if package is mentioned (support hyphen, underscore, and space variations)
        variants = {
            dep.name,
            dep.name.replace("-", " "),
            dep.name.replace("-", "_"),
        }
        # Also match the root name if multi-part (e.g. 'airflow' for 'apache-airflow')
        if "-" in dep.name:
            variants.add(dep.name.split("-")[-1])

        matched = any(re.search(rf"\b{re.escape(v)}\b", full_text) for v in variants)
        if matched:
            is_cve = "cve" in full_text or "vulnerability" in full_text or "security" in full_text
            is_breaking = "breaking" in full_text or "deprecat" in full_text or "removed" in full_text

            severity = "CRITICAL" if is_cve else ("WARNING" if is_breaking else "INFO")
            
            # Extract possible version from title
            v_match = re.search(r"v?(\d+\.\d+(?:\.\d+)?)", incoming_item_title)
            latest_v = v_match.group(1) if v_match else "new release"

            alert_msg = f"{dep.name} update ({latest_v}) touches your pinned version ({dep.version})."
            if is_cve:
                alert_msg += " 🚨 Security/CVE vulnerability reported."
            elif is_breaking:
                alert_msg += " ⚠️ Breaking changes or deprecations noted."

            alerts.append(
                DependencyAlert(
                    package_name=dep.name,
                    current_version=dep.version,
                    latest_version=latest_v,
                    severity=severity,
                    message=alert_msg,
                )
            )

    return alerts
