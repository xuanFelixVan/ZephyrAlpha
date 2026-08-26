# [BLUEPRINT] MOD-CMP-015 | docs/03_modules/_domain_compliance/compliance_policy_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-CMP-015 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.compliance.test_compliance_policy_engine
# [TESTS] src/zephyr/compliance/compliance_policy_engine.py
"""MOD-CMP-015 单元测试：compliance_policy_engine 合规策略即代码引擎。

蓝图验收（B14-04651/CAND-CMP-006，§0定位/§1规则）：
YAML 规则 DSL schema（条件/动作/严重度）+ 版本管理 + 回放验证（回放器注入）+
非交易时段热加载（时段判定注入）+ 人工审批队列。时钟/回放器/时段全注入，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.compliance.compliance_policy_engine",
    reason="compliance_policy_engine not importable",
)

from zephyr.compliance.compliance_policy_engine import (  # noqa: E402
    ChangeStatus,
    CompliancePolicyEngine,
    CompliancePolicyError,
    PolicyAction,
    ReplayReport,
    Severity,
)

_T0 = datetime.datetime(2026, 8, 25, 20, 0, 0)

_V1 = {
    "version": "v1",
    "rules": [
        {"rule_id": "r-cancel", "condition": "cancel_rate > 0.5",
         "action": "alert", "severity": "warning"},
        {"rule_id": "r-wash", "condition": "self_trade_ratio >= 0.3 and volume >= 1000",
         "action": "block", "severity": "critical"},
    ],
}

_V1_YAML = """
version: v1y
rules:
  - rule_id: r-cancel
    condition: cancel_rate > 0.5
    action: alert
    severity: warning
  - rule_id: r-tail
    condition: tail_volume_ratio >= 0.4 or deviation > 0.05
    action: record
    severity: info
"""

_V2 = {
    "version": "v2",
    "rules": [
        {"rule_id": "r-cancel", "condition": "cancel_rate > 0.3",
         "action": "block", "severity": "critical"},
    ],
}


def _engine(non_trading: bool = True, replayer=None) -> CompliancePolicyEngine:
    return CompliancePolicyEngine(
        clock=lambda: _T0,
        replayer=replayer,
        is_non_trading_time=lambda: non_trading,
    )


# ──────────────────────────────────────────────────────────────────────────────
# schema 解析
# ──────────────────────────────────────────────────────────────────────────────


class TestSchema:
    def test_submit_mapping_ok(self) -> None:
        eng = _engine()
        change = eng.submit_change("c1", _V1)
        assert change.status is ChangeStatus.PENDING
        assert change.version == "v1"
        assert len(change.rules) == 2

    def test_submit_yaml_text_ok(self) -> None:
        pytest.importorskip("yaml", reason="PyYAML not installed")
        eng = _engine()
        change = eng.submit_change("c1", _V1_YAML)
        assert change.version == "v1y"
        assert change.rules[1].action is PolicyAction.RECORD
        assert change.rules[1].severity is Severity.INFO

    def test_missing_version_raises(self) -> None:
        eng = _engine()
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", {"rules": []})

    def test_missing_rule_key_raises(self) -> None:
        eng = _engine()
        bad = {"version": "v", "rules": [{"rule_id": "r", "condition": "x > 1", "action": "alert"}]}
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", bad)

    def test_action_out_of_vocab_raises(self) -> None:
        eng = _engine()
        bad = {"version": "v", "rules": [
            {"rule_id": "r", "condition": "x > 1", "action": "nuke", "severity": "info"}]}
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", bad)

    def test_severity_out_of_vocab_raises(self) -> None:
        eng = _engine()
        bad = {"version": "v", "rules": [
            {"rule_id": "r", "condition": "x > 1", "action": "alert", "severity": "fatal"}]}
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", bad)

    def test_condition_syntax_invalid_raises(self) -> None:
        eng = _engine()
        bad = {"version": "v", "rules": [
            {"rule_id": "r", "condition": "cancel_rate ~~ 0.5", "action": "alert", "severity": "info"}]}
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", bad)

    def test_duplicate_rule_id_raises(self) -> None:
        eng = _engine()
        bad = {"version": "v", "rules": [
            {"rule_id": "r", "condition": "x > 1", "action": "alert", "severity": "info"},
            {"rule_id": "r", "condition": "x > 2", "action": "block", "severity": "critical"},
        ]}
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", bad)

    def test_duplicate_change_id_raises(self) -> None:
        eng = _engine()
        eng.submit_change("c1", _V1)
        with pytest.raises(CompliancePolicyError):
            eng.submit_change("c1", _V2)


# ──────────────────────────────────────────────────────────────────────────────
# 审批队列 + 版本管理
# ──────────────────────────────────────────────────────────────────────────────


class TestApprovalAndVersions:
    def test_approve_activates_version(self) -> None:
        eng = _engine()
        eng.submit_change("c1", _V1)
        eng.approve_change("c1")
        assert eng.active_version() == "v1"
        assert eng.change_status("c1") is ChangeStatus.APPROVED
        assert len(eng.active_rules()) == 2

    def test_no_active_version_evaluate_raises(self) -> None:
        eng = _engine()
        with pytest.raises(CompliancePolicyError):
            eng.evaluate({"cancel_rate": 0.9})

    def test_reject_keeps_inactive(self) -> None:
        eng = _engine()
        eng.submit_change("c1", _V1)
        eng.reject_change("c1")
        assert eng.active_version() is None
        assert eng.change_status("c1") is ChangeStatus.REJECTED

    def test_unknown_change_raises(self) -> None:
        eng = _engine()
        with pytest.raises(CompliancePolicyError):
            eng.approve_change("ghost")
        with pytest.raises(CompliancePolicyError):
            eng.change_status("ghost")

    def test_double_approve_raises(self) -> None:
        eng = _engine()
        eng.submit_change("c1", _V1)
        eng.approve_change("c1")
        with pytest.raises(CompliancePolicyError):
            eng.approve_change("c1")

    def test_reject_after_approve_raises(self) -> None:
        eng = _engine()
        eng.submit_change("c1", _V1)
        eng.approve_change("c1")
        with pytest.raises(CompliancePolicyError):
            eng.reject_change("c1")

    def test_pending_order_deterministic(self) -> None:
        eng = _engine()
        eng.submit_change("c2", _V2)
        eng.submit_change("c1", _V1)
        pending = eng.pending_changes()
        assert [c.change_id for c in pending] == ["c1", "c2"]  # 同刻按 id 排序

    def test_version_switch(self) -> None:
        eng = _engine()
        eng.submit_change("c1", _V1)
        eng.approve_change("c1")
        eng.submit_change("c2", _V2)
        eng.approve_change("c2")
        assert eng.active_version() == "v2"
        assert len(eng.active_rules()) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 回放验证 + 热加载门禁（注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestReplayAndHotReload:
    def test_replay_mismatch_blocks(self) -> None:
        eng = _engine(replayer=lambda old, new: ReplayReport(matched=False, details=("diff@r1",)))
        eng.submit_change("c1", _V1)
        with pytest.raises(CompliancePolicyError):
            eng.approve_change("c1")
        assert eng.active_version() is None

    def test_replay_match_passes(self) -> None:
        seen: list[tuple[int, int]] = []
        eng = _engine(replayer=lambda old, new: seen.append((len(old), len(new)))
                      or ReplayReport(matched=True))
        eng.submit_change("c1", _V1)
        eng.approve_change("c1")
        assert seen == [(0, 2)]  # 旧版本空 → 新2条

    def test_trading_time_blocks_hot_reload(self) -> None:
        eng = _engine(non_trading=False)
        eng.submit_change("c1", _V1)
        with pytest.raises(CompliancePolicyError):
            eng.approve_change("c1")
        assert eng.active_version() is None


# ──────────────────────────────────────────────────────────────────────────────
# 求值（条件 DSL）
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluate:
    def _active(self) -> CompliancePolicyEngine:
        eng = _engine()
        eng.submit_change("c1", _V1)
        eng.approve_change("c1")
        return eng

    def test_hit_sorted_by_rule_id(self) -> None:
        eng = self._active()
        out = eng.evaluate({"cancel_rate": 0.9, "self_trade_ratio": 0.5, "volume": 2000})
        assert [d.rule_id for d in out] == ["r-cancel", "r-wash"]
        assert out[1].action is PolicyAction.BLOCK
        assert out[1].severity is Severity.CRITICAL

    def test_no_hit(self) -> None:
        eng = self._active()
        assert eng.evaluate({"cancel_rate": 0.1, "self_trade_ratio": 0.1, "volume": 10}) == []

    def test_and_semantics(self) -> None:
        eng = self._active()
        out = eng.evaluate({"cancel_rate": 0.1, "self_trade_ratio": 0.5, "volume": 2000})
        assert [d.rule_id for d in out] == ["r-wash"]  # and 两子句全真

    def test_missing_field_fail_closed(self) -> None:
        eng = self._active()
        with pytest.raises(CompliancePolicyError):
            eng.evaluate({"self_trade_ratio": 0.5, "volume": 2000})  # 缺 cancel_rate

    def test_in_operator(self) -> None:
        eng = _engine()
        eng.submit_change("c1", {"version": "v", "rules": [
            {"rule_id": "r-in", "condition": "exchange in ['SH', 'SZ']",
             "action": "record", "severity": "info"}]})
        eng.approve_change("c1")
        assert len(eng.evaluate({"exchange": "SH"})) == 1
        assert eng.evaluate({"exchange": "BJ"}) == []

    def test_deterministic_same_input(self) -> None:
        e1 = self._active()
        e2 = self._active()
        ctx = {"cancel_rate": 0.9, "self_trade_ratio": 0.0, "volume": 0}
        assert e1.evaluate(ctx) == e2.evaluate(ctx)
