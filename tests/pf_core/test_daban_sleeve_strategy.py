# [A_test] module_id: MOD-GOV_daban_sleeve_strategy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_daban_sleeve_strategy
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_daban_sleeve_strategy.py
# [TTL] task_bound
"""打板 sleeve 组装策略测试（CAND-SIG-012 晋升，P0-4① 施工）。

覆盖：
- 空 universe/空 signals → 空 dict（ERROR_CONTRACT 不抛异常）
- 权重和 ≤ 1.0 不变量（fake 四引擎隔离，不打网络/DB）
- 6 类决策优先级映射（"中性"剔除、"回避"资格门剔除、融合降级剔除）
- StrategyRegistry 注册幂等（重复 import 不 raise；重复 register 同 id 必 raise）
- select() 返回 SelectionResult 且 urgency=immediate（21 号 L255-259 映射）
- 真实四引擎冒烟（默认构造，纯计算路径不变量断言）
"""

from __future__ import annotations

import importlib
from datetime import date
from types import SimpleNamespace

import pytest

from zephyr.governance.strategies.strategy_base import StrategyRegistry
from zephyr.pf_core.strategies import DabanSleeveStrategy
from zephyr.shared.contracts.selection_result import SelectionResult, SignalInput

# ── fake 四引擎（依赖注入隔离底层组件，不打网络/DB）──


class _FakeSelector:
    """BM-SEL-22 资格门 fake：推荐/回避由构造参数控制。"""

    def __init__(self, recommendation: str = "推荐", degraded: bool = False) -> None:
        self._recommendation = recommendation
        self._degraded = degraded

    def analyze(self, input_data):
        return SimpleNamespace(is_degraded=self._degraded, recommendation=self._recommendation)


class _FakeYouzi:
    def analyze(self, input_data):
        return SimpleNamespace(total_score=80.0, emotion_phase="主升", is_degraded=False)


class _FakeQuant:
    def analyze(self, input_data):
        return SimpleNamespace(total_score=75.0, is_degraded=False)


class _FakeFusion:
    """BM-SEL-25 融合 fake：decision/fused_score 按 symbol 查表。"""

    def __init__(self, table: dict[str, tuple[str, float]] | None = None, degraded: bool = False) -> None:
        # table: {youzi_score 透传键不适用——按调用次序太脆，故 fake 用固定决策表 keyed by 连板数}
        self._table = table or {}
        self._degraded = degraded

    def analyze(self, input_data):
        key = input_data.consecutive_limit_ups  # fusion_context 透传的连板数当查表键
        decision, fused = self._table.get(key, ("主升龙头", 90.0))
        return SimpleNamespace(is_degraded=self._degraded, decision=decision, fused_score=fused)


def _make_strategy(fusion_table=None, selector_recommendation="推荐", fusion_degraded=False):
    return DabanSleeveStrategy(
        selector=_FakeSelector(selector_recommendation),
        youzi_engine=_FakeYouzi(),
        quant_engine=_FakeQuant(),
        fusion_engine=_FakeFusion(fusion_table, degraded=fusion_degraded),
    )


def _payload(consecutive: int) -> dict:
    """最小合法负载：selector/youzi/quant 子 dict + fusion_context 连板数。"""
    return {
        "selector": {"current_price": 10.0, "target_price": 12.0},
        "youzi": {"consecutive_limit_ups": consecutive},
        "quant": {"momentum_z_score": 1.5},
        "fusion_context": {"consecutive_limit_ups": consecutive},
    }


def test_empty_universe_returns_empty_dict():
    s = _make_strategy()
    assert s.generate_target_weights(universe=[], signals={"600519": _payload(2)}) == {}
    assert s.generate_target_weights(universe=None, signals=None) == {}


def test_empty_signals_returns_empty_dict():
    s = _make_strategy()
    assert s.generate_target_weights(universe=["600519"], signals={}) == {}
    assert s.generate_target_weights(universe=["600519"], signals=None) == {}


def test_weight_sum_invariant_leq_one():
    """多标的评分比例归一化 + max_single 截顶后，权重和 ≤ 1.0。"""
    s = _make_strategy(
        fusion_table={3: ("主升龙头", 90.0), 2: ("二进三", 80.0), 1: ("跟风", 70.0)},
    )
    universe = ["600001", "600002", "600003"]
    signals = {"600001": _payload(3), "600002": _payload(2), "600003": _payload(1)}
    weights = s.generate_target_weights(universe, signals, {"top_n": 10, "max_single": 0.15})
    assert weights, "有效评分应产出非空权重"
    assert set(weights) <= set(universe)
    assert sum(weights.values()) <= 1.0 + 1e-9
    assert all(w <= 0.15 + 1e-9 for w in weights.values())
    # 主升龙头(90×1.0) > 二进三(80×0.85) > 跟风(70×0.65)：截顶后次序保持
    assert weights["600001"] >= weights["600003"]


def test_neutral_decision_excluded():
    """6 类决策外"中性"→ 优先级 0 剔除；全中性 → 空 dict。"""
    s = _make_strategy(fusion_table={2: ("中性", 85.0)})
    weights = s.generate_target_weights(["600001"], {"600001": _payload(2)})
    assert weights == {}


def test_selector_reject_gate():
    """BM-SEL-22 资格门：推荐"回避"→ 剔除。"""
    s = _make_strategy(selector_recommendation="回避")
    weights = s.generate_target_weights(["600001"], {"600001": _payload(2)})
    assert weights == {}


def test_fusion_degraded_excluded():
    """融合降级（含上游降级传播）→ 剔除。"""
    s = _make_strategy(fusion_degraded=True)
    weights = s.generate_target_weights(["600001"], {"600001": _payload(2)})
    assert weights == {}


def test_registry_registration_idempotent():
    """注册幂等：重复 import 不 raise（模块缓存）；显式重复 register 同 id 必 raise。"""
    mod1 = importlib.import_module("zephyr.pf_core.strategies.daban_sleeve_strategy")
    mod2 = importlib.import_module("zephyr.pf_core.strategies.daban_sleeve_strategy")
    assert mod1 is mod2  # import 只发生一次，装饰器不重跑

    import zephyr.pf_core.strategies as pkg

    assert pkg.DabanSleeveStrategy is mod1.DabanSleeveStrategy  # lazy getattr 走 globals 缓存

    if StrategyRegistry.get("daban-sleeve") is None:
        StrategyRegistry.register(mod1.DabanSleeveStrategy)
    with pytest.raises(ValueError, match="already registered"):
        StrategyRegistry.register(mod1.DabanSleeveStrategy)


def test_select_returns_selection_result_with_immediate_urgency():
    """select() → SelectionResult，urgency=immediate（打板映射，21 号 L257）。"""
    s = _make_strategy(fusion_table={2: ("二进三", 80.0)})
    si = SignalInput(
        as_of_date=date(2026, 8, 21),
        universe=["600001"],
        regime_budget=0.6,
        signals=[{"symbol": "600001", **_payload(2)}],
    )
    res = s.select(si)
    assert isinstance(res, SelectionResult)
    assert len(res.target_portfolio) == 1
    tp = res.target_portfolio[0]
    assert tp.symbol == "600001"
    assert tp.urgency == "immediate"
    assert tp.signal_source == "daban-sleeve"
    assert 0.0 <= res.confidence <= 1.0
    assert res.signals == si.signals  # 原始信号留痕


def test_select_empty_universe_returns_empty_result():
    s = _make_strategy()
    res = s.select(SignalInput(as_of_date=date(2026, 8, 21), universe=[], regime_budget=0.5))
    assert isinstance(res, SelectionResult)
    assert res.target_portfolio == []
    assert res.confidence == 0.0


def test_real_engines_smoke_invariants():
    """真实四引擎冒烟（纯计算，无网络/DB）：输出合法 dict、权重和 ≤1.0、键 ⊆ universe。"""
    s = DabanSleeveStrategy()  # 默认构造=真实四引擎（production 组件）
    payload = {
        "selector": {"current_price": 10.0, "target_price": 12.0, "consecutive_limit_ups": 2},
        "youzi": {
            "consecutive_limit_ups": 2,
            "seal_amount": 5e8,
            "float_market_cap": 3e9,
            "open_board_count": 0,
            "auction_rise_pct": 5.0,
            "auction_volume_ratio": 2.5,
            "sector_limit_up_count": 8,
            "market_limit_up_count": 60,
            "market_breadth_ratio": 0.7,
        },
        "quant": {
            "momentum_z_score": 2.0,
            "sector_change_pct": 3.0,
            "stock_change_pct": 10.0,
            "market_change_pct": 1.0,
            "capital_inflow": 2e8,
            "float_market_cap": 3e9,
            "technical_score": 80.0,
            "risk_score": 20.0,
            "youzi_emotion_score": 80.0,
            "consecutive_limit_ups": 2,
            "is_main_line": True,
        },
        "fusion_context": {"consecutive_limit_ups": 2, "is_main_line": True, "stock_change_pct": 10.0},
    }
    weights = s.generate_target_weights(["600001"], {"600001": payload})
    assert isinstance(weights, dict)
    assert set(weights) <= {"600001"}
    assert sum(weights.values()) <= 1.0 + 1e-9
