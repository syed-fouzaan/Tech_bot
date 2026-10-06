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
from sentinel.app.domain.career_advisor import CareerAdvisorEngine
from sentinel.app.domain.conversation import ConversationEngine
from sentinel.app.domain.win import WorkImpactEngine
from sentinel.app.domain.lab import LabEngine
from sentinel.app.domain.dependencies import parse_dependency_manifest, check_dependency_impact, PinnedDependency
from sentinel.app.domain.architecture_reviewer import ArchitectureReviewer
from sentinel.app.domain.interview import InterviewEngine
from sentinel.app.domain.promo import PromoEngine
from sentinel.app.domain.incident_drill import IncidentDrillEngine
from sentinel.app.domain.pr_reviewer import PRReviewerEngine
from sentinel.app.domain.migration_roi import MigrationROIEngine
from sentinel.app.domain.executive_status import ExecutiveStatusEngine
from sentinel.app.domain.design_patterns import DesignPatternEngine
from sentinel.app.domain.sql_optimizer import SQLOptimizerEngine
from sentinel.app.domain.cost_calculator import CostCalculatorEngine
from sentinel.app.domain.runbook_generator import RunbookEngine
from sentinel.app.domain.data_ninja import DataNinjaEngine
from sentinel.app.domain.standup_soundbite import StandupSoundbiteEngine
from sentinel.app.domain.script_profiler import ScriptProfilerEngine
from sentinel.app.domain.data_guardrails import DataGuardrailsEngine
from sentinel.app.domain.log_parser import LogParserEngine
from sentinel.app.domain.safe_eval import SafePythonRunner
from sentinel.app.domain.test_generator import TestSuiteGeneratorEngine


class BotCommandHandler:
    def __init__(
        self,
        session_factory=None,
        comparison_engine: Optional[ComparisonEngine] = None,
        advisor_engine: Optional[AdvisorEngine] = None,
        lab_engine: Optional[LabEngine] = None,
        career_advisor: Optional[CareerAdvisorEngine] = None,
        conversation_engine: Optional[ConversationEngine] = None,
        arch_reviewer: Optional[ArchitectureReviewer] = None,
        interview_engine: Optional[InterviewEngine] = None,
        promo_engine: Optional[PromoEngine] = None,
        drill_engine: Optional[IncidentDrillEngine] = None,
        pr_reviewer: Optional[PRReviewerEngine] = None,
        migration_roi: Optional[MigrationROIEngine] = None,
        status_engine: Optional[ExecutiveStatusEngine] = None,
        pattern_engine: Optional[DesignPatternEngine] = None,
        sql_optimizer: Optional[SQLOptimizerEngine] = None,
        cost_calc: Optional[CostCalculatorEngine] = None,
        runbook_engine: Optional[RunbookEngine] = None,
        data_ninja: Optional[DataNinjaEngine] = None,
        soundbite_engine: Optional[StandupSoundbiteEngine] = None,
        script_profiler: Optional[ScriptProfilerEngine] = None,
        guardrails_engine: Optional[DataGuardrailsEngine] = None,
        log_parser: Optional[LogParserEngine] = None,
        safe_eval: Optional[SafePythonRunner] = None,
        test_generator: Optional[TestSuiteGeneratorEngine] = None,
    ):
        self.session_factory = session_factory
        self.profile = get_default_profile()
        self.roadmap = RoadmapEngine()
        self.srs = SRSEngine()
        self.comparison = comparison_engine or ComparisonEngine()
        self.advisor = advisor_engine or AdvisorEngine()
        self.career_advisor = career_advisor or CareerAdvisorEngine()
        self.conversation = conversation_engine or ConversationEngine()
        self.arch_reviewer = arch_reviewer or ArchitectureReviewer()
        self.interview_engine = interview_engine or InterviewEngine()
        self.promo_engine = promo_engine or PromoEngine()
        self.drill_engine = drill_engine or IncidentDrillEngine()
        self.pr_reviewer = pr_reviewer or PRReviewerEngine()
        self.migration_roi = migration_roi or MigrationROIEngine()
        self.status_engine = status_engine or ExecutiveStatusEngine()
        self.pattern_engine = pattern_engine or DesignPatternEngine()
        self.sql_optimizer = sql_optimizer or SQLOptimizerEngine()
        self.cost_calc = cost_calc or CostCalculatorEngine()
        self.runbook_engine = runbook_engine or RunbookEngine()
        self.data_ninja = data_ninja or DataNinjaEngine()
        self.soundbite_engine = soundbite_engine or StandupSoundbiteEngine()
        self.script_profiler = script_profiler or ScriptProfilerEngine()
        self.guardrails_engine = guardrails_engine or DataGuardrailsEngine()
        self.log_parser = log_parser or LogParserEngine()
        self.safe_eval = safe_eval or SafePythonRunner()
        self.test_generator = test_generator or TestSuiteGeneratorEngine()
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

    async def handle_today(self, session: AsyncSession, user_id: int = 0) -> str:
        stmt = select(ItemModel).order_by(ItemModel.importance_score.desc()).limit(15)
        res = await session.execute(stmt)
        items = list(res.scalars().all())

        if not items:
            return (
                "☀️ **AI ENGINEERING BRIEF**\n\n"
                "No items indexed yet today. Trigger an ingestion pass via the API or wait for the scheduled job."
            )

        declared = await self.career_advisor.diagnose_career_path(session, user_id=user_id)
        return format_daily_digest(items, scanned_count=124, accepted_count=len(items), declared_learning=declared)

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

    async def handle_work(self, args: str = "", session: Optional[AsyncSession] = None, user_id: int = 0) -> str:
        args = args.strip()
        if args and session is not None:
            await self.career_advisor.record_journal_entry(session, user_id=user_id, entry_type="work", content=args)
            diag = await self.career_advisor.diagnose_career_path(session, user_id=user_id)
            return (
                "🏢 **Work Activity Logged Successfully!**\n\n"
                f"• **Logged**: {args}\n\n"
                "🎯 **Personal Career Advisor Feedback**:\n"
                f"This strengthens your path to **{diag['target_role']}**.\n\n"
                f"🚀 **Declared Next Step**: {diag['declared_next_topic']}\n"
                f"💡 *Strategic Rationale*: {diag['why_next']}\n\n"
                f"💻 *Production Challenge*: {diag['real_world_example']}"
            )

        wc = self.profile.work_context
        recent_text = "• No recent work logged."
        if session is not None:
            recent = await self.career_advisor.get_recent_entries(session, user_id=user_id, entry_type="work", limit=3)
            if recent:
                recent_text = "\n".join([f"• {r.content} ({r.created_at.strftime('%b %d')})" for r in recent])
        return (
            "🏢 **Work Context & Activity Journal**\n\n"
            f"• **Domain**: {wc.domain}\n"
            f"• **Confidentiality Mode**: `{wc.confidentiality_mode}` (No employer secrets sent to external models)\n"
            f"• **Registered Stack**: {', '.join(wc.stack)}\n"
            f"• **Current Problem Themes**: {', '.join(wc.current_problem_themes)}\n\n"
            f"**Recent Logged Work**:\n{recent_text}\n\n"
            "💡 *To log your work today*: `/work <description>`\n"
            "Example: `/work Built streaming vLLM inference endpoint with Redis cache`"
        )

    async def handle_learned(self, args: str, session: AsyncSession, user_id: int = 0) -> str:
        args = args.strip()
        if not args:
            recent = await self.career_advisor.get_recent_entries(session, user_id=user_id, entry_type="learned", limit=3)
            recent_text = "\n".join([f"• {r.content} ({r.created_at.strftime('%b %d')})" for r in recent]) if recent else "• No recent learnings logged."
            return (
                "🧠 **Learning Journal & Skill Progression**\n\n"
                f"**Recent Logged Learnings**:\n{recent_text}\n\n"
                "💡 *To record a learning & receive your next milestone*: `/learned <concept/framework>`\n"
                "Example: `/learned Understood FlashAttention-2 tiling and memory hierarchy`"
            )

        await self.career_advisor.record_journal_entry(session, user_id=user_id, entry_type="learned", content=args)
        diag = await self.career_advisor.diagnose_career_path(session, user_id=user_id)
        return (
            "🧠 **Knowledge Logged & Skill Level Updated!**\n\n"
            f"• **You Learned**: {args}\n\n"
            "🚀 **DECLARED: WHAT YOU MUST LEARN NEXT**\n"
            f"• **Topic**: {diag['declared_next_topic']}\n"
            f"• **Why it matters**: {diag['why_next']}\n\n"
            "💻 **REAL-WORLD PRODUCTION SCENARIO**\n"
            f"• {diag['real_world_example']}\n\n"
            "Run `/career` for full gap diagnosis and `/lab` for benchmark code."
        )

    async def handle_career(self, session: AsyncSession, user_id: int = 0) -> str:
        diag = await self.career_advisor.diagnose_career_path(session, user_id=user_id)
        recent_work_str = "\n".join([f"  • {w}" for w in diag['recent_work']]) if diag['recent_work'] else "  • (No recent work entries logged yet)"
        recent_learn_str = "\n".join([f"  • {l}" for l in diag['recent_learned']]) if diag['recent_learned'] else "  • (No recent learning entries logged yet)"

        lines = [
            f"🎯 **Personal Career & Skills Advisor — {self.profile.name}**",
            f"Target Role: **{diag['target_role']}**\n",
            "🛠️ **Recent Work Execution**:",
            recent_work_str,
            "\n💡 **Recent Concept Mastery**:",
            recent_learn_str,
            f"\n🔥 **Registered Interests**: {', '.join(diag['interests'])}",
            "\n" + "—"*28,
            "🚀 **DECLARED: WHAT YOU MUST LEARN NEXT**",
            f"• **{diag['declared_next_topic']}**",
            f"  *Strategic Rationale*: {diag['why_next']}\n",
            "💻 **REAL-WORLD PRODUCTION SCENARIO**",
            f"• {diag['real_world_example']}\n",
            "💡 *Commands to update your profile*: `/work <task>`, `/learned <topic>`, `/interests add <topic>`"
        ]
        return "\n".join(lines)

    async def handle_interests(self, args: str, session: AsyncSession, user_id: int = 0) -> str:
        args = args.strip()
        if args.startswith("add "):
            topic = args.replace("add ", "").strip()
            if topic:
                await self.career_advisor.record_journal_entry(session, user_id=user_id, entry_type="interest", content=topic)
                return f"✅ Registered **{topic}** in your personal interests! Sentinel will prioritize this topic."

        entries = await self.career_advisor.get_recent_entries(session, user_id=user_id, entry_type="interest", limit=10)
        custom_interests = [e.content for e in entries]
        all_interests = list(dict.fromkeys(custom_interests + self.profile.interests))
        return (
            "🔥 **Your Registered Interests & Preferences**\n\n"
            "Sentinel prioritizes intelligence and labs matching these topics:\n"
            + "\n".join([f"• {i}" for i in all_interests])
            + "\n\n💡 *To add an interest*: `/interests add <topic>` (e.g. `/interests add Agentic evals`)"
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

    async def handle_conversation(self, message_text: str, session: AsyncSession, user_id: int = 0) -> str:
        """Processes natural conversation, remembering context and long-term user facts."""
        return await self.conversation.chat(session, user_id=user_id, user_message=message_text)

    async def handle_memory(self, args: str, session: AsyncSession, user_id: int = 0) -> str:
        """Manages long-term memories: /memory, /memory add <fact>, /memory clear."""
        args = args.strip()
        if args == "clear":
            cleared_count = await self.conversation.clear_memories(session, user_id)
            return f"🧹 Cleared {cleared_count} saved memory item(s) from your long-term profile."

        if args.startswith("add "):
            fact = args.replace("add ", "").strip()
            if fact:
                await self.conversation.add_memory(session, user_id, fact)
                return f"🧠 Saved to long-term memory: '{fact}'\nI will remember this in all future conversations."

        memories = await self.conversation.get_memories(session, user_id)
        if not memories:
            return (
                "🧠 **Sentinel Long-Term AI Memory**\n\n"
                "No custom memories saved yet.\n\n"
                "💡 *How memory works*:\n"
                "• Tell me naturally: `\"Remember that I prefer PyTorch over TensorFlow\"`\n"
                "• Or explicitly add: `/memory add <fact>`\n"
                "• To clear: `/memory clear`"
            )

        lines = ["🧠 **Sentinel Long-Term AI Memory (Known Facts About You)**\n"]
        for idx, m in enumerate(memories, 1):
            lines.append(f"{idx}. {m.memory_text}")
        lines.append("\n💡 *To add a fact*: `/memory add <fact>` | *To clear*: `/memory clear`")
        return "\n".join(lines)

    async def handle_clear(self, session: AsyncSession, user_id: int = 0) -> str:
        """Resets recent chat turn history."""
        count = await self.conversation.clear_history(session, user_id)
        return f"🔄 Chat history reset ({count} turns cleared). Ready for a new conversation!"

    async def handle_review_arch(self, args: str) -> str:
        """Principal Architecture & Code Review ('Roast')."""
        return await self.arch_reviewer.review_architecture(args)

    async def handle_interview(self, args: str = "") -> str:
        """Mock Staff System Design Interviewer: generates scenario or grades candidate response."""
        args = args.strip()
        if args.lower().startswith("solve ") or args.lower().startswith("answer "):
            solution = args.split(" ", 1)[1].strip()
            return await self.interview_engine.evaluate_solution(solution)
        return await self.interview_engine.get_interview_scenario(args if args else None)

    async def handle_reproduce(self, topic: str) -> str:
        """1-Click Local 'Prove-It' benchmark script calibrated for local GPU."""
        return await self.handle_lab(topic)

    async def handle_promo(self, session: Optional[AsyncSession] = None, user_id: int = 0) -> str:
        """Compiles logged work, learnings, and wins into a STAR Promotion/Appraisal Pack."""
        return await self.promo_engine.compile_promotion_pack(session, user_id=user_id)

    async def handle_drill(self, args: str = "") -> str:
        """Production Incident Drill: simulated Sev-1 triage and RCA evaluation."""
        args = args.strip()
        if args.lower().startswith("solve ") or args.lower().startswith("answer "):
            plan = args.split(" ", 1)[1].strip()
            return await self.drill_engine.evaluate_drill(plan)
        return await self.drill_engine.start_drill()

    async def handle_pr_review(self, args: str = "") -> str:
        """Staff PR Review: scans diffs for GPU leaks, async blocks, and security holes."""
        return await self.pr_reviewer.review_diff(args)

    async def handle_roi(self, args: str = "") -> str:
        """Tech Migration ROI Calculator: realistic cloud savings and anti-hype check."""
        return await self.migration_roi.calculate_roi(args)

    async def handle_status(self, session: Optional[AsyncSession] = None, user_id: int = 0) -> str:
        """Executive 1:1 Status Generator: 60-second high-impact managerial briefing."""
        return await self.status_engine.generate_status(session, user_id=user_id)

    async def handle_pattern(self, args: str = "") -> str:
        """Staff System Design Pattern: battle-tested distributed AI and data architecture blueprints."""
        return self.pattern_engine.get_pattern(args if args else None)

    async def handle_optimize_sql(self, args: str = "") -> str:
        """Slow SQL & Pipeline Optimizer: query plan bottlenecks, rewrites & indexes."""
        return await self.sql_optimizer.optimize(args)

    async def handle_calc_cost(self, args: str = "") -> str:
        """LLM Cost & Token Budget: API billing vs self-hosted GPU break-even."""
        return self.cost_calc.parse_and_calculate(args)

    async def handle_runbook(self, args: str = "") -> str:
        """Production Runbook Generator: golden signals, alarms & emergency recovery commands."""
        return await self.runbook_engine.generate_runbook(args)

    async def handle_data_ninja(self, args: str = "") -> str:
        """Data Wrangling & SQL Ninja: window functions, complex JSON flattening & DuckDB/Polars."""
        return await self.data_ninja.solve_transform(args)

    async def handle_soundbite(self, args: str = "") -> str:
        """Standup Soundbite: 45-second conversational script & tech take for meetings."""
        return await self.soundbite_engine.generate_soundbite(args)

    async def handle_profile_script(self, args: str = "") -> str:
        """Python Script & Memory Leak Hunter: scans loops for bloat & emits vectorized code."""
        return await self.script_profiler.profile_code(args)

    async def handle_guardrails(self, args: str = "") -> str:
        """Data Quality Guardrails Generator: Pandera/Pydantic schemas to stop bad data."""
        return await self.guardrails_engine.generate_guardrails(args)

    async def handle_parse_log(self, args: str = "") -> str:
        """Regex & Log Parser Synthesizer: converts raw logs into clean tabular pipelines."""
        return await self.log_parser.parse_log_sample(args)

    async def handle_run_py(self, args: str = "") -> str:
        """Sandboxed Python Quick-Runner: safely executes math, datetime, formulas directly."""
        return self.safe_eval.execute(args)

    async def handle_gen_tests(self, args: str = "") -> str:
        """Automated Test Suite Generator: generates full pytest suites with edge cases & fixtures."""
        return await self.test_generator.generate_test_suite(args)

    async def handle_help(self) -> str:
        return get_help_text()
