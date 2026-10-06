"""Tests for advanced career advisor features: Architecture Reviewer, Mock Interviewer, STAR Promo Pack, and Reproduce scripts."""

import pytest
from sentinel.app.domain.architecture_reviewer import ArchitectureReviewer
from sentinel.app.domain.interview import InterviewEngine
from sentinel.app.domain.promo import PromoEngine
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.bot.registry import COMMANDS


@pytest.mark.asyncio
async def test_architecture_reviewer():
    reviewer = ArchitectureReviewer()
    # Test empty prompt returns usage guide
    usage = await reviewer.review_architecture("")
    assert "Principal Architecture" in usage
    assert "/review_arch" in usage

    # Test review with snippet
    review = await reviewer.review_architecture("FastAPI endpoint loading PyTorch model with synchronous inference on GPU")
    assert len(review) > 20


@pytest.mark.asyncio
async def test_mock_interview_engine():
    interviewer = InterviewEngine()
    # Test interview problem generation
    problem = await interviewer.get_interview_scenario("Real-Time vLLM Inference Service")
    assert "Mock Staff System Design Interview" in problem

    # Test candidate solution evaluation
    eval_result = await interviewer.evaluate_solution("We use Redis cache, batch requests with dynamic batching, and scale workers horizontally.")
    assert len(eval_result) > 20


@pytest.mark.asyncio
async def test_promo_pack_engine():
    promo = PromoEngine()
    pack = await promo.compile_promotion_pack()
    assert "Performance & Promotion Pack" in pack or "Executive" in pack
    assert "STAR" in pack or "Accomplishments" in pack


@pytest.mark.asyncio
async def test_bot_handlers_new_commands():
    handler = BotCommandHandler()

    # /review_arch
    roast_msg = await handler.handle_review_arch("vLLM streaming endpoint")
    assert len(roast_msg) > 10

    # /interview scenario
    interview_scenario = await handler.handle_interview("")
    assert "Interview" in interview_scenario

    # /interview solve <solution>
    interview_eval = await handler.handle_interview("solve Partition Kafka topics by user_id and use Ray for distributed workers")
    assert len(interview_eval) > 10

    # /reproduce
    reproduce_code = await handler.handle_reproduce("vllm")
    assert "RTX 4060" in reproduce_code or "vllm" in reproduce_code.lower()

    # /promo
    promo_msg = await handler.handle_promo()
    assert "Promotion" in promo_msg or "Performance" in promo_msg

    # /drill
    drill_start = await handler.handle_drill()
    assert "INCIDENT DRILL" in drill_start
    drill_eval = await handler.handle_drill("solve Drain traffic from the OOM nodes and rollback the max_model_len config")
    assert len(drill_eval) > 10

    # /pr_review
    pr_usage = await handler.handle_pr_review("")
    assert "PR & Git Diff Review" in pr_usage
    pr_res = await handler.handle_pr_review("def infer(x): y = model(x); return y.cpu().numpy()")
    assert len(pr_res) > 10

    # /roi
    roi_usage = await handler.handle_roi("")
    assert "Migration ROI" in roi_usage
    roi_res = await handler.handle_roi("Pandas vs Polars")
    assert len(roi_res) > 10

    # /status
    status_msg = await handler.handle_status()
    assert "Executive 1:1" in status_msg
    assert "SHIPPED" in status_msg

    # /pattern
    pattern_msg = await handler.handle_pattern("chunked_prefill")
    assert "Chunked Prefill" in pattern_msg
    assert "Production Implementation Blueprint" in pattern_msg

    # /optimize_sql
    sql_usage = await handler.handle_optimize_sql("")
    assert "SQL & Pipeline Optimizer" in sql_usage
    sql_opt = await handler.handle_optimize_sql("SELECT * FROM events e JOIN users u ON e.user_id = u.id WHERE e.ts > '2025-01-01'")
    assert len(sql_opt) > 10

    # /calc_cost
    cost_usage = await handler.handle_calc_cost("")
    assert "Cost & Token Budget" in cost_usage
    cost_res = await handler.handle_calc_cost("10000 gpt-4o")
    assert "Monthly" in cost_res or "Cost" in cost_res

    # /runbook
    runbook_vllm = await handler.handle_runbook("vllm")
    assert "vLLM Inference Service" in runbook_vllm
    assert "Golden Signals" in runbook_vllm

    # /data_ninja
    ninja_usage = await handler.handle_data_ninja("")
    assert "Data Wrangling & SQL Ninja" in ninja_usage
    ninja_res = await handler.handle_data_ninja("7-day rolling average in DuckDB")
    assert len(ninja_res) > 10

    # /soundbite
    soundbite_usage = await handler.handle_soundbite("")
    assert "Standup Soundbite" in soundbite_usage
    soundbite_res = await handler.handle_soundbite("Speculative Decoding")
    assert len(soundbite_res) > 10

    # /profile_script
    profile_usage = await handler.handle_profile_script("")
    assert "Memory Leak Hunter" in profile_usage
    profile_res = await handler.handle_profile_script("for i in range(100): df = pd.concat([df, row])")
    assert len(profile_res) > 10

    # /guardrails
    guardrails_usage = await handler.handle_guardrails("")
    assert "Data Quality Guardrails" in guardrails_usage
    guardrails_res = await handler.handle_guardrails("stoppages: timestamp, machine_id int, reason str")
    assert len(guardrails_res) > 10

    # /parse_log
    log_usage = await handler.handle_parse_log("")
    assert "Log Parser" in log_usage
    log_res = await handler.handle_parse_log("2026-10-06 14:00:00 [STOPPAGE] ID=42 Duration=120s")
    assert len(log_res) > 10

    # /run_py (Sandboxed execution)
    py_calc = await handler.handle_run_py("5000 * 12 / 100")
    assert "600.0" in py_calc or "600" in py_calc

    py_print = await handler.handle_run_py("import math; print(math.sqrt(144))")
    assert "12.0" in py_print

    py_blocked = await handler.handle_run_py("import os; os.system('echo test')")
    assert "Execution Blocked" in py_blocked

    # /gen_tests
    test_gen_usage = await handler.handle_gen_tests("")
    assert "Test Suite Generator" in test_gen_usage
    test_gen_code = await handler.handle_gen_tests("def calculate_scrap_rate(scraps, total): return scraps / total if total > 0 else 0.0")
    assert len(test_gen_code) > 10


def test_quick_actions_keyboard():
    from sentinel.app.bot.keyboards import get_quick_actions_keyboard
    kb = get_quick_actions_keyboard()
    assert kb is not None
    assert len(kb.inline_keyboard) >= 4


def test_command_registry_contains_new_commands():
    assert "review_arch" in COMMANDS
    assert "roast" in COMMANDS
    assert "reproduce" in COMMANDS
    assert "interview" in COMMANDS
    assert "brag" in COMMANDS
    assert "promo" in COMMANDS
    assert "drill" in COMMANDS
    assert "pr_review" in COMMANDS
    assert "roi" in COMMANDS
    assert "status" in COMMANDS
    assert "pattern" in COMMANDS
    assert "optimize_sql" in COMMANDS
    assert "calc_cost" in COMMANDS
    assert "runbook" in COMMANDS
    assert "data_ninja" in COMMANDS
    assert "soundbite" in COMMANDS
    assert "profile_script" in COMMANDS
    assert "guardrails" in COMMANDS
    assert "parse_log" in COMMANDS
    assert "run_py" in COMMANDS
    assert "gen_tests" in COMMANDS




