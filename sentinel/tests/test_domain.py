"""Tests for domain services: roadmap, hardware calculator, SRS quizzes, and work impact log."""

import pytest
from sentinel.app.domain.roadmap import RoadmapEngine
from sentinel.app.domain.hardware import calculate_hardware_fit
from sentinel.app.domain.srs import SRSEngine
from sentinel.app.domain.win import WorkImpactEngine


def test_roadmap_summary_and_recommendations():
    engine = RoadmapEngine()
    summary = engine.get_summary()
    assert summary["total_nodes"] > 0
    assert summary["completed"] >= 1

    next_nodes = engine.get_next_recommended_nodes(2)
    assert len(next_nodes) <= 2
    for node in next_nodes:
        assert node.status != "completed"


def test_hardware_fit_7b_on_8gb():
    res = calculate_hardware_fit("Qwen2.5-7B", user_vram_gb=8.0)
    assert res.param_count_b == 7.0
    assert res.verdict == "FITS_IN_Q4"
    assert res.weights_q4_gb < 8.0


def test_hardware_fit_70b_on_8gb():
    res = calculate_hardware_fit("Llama-3.1-70B", user_vram_gb=8.0)
    assert res.param_count_b == 70.0
    assert res.verdict == "NEEDS_MORE_VRAM"
    assert "Colab" in res.explanation or "exceeds" in res.explanation


def test_srs_quiz_generation_and_evaluation():
    srs = SRSEngine()
    quizzes = srs.get_daily_quiz(1)
    assert len(quizzes) == 1
    q = quizzes[0]

    # Evaluate correct answer
    res_correct = srs.evaluate_answer(q.id, q.correct_idx)
    assert res_correct["is_correct"]

    # Evaluate wrong answer
    wrong_idx = (q.correct_idx + 1) % len(q.options)
    res_wrong = srs.evaluate_answer(q.id, wrong_idx)
    assert not res_wrong["is_correct"]


def test_work_impact_log_captures_star_metric():
    engine = WorkImpactEngine()
    entry = engine.format_win_entry(
        title="Automated Data Quality Checks on Airflow",
        metric_before="Manual validation 1 hour daily",
        metric_after="Zero manual steps, automated Great Expectations tests",
        impact_summary="Prevented broken schema ingestion in downstream warehouse.",
    )
    assert "Accomplishment" in entry["formatted_star"]
    assert "Manual validation" in entry["formatted_star"]

    # Should raise error if secrets entered in work impact log
    with pytest.raises(ValueError):
        engine.format_win_entry(
            title="Leaked Key in Log",
            metric_before="sk-1234567890abcdef1234567890abcdef",
            metric_after="None",
            impact_summary="Test",
        )
