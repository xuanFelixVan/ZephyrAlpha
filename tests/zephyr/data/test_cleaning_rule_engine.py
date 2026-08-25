# [BLUEPRINT] MOD-L00-004 | tests/zephyr/data/test_cleaning_rule_engine.py
# [MODULE] tests.zephyr.data.test_cleaning_rule_engine
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.cleaning_rule_engine; zephyr.data.quality_gate
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-004 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CleaningRuleEngine 单元测试——规则DSL+滚动分位阈值自进化+拦截报告（CAND-DAT-007 / B10-01347）。

覆盖：
    1. 规则 DSL 解析：合法 gt/lt/between/rolling_quantile 与非法 op 拒绝
    2. 固定阈值规则判定：flag 打标保留 / block 拦截剔除
    3. 滚动分位阈值：限幅内自动生效、超限挂起待人工、approve 通道生效
    4. run_quality_gate 集成：输出形态对齐 quality_gate（rows+stats）并给出拦截报告
"""

from __future__ import annotations

import pytest

from zephyr.data.cleaning_rule_engine import (
    CleaningRule,
    CleaningRuleEngine,
    CleaningRuleError,
    RollingQuantileThreshold,
    parse_rules,
    run_quality_gate,
)


# ── 1. DSL 解析 ──


class TestParseRules:
    def test_parse_fixed_rules(self):
        rules = parse_rules(
            [
                {"name": "close_cap", "field": "close", "op": "lt", "value": 10000, "action": "flag"},
                {"name": "ret_band", "field": "ret", "op": "between", "lower": -0.11, "upper": 0.11, "action": "block"},
            ]
        )
        assert [r.name for r in rules] == ["close_cap", "ret_band"]
        assert rules[0].action == "flag"
        assert rules[1].op == "between"

    def test_invalid_op_rejected(self):
        with pytest.raises(CleaningRuleError):
            parse_rules([{"name": "bad", "field": "x", "op": "regex", "value": 1}])

    def test_missing_field_rejected(self):
        with pytest.raises(CleaningRuleError):
            parse_rules([{"name": "bad", "op": "lt", "value": 1}])

    def test_parse_rolling_quantile_rule(self):
        rules = parse_rules(
            [
                {
                    "name": "vol_rq",
                    "field": "volume",
                    "op": "rolling_quantile",
                    "quantile": 0.9,
                    "window": 10,
                    "guard_lower": 0,
                    "guard_upper": 1000,
                    "seed": [10, 20, 30],
                    "action": "block",
                }
            ]
        )
        assert rules[0].op == "rolling_quantile"
        assert rules[0].quantile == 0.9


# ── 2. 固定阈值规则判定 ──


def _engine() -> CleaningRuleEngine:
    rules = parse_rules(
        [
            {"name": "close_cap", "field": "close", "op": "lt", "value": 100, "action": "flag"},
            {"name": "ret_band", "field": "ret", "op": "between", "lower": -0.1, "upper": 0.1, "action": "block"},
        ]
    )
    return CleaningRuleEngine(rules)


class TestFixedRuleEvaluation:
    def test_clean_row_passes(self):
        report = _engine().evaluate([{"close": 50, "ret": 0.01}])
        assert report.total == 1
        assert report.flagged == 0 and report.intercepted == 0

    def test_flag_action_marks_and_retains(self):
        rows = [{"close": 500, "ret": 0.01}]
        report = _engine().evaluate(rows)
        assert report.flagged == 1
        assert report.by_rule["close_cap"] == 1
        assert rows[0]["quality_flag"] == 0  # 打标但保留

    def test_block_action_intercepts(self):
        report = _engine().evaluate([{"close": 50, "ret": 0.5}])
        assert report.intercepted == 1
        assert report.by_rule["ret_band"] == 1

    def test_clean_rows_returns_only_unblocked(self):
        engine = _engine()
        rows = [
            {"close": 50, "ret": 0.01},   # clean
            {"close": 500, "ret": 0.01},  # flagged
            {"close": 50, "ret": 0.5},    # blocked
        ]
        clean = engine.clean_rows(rows)
        assert len(clean) == 2  # flagged 保留、blocked 剔除


# ── 3. 滚动分位阈值自进化 ──


def _rq() -> RollingQuantileThreshold:
    return RollingQuantileThreshold(
        quantile=0.5, window=4, guard_lower=5.0, guard_upper=50.0, seed=[10.0, 20.0]
    )


class TestRollingQuantileThreshold:
    def test_initial_threshold_from_seed(self):
        rq = _rq()
        assert rq.current == pytest.approx(15.0)

    def test_evolve_within_guardrails_adopted(self):
        rq = _rq()
        outcome = rq.observe([12.0, 18.0])
        assert outcome == "adopted"
        assert rq.pending is None
        assert rq.current == pytest.approx(15.0)

    def test_evolve_beyond_guardrail_pending(self):
        rq = _rq()
        outcome = rq.observe([1000.0, 2000.0])  # 候选分位数远超 guard_upper
        assert outcome == "pending_approval"
        assert rq.current == pytest.approx(15.0)  # 旧阈值保留
        assert rq.pending is not None and rq.pending > 50.0

    def test_approve_applies_pending(self):
        rq = _rq()
        rq.observe([1000.0, 2000.0])
        rq.approve()
        assert rq.pending is None
        assert rq.current > 50.0

    def test_violation_uses_current_threshold(self):
        rq = _rq()
        assert rq.is_violation(16.0) is True
        assert rq.is_violation(14.0) is False


# ── 引擎内滚动规则联动 ──


class TestEngineRollingRule:
    def test_observe_collects_pending_rules(self):
        rules = parse_rules(
            [
                {
                    "name": "vol_rq",
                    "field": "volume",
                    "op": "rolling_quantile",
                    "quantile": 0.5,
                    "window": 4,
                    "guard_lower": 5.0,
                    "guard_upper": 50.0,
                    "seed": [10.0, 20.0],
                    "action": "block",
                }
            ]
        )
        engine = CleaningRuleEngine(rules)
        assert engine.evaluate([{"volume": 14.0}]).intercepted == 0
        assert engine.evaluate([{"volume": 16.0}]).intercepted == 1
        pending = engine.observe("volume", [1000.0, 2000.0])
        assert pending == ["vol_rq"]
        # 挂起期间仍用旧阈值
        assert engine.evaluate([{"volume": 60.0}]).intercepted == 1
        engine.approve("vol_rq")
        assert engine.evaluate([{"volume": 60.0}]).intercepted == 0


# ── 4. run_quality_gate 集成 ──


class TestRunQualityGate:
    def test_output_shape_and_report(self):
        engine = _engine()
        rows = [
            {"close": 50, "ret": 0.01},
            {"close": 500, "ret": 0.01},
            {"close": 50, "ret": 0.5},
        ]
        clean, stats = run_quality_gate(engine, "kline_daily", rows)
        assert stats["table"] == "kline_daily"
        assert stats["total"] == 3
        assert stats["flagged"] == 1
        assert stats["intercepted"] == 1
        assert stats["by_rule"] == {"close_cap": 1, "ret_band": 1}
        assert len(clean) == 2
        assert any(r.get("quality_flag") == 0 for r in clean)  # 拦截报告含打标留痕

    def test_pending_approvals_surface_in_report(self):
        rules = parse_rules(
            [
                {
                    "name": "vol_rq",
                    "field": "volume",
                    "op": "rolling_quantile",
                    "quantile": 0.5,
                    "window": 4,
                    "guard_lower": 5.0,
                    "guard_upper": 50.0,
                    "seed": [10.0, 20.0],
                    "action": "block",
                }
            ]
        )
        engine = CleaningRuleEngine(rules)
        engine.observe("volume", [1000.0, 2000.0])
        _, stats = run_quality_gate(engine, "t", [{"volume": 14.0}])
        assert stats["pending_approvals"] == ["vol_rq"]
