# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.3
# [TTL] permanent
"""信号冲突消解器（MOD-SIG-010）单元测试——规则链 R1-R5/分组/留痕/非法输入。"""

from __future__ import annotations

import pytest

from zephyr.signal_fundamental.router.signal_conflict_resolver import (
    ConflictResolverConfig,
    ConflictSignal,
    ResolutionAction,
    resolve_conflicts,
)


def _sig(sid: str, symbol: str = "X", **kw) -> ConflictSignal:
    return ConflictSignal(signal_id=sid, symbol=symbol, **kw)


class TestNoConflict:
    def test_single_long_adopt(self):
        out = resolve_conflicts([_sig("a", direction="LONG", confidence=0.7)])
        assert out[0].action == ResolutionAction.ADOPT
        assert out[0].rule_applied == "no_conflict"
        assert out[0].winner_id == "a"
        assert out[0].loser_ids == ()

    def test_single_exit_reject(self):
        """纯 EXIT 组 → REJECT（剔除/不买入，非做空）。"""
        out = resolve_conflicts([_sig("a", direction="EXIT", confidence=0.7)])
        assert out[0].action == ResolutionAction.REJECT

    def test_same_direction_group_no_conflict(self):
        out = resolve_conflicts(
            [
                _sig("a", direction="LONG", confidence=0.6),
                _sig("b", direction="LONG", confidence=0.9),
            ]
        )
        assert out[0].action == ResolutionAction.ADOPT
        assert out[0].winner_id == "b"  # 置信度最高者为代表
        assert out[0].loser_ids == ("a",)


class TestRuleChain:
    def test_r1_risk_veto_overrides_strong_long(self):
        """风险否决绝对优先：LONG 满置信也不敌 RISK 高置信。"""
        out = resolve_conflicts(
            [
                _sig("buy", direction="LONG", kind="OPPORTUNITY", confidence=1.0),
                _sig("risk", direction="EXIT", kind="RISK", confidence=0.85),
            ]
        )
        r = out[0]
        assert r.action == ResolutionAction.REJECT
        assert r.rule_applied == "R1_risk_veto"
        assert r.winner_id == "risk"
        assert r.loser_ids == ("buy",)

    def test_r1_not_triggered_below_veto_threshold(self):
        """RISK 置信度低于否决线 → 落入 R2。"""
        out = resolve_conflicts(
            [
                _sig("buy", direction="LONG", kind="OPPORTUNITY", confidence=0.9),
                _sig("risk", direction="EXIT", kind="RISK", confidence=0.5),
            ]
        )
        assert out[0].rule_applied == "R2_confidence"
        assert out[0].action == ResolutionAction.ADOPT

    def test_r2_confidence_margin(self):
        out = resolve_conflicts(
            [
                _sig("buy", direction="LONG", confidence=0.9),
                _sig("sell", direction="EXIT", confidence=0.6),
            ]
        )
        assert out[0].rule_applied == "R2_confidence"
        assert out[0].action == ResolutionAction.ADOPT
        out2 = resolve_conflicts(
            [
                _sig("buy", direction="LONG", confidence=0.5),
                _sig("sell", direction="EXIT", confidence=0.9),
            ]
        )
        assert out2[0].action == ResolutionAction.REJECT

    def test_r3_recency_when_confidence_close(self):
        out = resolve_conflicts(
            [
                _sig("old", direction="LONG", confidence=0.70, created_seq=1),
                _sig("new", direction="EXIT", confidence=0.65, created_seq=9),
            ]
        )
        r = out[0]
        assert r.rule_applied == "R3_recency"
        assert r.action == ResolutionAction.REJECT  # 新者（EXIT）胜

    def test_r4_source_priority(self):
        cfg = ConflictResolverConfig(source_priority={"engine_a": 10, "engine_b": 1})
        out = resolve_conflicts(
            [
                _sig("buy", direction="LONG", confidence=0.7, created_seq=1, source="engine_a"),
                _sig("sell", direction="EXIT", confidence=0.7, created_seq=1, source="engine_b"),
            ],
            config=cfg,
        )
        assert out[0].rule_applied == "R4_source"
        assert out[0].action == ResolutionAction.ADOPT

    def test_r5_defer_on_full_tie(self):
        out = resolve_conflicts(
            [
                _sig("buy", direction="LONG", confidence=0.7, created_seq=1, source="s"),
                _sig("sell", direction="EXIT", confidence=0.7, created_seq=1, source="s"),
            ]
        )
        r = out[0]
        assert r.action == ResolutionAction.DEFER
        assert r.rule_applied == "R5_defer"
        assert r.winner_id == ""
        assert set(r.loser_ids) == {"buy", "sell"}


class TestBatchAndValidation:
    def test_grouped_by_symbol_sorted(self):
        out = resolve_conflicts(
            [
                _sig("b1", symbol="B", direction="LONG"),
                _sig("a1", symbol="A", direction="EXIT"),
            ]
        )
        assert [r.symbol for r in out] == ["A", "B"]

    def test_invalid_confidence_raises(self):
        with pytest.raises(ValueError):
            resolve_conflicts([_sig("x", confidence=2.0)])

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError):
            resolve_conflicts([_sig("x", direction="SHORT")])  # A 股无做空

    def test_empty(self):
        assert resolve_conflicts([]) == []
