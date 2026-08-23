# [BLUEPRINT] MOD-CMP-003 | docs/03_modules/MOD-CMP-003/ | §test
# [MODULE] tests.compliance.test_compliance_tech_enabler
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.compliance.compliance_tech_enabler
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_compliance_tech_enabler.py
# [A_test] module_id: MOD-CMP-003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-CMP-003 单元测试: ComplianceTechEnabler — 合规技术使能器。

覆盖: 声明式规则定义→ComplianceRule(CTR-P1-012) 物化, 枚举校验
(enforcement_action/severity 未知值拒绝, 不静默降级), severity 排序,
必填缺失/重复 rule_id/非映射条目拒绝, 源失败 fail-closed 上抛。
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytest.importorskip(
    "zephyr.compliance.compliance_tech_enabler",
    reason="compliance_tech_enabler not importable",
)

from zephyr.compliance.compliance_tech_enabler import (  # noqa: E402
    ComplianceEnablementError,
    ComplianceTechEnabler,
    materialize_compliance_rules,
)

_NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)


def _definition(**overrides) -> dict:
    base = dict(
        rule_id="R-001",
        rule_name="非交易时段禁下单",
        rule_type="trading_window",
        severity="critical",
        enforcement_action="block",
        rule_logic="now not in trading_window",
        description="L-003 非交易时段订单为废单",
        jurisdiction="CN-SSE/SZSE",
        version="1.0",
        is_active=True,
    )
    base.update(overrides)
    return base


# ── 物化纯函数 ───────────────────────────────────────────────────────


class TestMaterialize:
    def test_valid_definition_materializes(self):
        result = materialize_compliance_rules([_definition()], now=_NOW)
        assert len(result.rules) == 1
        rule = result.rules[0]
        assert rule.rule_id == "R-001"
        assert rule.severity == "critical"
        assert rule.enforcement_action == "block"
        assert rule.is_active is True
        assert rule.created_at == _NOW
        assert result.rejected == ()

    def test_severity_sorting(self):
        defs = [
            _definition(rule_id="R-low", severity="low"),
            _definition(rule_id="R-crit", severity="critical"),
            _definition(rule_id="R-med", severity="medium"),
            _definition(rule_id="R-high", severity="high"),
        ]
        result = materialize_compliance_rules(defs, now=_NOW)
        assert [r.rule_id for r in result.rules] == [
            "R-crit", "R-high", "R-med", "R-low",
        ]

    def test_unknown_enforcement_action_rejected(self):
        result = materialize_compliance_rules(
            [_definition(enforcement_action="ignore")], now=_NOW,
        )
        assert result.rules == ()
        assert len(result.rejected) == 1
        assert "enforcement_action" in result.rejected[0].reason

    def test_unknown_severity_rejected(self):
        result = materialize_compliance_rules(
            [_definition(severity="fatal")], now=_NOW,
        )
        assert result.rules == ()
        assert "severity" in result.rejected[0].reason

    def test_missing_required_key_rejected(self):
        bad = _definition()
        del bad["rule_logic"]
        result = materialize_compliance_rules([bad], now=_NOW)
        assert result.rules == ()
        assert "rule_logic" in result.rejected[0].reason

    def test_duplicate_rule_id_rejected(self):
        result = materialize_compliance_rules(
            [_definition(), _definition(version="2.0")], now=_NOW,
        )
        assert len(result.rules) == 1
        assert len(result.rejected) == 1
        assert "duplicate" in result.rejected[0].reason

    def test_non_mapping_entry_rejected(self):
        result = materialize_compliance_rules(["not-a-mapping"], now=_NOW)
        assert result.rules == ()
        assert len(result.rejected) == 1

    def test_inactive_flag_preserved(self):
        result = materialize_compliance_rules(
            [_definition(is_active=False)], now=_NOW,
        )
        assert len(result.rules) == 1
        assert result.rules[0].is_active is False
        assert result.active_count == 0

    def test_result_immutable(self):
        result = materialize_compliance_rules([_definition()], now=_NOW)
        with pytest.raises(AttributeError):
            result.active_count = 99  # type: ignore[misc]

    def test_mixed_batch_partial_accept(self):
        result = materialize_compliance_rules(
            [_definition(), _definition(rule_id="R-002", severity="bad")],
            now=_NOW,
        )
        assert len(result.rules) == 1
        assert len(result.rejected) == 1


# ── 使能器编排 ───────────────────────────────────────────────────────


class TestComplianceTechEnabler:
    def test_load_active_rules_filters_inactive(self):
        enabler = ComplianceTechEnabler(
            definition_source=lambda: [
                _definition(),
                _definition(rule_id="R-002", is_active=False),
            ],
        )
        active = enabler.load_active_rules()
        assert [r.rule_id for r in active] == ["R-001"]

    def test_source_failure_raises_fail_closed(self):
        def _boom():
            raise RuntimeError("config store down")

        enabler = ComplianceTechEnabler(definition_source=_boom)
        with pytest.raises(ComplianceEnablementError):
            enabler.load_active_rules()

    def test_last_result_cached(self):
        enabler = ComplianceTechEnabler(definition_source=lambda: [_definition()])
        assert enabler.last_result is None
        enabler.load_active_rules()
        assert enabler.last_result is not None
        assert enabler.last_result.active_count == 1
