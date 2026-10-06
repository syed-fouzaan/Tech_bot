"""Telegram message formatters with clean HTML escaping and length chunking."""

import html
import re
from typing import List, Dict, Any
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
) -> str:
    """
    Formats the daily intelligence brief in Telegram-compliant HTML.
    """
    must_know = [it for it in items if it.priority == "MUST_KNOW"][:3]
    should_know = [it for it in items if it.priority == "SHOULD_KNOW"][:4]
    work_items = [it for it in items if "day-job" in (it.why_it_matters or "").lower()][:3]
    growth_items = [it for it in items if it.priority == "LEARN"][:2]

    lines = [
        "☀️ <b>AI ENGINEERING BRIEF</b>",
        f"📊 <i>Scanned {scanned_count} · Meaningful {accepted_count} · For you {len(must_know) + len(should_know)}</i>\n",
    ]

    if must_know:
        lines.append("🔥 <b>MUST KNOW</b>")
        for idx, it in enumerate(must_know, 1):
            t = clean_html(it.title)
            lines.append(f"{idx}. <b>{t}</b> [{it.epistemic_marker}]")
            if it.why_it_matters:
                lines.append(f"   <i>Why you</i>: {clean_html(it.why_it_matters)}")
            if it.practical_action:
                lines.append(f"   <i>Do</i>: {clean_html(it.practical_action)}")
            lines.append(f"   🔗 <a href=\"{it.canonical_url}\">Source Link</a>\n")

    if should_know:
        lines.append("⚡ <b>SHOULD KNOW</b>")
        for idx, it in enumerate(should_know, 1):
            t = clean_html(it.title)
            lines.append(f"{idx}. <b>{t}</b> [{it.epistemic_marker}]")
            if it.why_it_matters:
                lines.append(f"   <i>Why</i>: {clean_html(it.why_it_matters)}")
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

    lines.append("⚠️ <b>BECOMING OBSOLETE</b>")
    lines.append("• Static unbatched KV-cache architectures → replaced by continuous chunked prefill.")
    lines.append("")

    lines.append("🧠 <b>TODAY'S LEARNING PRIORITY</b>")
    lines.append("• AWQ vs GPTQ Quantization internals (Roadmap Node: ai_quantization)")
    lines.append("")

    lines.append("💻 <b>PRACTICAL ACTION</b>")
    lines.append("• Run a 45-minute benchmark test comparing FP16 vs Q4 latency.")

    return "\n".join(lines)


# Backwards compatibility helper
def escape_markdown(text: str) -> str:
    return clean_html(text)
