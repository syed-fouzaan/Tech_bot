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

