# [BLUEPRINT] MOD-CMP-004 | docs/03_modules/MOD-CMP-004/ | §test
# [MODULE] tests.compliance.test_compliance_continuous_ops
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.compliance.compliance_continuous_ops
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_compliance_continuous_ops.py
# [A_test] module_id: MOD-CMP-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-CMP-004 单元测试: ComplianceContinuousOps — 合规持续运营。

覆盖: 留存达标核查(B-016 7年/3年/1年), 规则新鲜度, 拦截队列积压,
探针失败 fail-closed(CRITICAL), healthy 语义(无 CRITICAL), 报告契约。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytest.importorskip(
    "zephyr.compliance.compliance_continuous_ops",
    reason="compliance_continuous_ops not importable",
)

from zephyr.compliance.compliance_continuous_ops import (  # noqa: E402
    DEFAULT_RETENTION_REQUIREMENTS,
    ComplianceContinuousOps,
    ComplianceOpsConfig,
    ComplianceOpsInput,
    evaluate_continuous_ops,
)

_NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)


def _input(**overrides) -> ComplianceOpsInput:
    base = dict(
        retention_status={"trade_log": 3000, "decision_log": 1500, "system_log": 500},
        rule_updates={"R-001": _NOW - timedelta(days=30)},
        intercept_queue_pending=0,
        now=_NOW,
    )
    base.update(overrides)
    return ComplianceOpsInput(**base)


# ── B-016 默认留存要求 ───────────────────────────────────────────────


class TestRetentionDefaults:
    def test_default_requirements_match_b016(self):
        mapping = {r.category: r.min_days for r in DEFAULT_RETENTION_REQUIREMENTS}
        assert mapping["trade_log"] == 2555  # 交易日志 ≥7年
        assert mapping["decision_log"] == 1095  # 决策日志 ≥3年
        assert mapping["system_log"] == 365  # 系统日志 ≥1年


# ── 纯函数评估 ───────────────────────────────────────────────────────


class TestEvaluateContinuousOps:
    def test_all_healthy(self):
        report = evaluate_continuous_ops(_input(), ComplianceOpsConfig())
        assert report.healthy
        criticals = [f for f in report.findings if f.severity == "CRITICAL"]
        assert criticals == []

    def test_retention_shortfall_critical(self):
        report = evaluate_continuous_ops(
            _input(retention_status={"trade_log": 1000, "decision_log": 1500, "system_log": 500}),
            ComplianceOpsConfig(),
        )
        assert not report.healthy
        shortfalls = [f for f in report.findings if f.check_id == "retention_shortfall"]
        assert shortfalls and shortfalls[0].severity == "CRITICAL"
        assert "trade_log" in shortfalls[0].message

    def test_retention_category_missing_critical(self):
        # 类别缺失=无法验证留存 → fail-closed CRITICAL
        report = evaluate_continuous_ops(
            _input(retention_status={"trade_log": 3000}),
            ComplianceOpsConfig(),
        )
        assert not report.healthy
        missing = [f for f in report.findings if f.check_id == "retention_unverifiable"]
        assert missing
        assert "decision_log" in missing[0].message

    def test_stale_rule_warning_keeps_healthy(self):
        report = evaluate_continuous_ops(
            _input(rule_updates={"R-001": _NOW - timedelta(days=400)}),
            ComplianceOpsConfig(rule_stale_days=365),
        )
        stale = [f for f in report.findings if f.check_id == "rule_stale"]
        assert stale and stale[0].severity == "WARNING"
        assert report.healthy  # WARNING 不影响 healthy

    def test_no_rules_warning(self):
        report = evaluate_continuous_ops(
            _input(rule_updates={}),
            ComplianceOpsConfig(),
        )
        absent = [f for f in report.findings if f.check_id == "rules_absent"]
        assert absent

    def test_intercept_backlog_warning(self):
        report = evaluate_continuous_ops(
            _input(intercept_queue_pending=600),
            ComplianceOpsConfig(intercept_queue_backlog_threshold=500),
        )
        backlog = [f for f in report.findings if f.check_id == "intercept_backlog"]
        assert backlog and backlog[0].severity == "WARNING"

    def test_report_immutable(self):
        report = evaluate_continuous_ops(_input(), ComplianceOpsConfig())
        with pytest.raises(AttributeError):
            report.healthy = False  # type: ignore[misc]

    def test_fresh_rule_no_stale_finding(self):
        report = evaluate_continuous_ops(_input(), ComplianceOpsConfig())
        stale = [f for f in report.findings if f.check_id == "rule_stale"]
        assert stale == []


# ── 编排层（探针 fail-closed）───────────────────────────────────────


class TestComplianceContinuousOps:
    def _ops(self, **probes) -> ComplianceContinuousOps:
        kwargs = dict(
            retention_probe=lambda: {"trade_log": 3000, "decision_log": 1500, "system_log": 500},
            rule_update_probe=lambda: {"R-001": _NOW},
            queue_pending_probe=lambda: 0,
        )
        kwargs.update(probes)
        return ComplianceContinuousOps(**kwargs)

    def test_run_once_healthy(self):
        report = self._ops().run_once(now=_NOW)
        assert report.healthy
        assert report.run_id

    def test_probe_failure_critical_fail_closed(self):
        def _boom():
            raise RuntimeError("audit store down")

        report = self._ops(retention_probe=_boom).run_once(now=_NOW)
        assert not report.healthy
        probe_err = [f for f in report.findings if f.check_id == "probe_error"]
        assert probe_err and probe_err[0].severity == "CRITICAL"
