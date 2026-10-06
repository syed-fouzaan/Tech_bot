"""Command Registry with descriptions, argument syntax, and access tiers."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class CommandInfo(BaseModel):
    name: str
    args: str = ""
    description: str
    tier: str = "core"  # core | advanced | admin


COMMANDS: Dict[str, CommandInfo] = {
    "start": CommandInfo(name="start", description="Initialize Sentinel and view current profile"),
    "today": CommandInfo(name="today", description="Get today's AI Engineering intelligence brief"),
    "digest": CommandInfo(name="digest", args="[date]", description="Retrieve digest for specific date"),
    "important": CommandInfo(name="important", description="View all 🔥 MUST KNOW items from past 7 days"),
    "why": CommandInfo(name="why", args="<topic>", description="10-point analysis: why should an engineer care"),
    "compare": CommandInfo(name="compare", args="<modelA> <modelB>", description="Evidence-backed side-by-side model comparison"),
    "implement": CommandInfo(name="implement", args="<technology>", description="Implementation blueprint with $0 setup path"),
    "learn": CommandInfo(name="learn", args="[topic]", description="Start or continue a roadmap micro-lesson"),
    "roadmap": CommandInfo(name="roadmap", description="View progress on AI and Data Engineering roadmap"),
    "hardware": CommandInfo(name="hardware", description="View registered GPU/VRAM hardware profile"),
    "fit": CommandInfo(name="fit", args="<model>", description="Calculate if a model fits in your VRAM"),
    "deps": CommandInfo(name="deps", args="[add|check]", description="Dependency Impact Radar: checks pinned packages for CVEs & breaking releases"),
    "lab": CommandInfo(name="lab", args="<topic>", description="Personal AI Lab: generate executable benchmark script for RTX 4060"),
    "work": CommandInfo(name="work", args="[what you worked on]", description="Log what you worked on or view registered work context"),
    "learned": CommandInfo(name="learned", args="<what you learned>", description="Log concepts/tools learned; declares what to learn next"),
    "career": CommandInfo(name="career", description="Personal Career Advisor: diagnoses skill gaps and declares your next learning milestone"),
    "interests": CommandInfo(name="interests", args="[add <topic>]", description="View or add topics and technologies you like more"),
    "win": CommandInfo(name="win", args="<title>", description="Log a measurable work achievement for appraisal/1:1"),
    "quiz": CommandInfo(name="quiz", description="Daily spaced repetition quiz on AI and Data concepts"),
    "review": CommandInfo(name="review", description="Weekly review of work wins, topics learned, and roadmaps"),
    "search": CommandInfo(name="search", args="<query>", description="Search verified knowledge store"),
    "profile": CommandInfo(name="profile", description="View and manage user profile and skill inventory"),
    "memory": CommandInfo(name="memory", args="[add <fact>|clear]", description="View, add, or clear facts stored in long-term AI memory"),
    "review_arch": CommandInfo(name="review_arch", args="<architecture/code>", description="Principal Architecture & Code Reviewer: scale failure points & drop-in refactors"),
    "roast": CommandInfo(name="roast", args="<architecture/code>", description="Brutally roast an architecture design for scale bottlenecks & compute waste"),
    "reproduce": CommandInfo(name="reproduce", args="<topic>", description="1-Click Local 'Prove-It' Script: runnable benchmark calibrated for RTX 4060"),
    "interview": CommandInfo(name="interview", args="[topic | solve <solution>]", description="Mock Staff System Design Interviewer: scenario generation & grading rubrics"),
    "brag": CommandInfo(name="brag", description="STAR Promotion & Appraisal Dossier: auto-compiles your logged wins & work into executive format"),
    "promo": CommandInfo(name="promo", description="STAR Promotion & Appraisal Dossier: auto-compiles your logged wins & work into executive format"),
    "clear": CommandInfo(name="clear", description="Reset current conversational history for a fresh chat session"),
    "help": CommandInfo(name="help", description="Show command list and quick reference guide"),
}


def get_help_text() -> str:
    lines = ["🤖 **Sentinel AI Engineering Intelligence Agent — Command Reference**\n"]
    for cmd in COMMANDS.values():
        arg_str = f" `{cmd.args}`" if cmd.args else ""
        lines.append(f"• `/{cmd.name}`{arg_str} — {cmd.description}")
    lines.append("\n🔒 *100% $0 Operating Budget Guaranteed · Evidence-First Intelligence*")
    return "\n".join(lines)
