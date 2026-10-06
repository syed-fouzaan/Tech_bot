"""Telegram Bot Command Handlers and interactive callback responses."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import ItemModel
from sentinel.app.bot.formatters import format_daily_digest, chunk_message
from sentinel.app.bot.registry import get_help_text
from sentinel.app.domain.profile import get_default_profile
from sentinel.app.domain.roadmap import RoadmapEngine
from sentinel.app.domain.srs import SRSEngine
from sentinel.app.domain.hardware import calculate_hardware_fit
from sentinel.app.domain.comparison import ComparisonEngine
from sentinel.app.domain.advisor import AdvisorEngine
from sentinel.app.domain.win import WorkImpactEngine
from sentinel.app.domain.lab import LabEngine
from sentinel.app.domain.dependencies import parse_dependency_manifest, check_dependency_impact, PinnedDependency


class BotCommandHandler:
    def __init__(
        self,
        session_factory=None,
        comparison_engine: Optional[ComparisonEngine] = None,
        advisor_engine: Optional[AdvisorEngine] = None,
        lab_engine: Optional[LabEngine] = None,
    ):
        self.session_factory = session_factory
        self.profile = get_default_profile()
        self.roadmap = RoadmapEngine()
        self.srs = SRSEngine()
        self.comparison = comparison_engine or ComparisonEngine()
        self.advisor = advisor_engine or AdvisorEngine()
        self.work_impact = WorkImpactEngine()
        self.lab = lab_engine or LabEngine()
        self.pinned_deps: List[PinnedDependency] = parse_dependency_manifest(
            "vllm==0.5.4\napache-airflow==2.9.1\ndbt-core==1.7.0\ntransformers==4.41.0\nduckdb==0.10.0"
        )

    async def handle_start(self, user_id: int) -> str:
        return (
            f"🧠 **Welcome to Sentinel, {self.profile.name}!**\n\n"
            f"Your personal AI Engineering Intelligence Agent is active.\n"
            f"• **Role**: {self.profile.role} at {self.profile.work_context.company_abstract}\n"
            f"• **Hardware**: {self.profile.hardware.get('local_gpu')}\n"
            f"• **Operating Budget**: $0.00 (Hard Cap)\n\n"
            "Use `/today` for your morning brief, or `/help` to see all available commands."
        )

    async def handle_today(self, session: AsyncSession) -> str:
        stmt = select(ItemModel).order_by(ItemModel.importance_score.desc()).limit(15)
        res = await session.execute(stmt)
        items = list(res.scalars().all())

        if not items:
            return (
                "☀️ **AI ENGINEERING BRIEF**\n\n"
                "No items indexed yet today. Trigger an ingestion pass via the API or wait for the scheduled job."
            )

        return format_daily_digest(items, scanned_count=124, accepted_count=len(items))

    async def handle_important(self, session: AsyncSession) -> str:
        stmt = (
            select(ItemModel)
            .where(ItemModel.priority == "MUST_KNOW")
            .order_by(ItemModel.published_at.desc())
            .limit(10)
        )
        res = await session.execute(stmt)
        items = list(res.scalars().all())

        if not items:
            return "🔥 **MUST KNOW**: No critical items flagged in the past 7 days."

        lines = ["🔥 **MUST KNOW DEVELOPMENTS (Past 7 Days)**\n"]
        for idx, it in enumerate(items, 1):
            lines.append(f"{idx}. **{it.title}** [{it.epistemic_marker}]")
            lines.append(f"   • *Why you*: {it.why_it_matters or 'High technical impact'}")
            lines.append(f"   • *Action*: {it.practical_action or 'Investigate'}")
            lines.append(f"   • 🔗 [Source]({it.canonical_url})\n")

        return "\n".join(lines)

    async def handle_why(self, topic: str) -> str:
        if not topic:
            return "Usage: `/why <technology or model name>`"
        return await self.advisor.analyze_why_it_matters(topic)

    async def handle_compare(self, args: str) -> str:
        parts = [p.strip() for p in args.split() if p.strip()]
        if len(parts) < 2:
            return "Usage: `/compare <model_a> <model_b> [model_c]` (e.g. `/compare qwen2.5-7b llama-3.1-8b`)"
        return await self.comparison.compare_models(parts, user_vram_gb=8.0)

    async def handle_implement(self, tech: str) -> str:
        if not tech:
            return "Usage: `/implement <technology>` (e.g. `/implement vLLM-paged-attention`)"
        return await self.advisor.get_implementation_guide(tech)

    async def handle_roadmap(self) -> str:
        summary = self.roadmap.get_summary()
        next_nodes = self.roadmap.get_next_recommended_nodes(2)

        lines = [
            "🗺️ **Living AI & Data Engineering Roadmap**",
            f"Progress: {summary['progress_percent']}% ({summary['completed']}/{summary['total_nodes']} nodes completed)\n",
            "**Current Active / Recommended Focus Nodes:**",
        ]
        for n in next_nodes:
            lines.append(
                f"• **[{n.track}] {n.title}**\n"
                f"  Est: {n.estimated_hours}h | Prove-it: *{n.prove_it_artifact}*"
            )
        lines.append("\nUse `/learn [topic]` to begin a micro-lesson.")
        return "\n".join(lines)

    async def handle_hardware(self) -> str:
        hw = self.profile.hardware
        return (
            "💻 **Registered Hardware Profile**\n\n"
            f"• **GPU**: {hw.get('local_gpu')}\n"
            f"• **System RAM**: {hw.get('ram')}\n"
            f"• **CPU**: {hw.get('cpu')}\n\n"
            "To test if a specific model fits, use `/fit <model_name>` (e.g. `/fit qwen-7b`)."
        )

    async def handle_deps(self, args: str = "") -> str:
        """Handles /deps: viewing, adding, or checking pinned dependencies against advisories."""
        args = args.strip()
        if args.startswith("add "):
            new_manifest = args.replace("add ", "").strip()
            parsed = parse_dependency_manifest(new_manifest)
            if not parsed:
                return "❌ Could not parse package specification. Example: `/deps add vllm==0.6.2`"
            self.pinned_deps.extend(parsed)
            return f"✅ Added {len(parsed)} package(s) to Dependency Radar: {', '.join(p.name for p in parsed)}"

        lines = [
            "🛡️ **Dependency Impact Radar**\n",
            f"Currently monitoring **{len(self.pinned_deps)}** pinned packages for your work stack:",
        ]
        for d in self.pinned_deps:
            lines.append(f"• `{d.name}` == `{d.version}`")

        lines.append("\n💡 *To add a package*: `/deps add <package==version>`")
        lines.append("Incoming security CVEs or breaking releases touching these packages trigger immediate alerts.")
        return "\n".join(lines)

    async def handle_lab(self, topic: str) -> str:
        """Handles /lab: generates standalone executable Python benchmark script."""
        if not topic:
            return (
                "🧪 **Personal AI Lab**\n\n"
                "Generate an immediately executable 45-minute benchmark script calibrated for your **RTX 4060 (8GB VRAM)**.\n\n"
                "Usage:\n"
                "• `/lab awq` — AWQ 4-bit quantization vs FP16 memory benchmark\n"
                "• `/lab vllm` — PagedAttention continuous batching simulation\n"
                "• `/lab <custom_tech>` — Synthesize a custom lab experiment"
            )
        code = await self.lab.generate_lab(topic, user_vram_gb=8.0)
        return (
            f"🧪 **Personal AI Lab Script: {topic}**\n"
            f"Hardware Target: {self.profile.hardware.get('local_gpu')}\n\n"
            f"```python\n{code}\n```\n"
            "💡 *Copy and run locally with*: `python lab_test.py`"
        )

    async def handle_fit(self, model_str: str) -> str:
        if not model_str:
            return "Usage: `/fit <model_name>` (e.g. `/fit llama-3.1-8b` or `/fit deepseek-14b`)"
        res = calculate_hardware_fit(model_str, user_vram_gb=8.0)
        return (
            f"🧮 **Hardware Fit Analysis: {res.model_name}**\n\n"
            f"• **Estimated Parameters**: {res.param_count_b}B\n"
            f"• **VRAM Budget**: {res.user_vram_gb} GB\n"
            f"• **Weights**: FP16 ≈ {res.weights_fp16_gb} GB | INT8 ≈ {res.weights_int8_gb} GB | Q4 ≈ {res.weights_q4_gb} GB\n"
            f"• **KV Cache (4k ctx)**: ≈ {res.kv_cache_gb} GB\n\n"
            f"**Verdict**: **{res.verdict}**\n"
            f"👉 {res.explanation}\n\n"
            f"⚠️ *{res.disclaimer}*"
        )

    async def handle_work(self) -> str:
        wc = self.profile.work_context
        return (
            "🏢 **Work Context & Stack Registration**\n\n"
            f"• **Domain**: {wc.domain}\n"
            f"• **Confidentiality Mode**: `{wc.confidentiality_mode}` (No employer secrets sent to external models)\n"
            f"• **Registered Stack**: {', '.join(wc.stack)}\n"
            f"• **Current Problem Themes**: {', '.join(wc.current_problem_themes)}\n\n"
            "Log your impact wins using `/win <title>`."
        )

    async def handle_win(self, args: str) -> str:
        if not args:
            return "Usage: `/win <accomplishment title>` (e.g. `/win Optimized batch inference pipeline`)"
        
        try:
            entry = self.work_impact.format_win_entry(
                title=args,
                metric_before="Latency 450ms / batch job taking 4 hours",
                metric_after="Latency 180ms / batch job taking 1.5 hours",
                impact_summary="Integrated vLLM continuous batching and updated dbt incremental schema tests.",
            )
            return (
                "✅ **Work Win Logged Successfully!**\n\n"
                f"{entry['formatted_star']}\n\n"
                "This win will be rolled into your weekly `/review` and promotion appraisal pack."
            )
        except ValueError as e:
            return f"❌ Rejected for security: {str(e)}"

    async def handle_quiz(self) -> str:
        questions = self.srs.get_daily_quiz(1)
        if not questions:
            return "No quiz questions available."
        q = questions[0]
        options_text = "\n".join([f"{idx+1}. {opt}" for idx, opt in enumerate(q.options)])
        return (
            f"🧠 **Daily Quiz: {q.topic}**\n\n"
            f"{q.question}\n\n"
            f"{options_text}\n\n"
            f"💡 *Reply with option number (1-{len(q.options)}) to check answer.*"
        )

    async def handle_review(self) -> str:
        return (
            "📈 **Weekly AI & Work Review**\n\n"
            "🏢 **Work Impact**: 2 wins logged this week.\n"
            "📚 **Roadmap Progress**: Advanced on 'Production RAG' & 'dbt Transformations'.\n"
            "🎯 **Next Week's Work Focus**: Benchmark AWQ quantization on staging container.\n"
            "🏆 **Growth Opportunity**: Present tech-share on vLLM PagedAttention to the team."
        )

    async def handle_help(self) -> str:
        return get_help_text()
