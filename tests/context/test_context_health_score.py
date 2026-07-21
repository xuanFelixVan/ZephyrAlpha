# [A_test] module_id: MOD-GOV_context_health_score | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_health_score
# [INVARIANTS] score_0_to_100;healthy_ge70;degraded_ge40;critical_lt40;empty_100
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_context_health_score.py
# [TTL] task_bound

from zephyr.autonomy_core.context.context_health_score import ContextHealthScore, HealthScoreReport


class TestHealthScoreReport:
    def test_creation(self):
        r = HealthScoreReport(score=85.0, status="healthy", sub_metrics={"a": 90.0})
        assert r.score == 85.0
        assert r.status == "healthy"
        assert r.sub_metrics == {"a": 90.0}


class TestContextHealthScore:
    def test_empty_metrics_returns_healthy(self):
        scorer = ContextHealthScore()
        report = scorer.compute({})
        assert report.score == 100.0
        assert report.status == "healthy"

    def test_high_scores_healthy(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 90.0, "m2": 85.0, "m3": 95.0})
        assert report.status == "healthy"
        assert report.score >= 70

    def test_medium_scores_degraded(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 50.0, "m2": 55.0})
        assert report.status == "degraded"
        assert 40 <= report.score < 70

    def test_low_scores_critical(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 20.0, "m2": 10.0})
        assert report.status == "critical"
        assert report.score < 40

    def test_score_clamped_to_100(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 150.0, "m2": 200.0})
        assert report.score <= 100.0

    def test_score_clamped_to_0(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": -50.0, "m2": -100.0})
        assert report.score >= 0.0

    def test_boundary_healthy_at_70(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 70.0})
        assert report.status == "healthy"

    def test_boundary_degraded_at_40(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 40.0})
        assert report.status == "degraded"

    def test_sub_metrics_preserved(self):
        scorer = ContextHealthScore()
        metrics = {"latency": 80.0, "accuracy": 90.0}
        report = scorer.compute(metrics)
        assert report.sub_metrics == metrics

    def test_score_rounded_to_1_decimal(self):
        scorer = ContextHealthScore()
        report = scorer.compute({"m1": 33.33, "m2": 66.66})
        assert report.score == round(report.score, 1)
