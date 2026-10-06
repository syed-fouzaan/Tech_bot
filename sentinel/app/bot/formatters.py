"""Telegram message formatters with clean HTML escaping and length chunking."""

import html
import re
from typing import List, Dict, Any, Optional
from sentinel.app.models import ItemModel


def clean_html(text: str) -> str:
    """Escapes HTML special characters safely for Telegram."""
    if not text:
        return ""
    return html.escape(text, quote=False)


def chunk_message(text: str, max_chars: int = 4000) -> List[str]:
    """Splits long text into chunks under Telegram's 4096 character ceiling."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_len = 0

    for line in lines:
        if current_len + len(line) + 1 > max_chars:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_len = len(line)
        else:
            current_chunk.append(line)
            current_len += len(line) + 1

    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks


def format_daily_digest(
    items: List[ItemModel],
    scanned_count: int = 120,
    accepted_count: int = 24,
    declared_learning: Optional[Dict[str, str]] = None,
) -> str:
    """
    Formats the daily intelligence brief in Telegram-compliant HTML.
    Includes verified dates and dynamic declared career milestones.
    """
    must_know = [it for it in items if it.priority == "MUST_KNOW"][:3]
    should_know = [it for it in items if it.priority == "SHOULD_KNOW"][:4]
    work_items = [it for it in items if "day-job" in (it.why_it_matters or "").lower() or "production" in (it.why_it_matters or "").lower()][:3]
    growth_items = [it for it in items if it.priority == "LEARN"][:2]

    lines = [
        "☀️ <b>AI ENGINEERING BRIEF</b>",
        f"📊 <i>Scanned {scanned_count} · Meaningful {accepted_count} · For you {len(must_know) + len(should_know)}</i>\n",
    ]

    if must_know:
        lines.append("🔥 <b>MUST KNOW</b>")
        for idx, it in enumerate(must_know, 1):
            t = clean_html(it.title)
            pub_str = it.published_at.strftime("%b %d, %Y") if it.published_at else ""
            date_tag = f" <i>(📅 {pub_str})</i>" if pub_str else ""
            lines.append(f"{idx}. <b>{t}</b> [{it.epistemic_marker}]{date_tag}")
            if it.why_it_matters:
                lines.append(f"   <i>Why you</i>: {clean_html(it.why_it_matters)}")
            if it.practical_action:
                lines.append(f"   <i>Action</i>: {clean_html(it.practical_action)}")
            lines.append(f"   🔗 <a href=\"{it.canonical_url}\">Source Link</a>\n")

    if should_know:
        lines.append("⚡ <b>SHOULD KNOW</b>")
        for idx, it in enumerate(should_know, 1):
            t = clean_html(it.title)
            pub_str = it.published_at.strftime("%b %d, %Y") if it.published_at else ""
            date_tag = f" <i>(📅 {pub_str})</i>" if pub_str else ""
            lines.append(f"{idx}. <b>{t}</b> [{it.epistemic_marker}]{date_tag}")
            if it.why_it_matters:
                lines.append(f"   <i>Why</i>: {clean_html(it.why_it_matters)}")
            if it.practical_action:
                lines.append(f"   <i>Action</i>: {clean_html(it.practical_action)}")
            lines.append(f"   🔗 <a href=\"{it.canonical_url}\">Source Link</a>\n")

    if work_items:
        lines.append("🏢 <b>FOR YOUR WORK</b>")
        for it in work_items:
            lines.append(f"• <b>{clean_html(it.title)}</b>: {clean_html(it.why_it_matters or '')}")
        lines.append("")

    if growth_items:
        lines.append("🎯 <b>FOR YOUR GROWTH</b>")
        for it in growth_items:
            lines.append(f"• <b>{clean_html(it.title)}</b>: {clean_html(it.practical_action or 'Learn fundamentals')}")
        lines.append("")

    if declared_learning:
        lines.append("🧠 <b>TODAY'S LEARNING PRIORITY & CAREER GOAL</b>")
        lines.append(f"• <b>{clean_html(declared_learning.get('declared_next_topic', 'Inference Optimization'))}</b>")
        lines.append(f"  <i>Why</i>: {clean_html(declared_learning.get('why_next', 'Directly levels up your stack'))}")
        lines.append("")
        if declared_learning.get("real_world_example"):
            lines.append("💻 <b>REAL-WORLD PRODUCTION SCENARIO</b>")
            lines.append(f"• {clean_html(declared_learning['real_world_example'])}")
            lines.append("")
    else:
        lines.append("🧠 <b>TODAY'S LEARNING PRIORITY & CAREER GOAL</b>")
        lines.append("• <b>Continuous Chunked Prefill & Speculative Decoding</b>")
        lines.append("  <i>Why</i>: Crucial for reducing p99 latency in high-concurrency LLM serving.")
        lines.append("")
        lines.append("💻 <b>REAL-WORLD PRODUCTION SCENARIO</b>")
        lines.append("• Test a 1B draft model with Llama-3-8B in vLLM to cut TTFT without quality loss.")
        lines.append("")

    return "\n".join(lines)


# Backwards compatibility helper
def escape_markdown(text: str) -> str:
    return clean_html(text)
