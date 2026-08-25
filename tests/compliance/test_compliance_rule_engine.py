# [BLUEPRINT] MOD-CMP-012 | docs/03_modules/_domain_compliance/compliance_rule_engine/blueprint.md | §test
# [A_test] module_id: MOD-CMP-012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ComplianceRuleEngine 单元测试 (MOD-CMP-012, MVP)。

覆盖: DSL 解析校验（字段/op/severity/复合条件）/ 版本管理器（不可变历史+活跃指针）/
Pre-Trade 实时评估聚合（Hard Block>Soft Warn>Warning>Pass）/ 评估错误 Fail-Closed 拒单 /
命中经 hit_sink 落 compliance_log 契约 / 盘后批量审计器 / 收编规则包 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.compliance.compliance_rule_engine import (
    ComplianceDisposition,
    ComplianceRule,
    ComplianceRuleEngine,
    ComplianceVerdict,
    InvalidComplianceRuleError,
    RuleDslParser,
    RuleHit,
    RuleVersionManager,
    trading_compliance_rule_pack,
)


def _rule(rule_id: str = "R-001", version: str = "v1", severity: str = "hard_block",
          condition: dict | None = None) -> dict:
    return {
        "rule_id": rule_id,
        "version": version,
        "description": f"{rule_id} 描述",
        "severity": severity,
        "condition": condition if condition is not None else {"field": "qty", "op": ">", "value": 100},
    }


# ── DSL 解析器 ───────────────────────────────────────────────────────────────


def test_parse_valid_rule() -> None:
    rule = RuleDslParser.parse(_rule())
    assert isinstance(rule, ComplianceRule)
    assert rule.rule_id == "R-001"
    assert rule.severity is ComplianceDisposition.HARD_BLOCK


def test_parse_composite_condition() -> None:
    rule = RuleDslParser.parse(_rule(condition={
        "all": [
            {"field": "price_dev", "op": ">", "value": 0.03},
            {"any": [{"field": "share", "op": ">", "value": 0.3}, {"field": "spoof", "op": "==", "value": True}]},
        ]
    }))
    assert "all" in rule.condition


@pytest.mark.parametrize("bad", [
    {},  # 缺字段
    {"rule_id": "R", "version": "v1", "description": "d", "severity": "hard_block"},  # 缺 condition
    _rule(severity="fatal"),  # 非法 severity
    _rule(condition={"field": "q", "op": "~", "value": 1}),  # 非法 op
    _rule(condition={"field": "", "op": ">", "value": 1}),  # 空 field
    _rule(condition={"all": []}),  # 空复合
    _rule(condition={"all": [{"field": "q"}]}),  # 原子缺 op/value
    _rule(rule_id=""),  # 空 rule_id
    _rule(version=""),  # 空 version
])
def test_parse_invalid_rejected(bad: dict) -> None:
    with pytest.raises(InvalidComplianceRuleError):
        RuleDslParser.parse(bad)


# ── 版本管理器 ───────────────────────────────────────────────────────────────


def test_version_manager_register_and_activate() -> None:
    mgr = RuleVersionManager()
    r1 = RuleDslParser.parse(_rule(version="v1"))
    r2 = RuleDslParser.parse(_rule(version="v2", condition={"field": "qty", "op": ">", "value": 200}))
    mgr.register(r1)
    mgr.register(r2)
    mgr.activate("R-001", "v1")
    assert mgr.active("R-001") == r1
    mgr.activate("R-001", "v2")
    assert mgr.active("R-001") == r2
    assert mgr.history("R-001") == (r1, r2)


def test_version_manager_duplicate_version_rejected() -> None:
    mgr = RuleVersionManager()
    mgr.register(RuleDslParser.parse(_rule(version="v1")))
    with pytest.raises(InvalidComplianceRuleError):
        mgr.register(RuleDslParser.parse(_rule(version="v1")))


def test_activate_unregistered_version_rejected() -> None:
    mgr = RuleVersionManager()
    mgr.register(RuleDslParser.parse(_rule(version="v1")))
    with pytest.raises(InvalidComplianceRuleError):
        mgr.activate("R-001", "v9")


def test_active_unknown_rule_returns_none() -> None:
    assert RuleVersionManager().active("ghost") is None


def test_deactivate() -> None:
    mgr = RuleVersionManager()
    mgr.register(RuleDslParser.parse(_rule(version="v1")))
    mgr.activate("R-001", "v1")
    mgr.deactivate("R-001")
    assert mgr.active("R-001") is None
    assert len(mgr.history("R-001")) == 1  # 历史不可变保留


# ── 实时评估器 ───────────────────────────────────────────────────────────────


def _engine(*rules: dict, hits: list | None = None) -> ComplianceRuleEngine:
    eng = ComplianceRuleEngine(hit_sink=hits.append if hits is not None else None)
    eng.load_rule_pack(rules)
    return eng


def test_evaluate_pass_when_no_hit() -> None:
    eng = _engine(_rule())
    v = eng.evaluate_pre_trade({"qty": 50})
    assert v.disposition is ComplianceDisposition.PASS
    assert v.hits == ()


def test_evaluate_hard_block() -> None:
    eng = _engine(_rule())
    v = eng.evaluate_pre_trade({"qty": 150})
    assert v.disposition is ComplianceDisposition.HARD_BLOCK
    assert v.hits[0].rule_id == "R-001"


def test_disposition_aggregation_order() -> None:
    eng = _engine(
        _rule("R-W", "v1", "warning", {"field": "qty", "op": ">", "value": 10}),
        _rule("R-S", "v1", "soft_warn", {"field": "qty", "op": ">", "value": 10}),
    )
    v = eng.evaluate_pre_trade({"qty": 50})
    assert v.disposition is ComplianceDisposition.SOFT_WARN
    eng2 = _engine(
        _rule("R-W", "v1", "warning", {"field": "qty", "op": ">", "value": 10}),
        _rule("R-S", "v1", "soft_warn", {"field": "qty", "op": ">", "value": 10}),
        _rule("R-H", "v1", "hard_block", {"field": "qty", "op": ">", "value": 10}),
    )
    assert eng2.evaluate_pre_trade({"qty": 50}).disposition is ComplianceDisposition.HARD_BLOCK


def test_warning_hit_still_passes_with_record() -> None:
    eng = _engine(_rule("R-W", "v1", "warning", {"field": "qty", "op": ">", "value": 10}))
    v = eng.evaluate_pre_trade({"qty": 50})
    assert v.disposition is ComplianceDisposition.WARNING
    assert len(v.hits) == 1


def test_evaluate_error_fail_closed_hard_block() -> None:
    eng = _engine(_rule())  # 需要字段 qty
    v = eng.evaluate_pre_trade({"other": 1})  # 字段缺失
    assert v.disposition is ComplianceDisposition.HARD_BLOCK
    assert v.engine_error is not None


def test_composite_condition_evaluation() -> None:
    eng = _engine(_rule(condition={
        "all": [{"field": "a", "op": ">=", "value": 1}, {"any": [{"field": "b", "op": "<", "value": 5}, {"field": "c", "op": "in", "value": [1, 2]}]}]
    }))
    assert eng.evaluate_pre_trade({"a": 1, "b": 4}).disposition is ComplianceDisposition.HARD_BLOCK
    assert eng.evaluate_pre_trade({"a": 1, "c": 2}).disposition is ComplianceDisposition.HARD_BLOCK
    assert eng.evaluate_pre_trade({"a": 1, "b": 9, "c": 3}).disposition is ComplianceDisposition.PASS
    assert eng.evaluate_pre_trade({"a": 0, "b": 4}).disposition is ComplianceDisposition.PASS


def test_hit_sink_receives_compliance_log_record() -> None:
    hits: list[dict] = []
    eng = _engine(_rule(), hits=hits)
    eng.evaluate_pre_trade({"qty": 150})
    assert len(hits) == 1
    rec = hits[0]
    assert rec["event_type"] == "RULE_ENGINE_HIT"
    assert rec["rule_id"] == "R-001"
    assert rec["severity"] == "hard_block"


def test_hit_sink_exception_does_not_break_evaluate() -> None:
    def _boom(_rec) -> None:
        raise RuntimeError("log down")

    eng = ComplianceRuleEngine(hit_sink=_boom)
    eng.load_rule_pack([_rule()])
    v = eng.evaluate_pre_trade({"qty": 150})
    assert v.disposition is ComplianceDisposition.HARD_BLOCK


def test_only_active_version_evaluated() -> None:
    mgr = RuleVersionManager()
    r1 = RuleDslParser.parse(_rule(version="v1", condition={"field": "qty", "op": ">", "value": 100}))
    r2 = RuleDslParser.parse(_rule(version="v2", condition={"field": "qty", "op": ">", "value": 200}))
    mgr.register(r1)
    mgr.register(r2)
    mgr.activate("R-001", "v1")
    eng = ComplianceRuleEngine(manager=mgr)
    assert eng.evaluate_pre_trade({"qty": 150}).disposition is ComplianceDisposition.HARD_BLOCK
    mgr.activate("R-001", "v2")
    assert eng.evaluate_pre_trade({"qty": 150}).disposition is ComplianceDisposition.PASS


# ── 盘后批量审计器 ───────────────────────────────────────────────────────────


def test_batch_audit_summary() -> None:
    eng = _engine(
        _rule("R-H", "v1", "hard_block", {"field": "qty", "op": ">", "value": 100}),
        _rule("R-W", "v1", "warning", {"field": "flag", "op": "==", "value": True}),
    )
    report = eng.evaluate_batch([{"qty": 150, "flag": False}, {"qty": 50, "flag": True}, {"qty": 50, "flag": False}])
    assert report.total == 3
    assert report.hard_block == 1
    assert report.warning == 1
    assert report.passed == 1
    assert len(report.verdicts) == 3


# ── 收编规则包 ───────────────────────────────────────────────────────────────


def test_trading_compliance_rule_pack_loadable() -> None:
    pack = trading_compliance_rule_pack()
    assert len(pack) >= 2
    eng = _engine(*pack)
    # 自成交零容忍（收编 WASH_TRADE）
    v = eng.evaluate_pre_trade({"buyer_account": "A1", "seller_account": "A1"})
    assert v.disposition is ComplianceDisposition.HARD_BLOCK
    v2 = eng.evaluate_pre_trade({"buyer_account": "A1", "seller_account": "B2", "order_qty": 10, "minute_avg_volume": 1000})
    assert v2.disposition is ComplianceDisposition.PASS


# ── frozen 不可变 ────────────────────────────────────────────────────────────


def test_rule_and_verdict_frozen() -> None:
    rule = RuleDslParser.parse(_rule())
    with pytest.raises(dataclasses.FrozenInstanceError):
        rule.severity = ComplianceDisposition.PASS  # type: ignore[misc]
    eng = _engine(_rule())
    v: ComplianceVerdict = eng.evaluate_pre_trade({"qty": 150})
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.disposition = ComplianceDisposition.PASS  # type: ignore[misc]
    assert isinstance(v.hits, tuple)
    assert isinstance(v.hits[0], RuleHit)
