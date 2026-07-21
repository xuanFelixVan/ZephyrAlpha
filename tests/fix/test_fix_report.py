# [A_test] module_id: MOD-GOV_fix_report | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_fix_report
# [INVARIANTS] Report MUST contain all fix results; MUST contain budget status
# [MODIFY-GUARD] blueprint.md §3; fix_report.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_fix_report.py
# [TTL] task_bound

from __future__ import annotations

import json

from zephyr.infrastructure.auto_fix_engine.fix_report import FixReportGenerator
from zephyr.infrastructure.auto_fix_engine.models import (
    BudgetInfo,
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
)


class TestFixReportGenerator:
    def test_instantiation(self):
        gen = FixReportGenerator()
        assert gen._history == []

    def test_generate_empty_actions(self):
        gen = FixReportGenerator()
        report = gen.generate([])
        assert report.total_attempted == 0
        assert report.succeeded == 0
        assert report.failed == 0
        assert report.escalated == 0
        assert report.dead_lettered == 0
        assert report.actions == []

    def test_generate_with_mixed_actions(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="fix_a", target="a.py", status=FixStatus.COMPLETED),
            FixAction(action_type="fix_b", target="b.py", status=FixStatus.FAILED),
            FixAction(action_type="fix_c", target="c.py", status=FixStatus.APPROVAL_PENDING, escalated=True),
            FixAction(action_type="fix_d", target="d.py", status=FixStatus.DEAD_LETTER),
        ]
        report = gen.generate(actions)
        assert report.total_attempted == 4
        assert report.succeeded == 1
        assert report.failed == 1
        assert report.escalated == 1
        assert report.dead_lettered == 1

    def test_generate_with_custom_budget_info(self):
        gen = FixReportGenerator()
        bi = BudgetInfo(daily_remaining=10, monthly_remaining=100, llm_tokens_remaining=5000)
        report = gen.generate([], budget_info=bi)
        assert report.budget_remaining.daily_remaining == 10
        assert report.budget_remaining.monthly_remaining == 100

    def test_generate_with_cascade_alerts(self):
        gen = FixReportGenerator()
        report = gen.generate([], cascade_alerts=["storm detected", "cascade active"])
        assert len(report.cascade_alerts) == 2
        assert "storm detected" in report.cascade_alerts

    def test_generate_appends_to_history(self):
        gen = FixReportGenerator()
        gen.generate([])
        gen.generate([])
        assert len(gen._history) == 2


class TestFixReportGeneratorSummary:
    def test_generate_summary_empty(self):
        gen = FixReportGenerator()
        report = gen.generate([])
        summary = gen.generate_summary(report)
        assert summary["total_attempted"] == 0
        assert summary["succeeded"] == 0
        assert summary["failed"] == 0
        assert summary["success_rate"] == 0.0

    def test_generate_summary_with_actions(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="fix_a", target="a.py", status=FixStatus.COMPLETED),
            FixAction(action_type="fix_a", target="b.py", status=FixStatus.COMPLETED),
            FixAction(action_type="fix_b", target="c.py", status=FixStatus.FAILED),
        ]
        report = gen.generate(actions)
        summary = gen.generate_summary(report)
        assert summary["total_attempted"] == 3
        assert summary["succeeded"] == 2
        assert summary["failed"] == 1
        assert abs(summary["success_rate"] - 2 / 3) < 0.01

    def test_generate_summary_by_type(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="zombie_cleanup", target="a.py", status=FixStatus.COMPLETED),
            FixAction(action_type="zombie_cleanup", target="b.py", status=FixStatus.FAILED),
            FixAction(action_type="drift_fix", target="c.py", status=FixStatus.COMPLETED),
        ]
        report = gen.generate(actions)
        summary = gen.generate_summary(report)
        assert "zombie_cleanup" in summary["by_type"]
        assert summary["by_type"]["zombie_cleanup"]["total"] == 2
        assert summary["by_type"]["zombie_cleanup"]["succeeded"] == 1
        assert summary["by_type"]["zombie_cleanup"]["failed"] == 1
        assert summary["by_type"]["drift_fix"]["total"] == 1

    def test_generate_summary_by_level(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="fix_a", target="a.py", level=FixLevel.L1_RULE, status=FixStatus.COMPLETED),
            FixAction(action_type="fix_b", target="b.py", level=FixLevel.L2_LLM, status=FixStatus.COMPLETED),
        ]
        report = gen.generate(actions)
        summary = gen.generate_summary(report)
        assert "l1_rule" in summary["by_level"]
        assert "l2_llm" in summary["by_level"]

    def test_generate_summary_by_confidence(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="fix_a", target="a.py", confidence=FixConfidence.HIGH, status=FixStatus.COMPLETED),
            FixAction(action_type="fix_b", target="b.py", confidence=FixConfidence.LOW, status=FixStatus.FAILED),
        ]
        report = gen.generate(actions)
        summary = gen.generate_summary(report)
        assert "high" in summary["by_confidence"]
        assert "low" in summary["by_confidence"]

    def test_generate_summary_budget_remaining(self):
        gen = FixReportGenerator()
        bi = BudgetInfo(daily_remaining=5, monthly_remaining=50, llm_tokens_remaining=1000)
        report = gen.generate([], budget_info=bi)
        summary = gen.generate_summary(report)
        assert summary["budget_remaining"]["daily"] == 5
        assert summary["budget_remaining"]["monthly"] == 50
        assert summary["budget_remaining"]["llm_tokens"] == 1000

    def test_generate_summary_cascade_alerts(self):
        gen = FixReportGenerator()
        report = gen.generate([], cascade_alerts=["alert1"])
        summary = gen.generate_summary(report)
        assert "alert1" in summary["cascade_alerts"]


class TestFixReportGeneratorToJson:
    def test_to_json_valid(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="fix_a", target="a.py", status=FixStatus.COMPLETED),
        ]
        report = gen.generate(actions)
        json_str = gen.to_json(report)
        parsed = json.loads(json_str)
        assert parsed["total_attempted"] == 1
        assert parsed["succeeded"] == 1
        assert len(parsed["actions"]) == 1

    def test_to_json_contains_action_fields(self):
        gen = FixReportGenerator()
        actions = [
            FixAction(action_type="fix_a", target="a.py", status=FixStatus.COMPLETED, level=FixLevel.L1_RULE),
        ]
        report = gen.generate(actions)
        json_str = gen.to_json(report)
        parsed = json.loads(json_str)
        action_data = parsed["actions"][0]
        assert "action_id" in action_data
        assert action_data["action_type"] == "fix_a"
        assert action_data["status"] == "completed"
        assert action_data["level"] == "l1_rule"

    def test_to_json_empty_report(self):
        gen = FixReportGenerator()
        report = gen.generate([])
        json_str = gen.to_json(report)
        parsed = json.loads(json_str)
        assert parsed["total_attempted"] == 0
        assert parsed["actions"] == []


class TestFixReportGeneratorHistory:
    def test_get_history_empty(self):
        gen = FixReportGenerator()
        assert gen.get_history() == []

    def test_get_history_limited(self):
        gen = FixReportGenerator()
        for _ in range(15):
            gen.generate([])
        history = gen.get_history(limit=5)
        assert len(history) == 5

    def test_get_history_returns_latest(self):
        gen = FixReportGenerator()
        gen.generate([], cascade_alerts=["first"])
        gen.generate([], cascade_alerts=["second"])
        history = gen.get_history(limit=1)
        assert history[0].cascade_alerts == ["second"]
