# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.3
# [TTL] permanent
"""信号优先级路由器（MOD-SIG-009）单元测试——类别绝对优先/置信度/FIFO/确定性。"""

from __future__ import annotations

import pytest

from zephyr.signal_fundamental.router.signal_priority_router import (
    RoutableSignal,
    SignalKind,
    priority_score,
    route_signals,
    PriorityRouterConfig,
)


def _sig(sid: str, **kw) -> RoutableSignal:
    return RoutableSignal(signal_id=sid, symbol=kw.pop("symbol", "X"), **kw)


class TestPriorityScore:
    def test_risk_always_before_opportunity(self):
        """风险类 0 置信度仍先于机会类满置信度（类别间隔 ≫ 置信度量程）。"""
        cfg = PriorityRouterConfig()
        risk = priority_score(_sig("r", kind="RISK", confidence=0.0), cfg=cfg)
        opp = priority_score(_sig("o", kind="OPPORTUNITY", confidence=1.0), cfg=cfg)
        assert risk > opp

    def test_confidence_within_kind(self):
        cfg = PriorityRouterConfig()
        hi = priority_score(_sig("a", kind="OPPORTUNITY", confidence=0.9), cfg=cfg)
        lo = priority_score(_sig("b", kind="OPPORTUNITY", confidence=0.1), cfg=cfg)
        assert hi > lo

    def test_invalid_confidence_raises(self):
        with pytest.raises(ValueError):
            priority_score(_sig("x", confidence=1.5), cfg=PriorityRouterConfig())

    def test_unknown_kind_raises(self):
        with pytest.raises(ValueError):
            priority_score(_sig("x", kind="UNKNOWN"), cfg=PriorityRouterConfig())


class TestRouteSignals:
    def test_kind_ordering(self):
        signals = [
            _sig("meta", kind="META", confidence=1.0, created_seq=0),
            _sig("opp", kind="OPPORTUNITY", confidence=0.9, created_seq=1),
            _sig("risk", kind="RISK", confidence=0.1, created_seq=2),
        ]
        out = route_signals(signals)
        assert out.ordered == ("risk", "opp", "meta")

    def test_fifo_tiebreak(self):
        """同类别同置信度 → created_seq 升序（先到先处理）。"""
        signals = [
            _sig("late", kind="RISK", confidence=0.5, created_seq=9),
            _sig("early", kind="RISK", confidence=0.5, created_seq=1),
        ]
        out = route_signals(signals)
        assert out.ordered == ("early", "late")

    def test_full_deterministic(self):
        """同分同序 → signal_id 字典序兜底。"""
        signals = [_sig("b", created_seq=1), _sig("a", created_seq=1)]
        out = route_signals(signals)
        assert out.ordered == ("a", "b")

    def test_scores_recorded(self):
        out = route_signals([_sig("s", kind="RISK", confidence=0.5)])
        assert out.scores["s"] == pytest.approx(1000.0 + 50.0)

    def test_empty(self):
        assert route_signals([]).ordered == ()

    def test_enum_kind_accepted(self):
        out = route_signals([_sig("e", kind=SignalKind.META.value)])
        assert out.ordered == ("e",)
