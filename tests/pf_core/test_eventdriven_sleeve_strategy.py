# [A_test] module_id: MOD-GOV_eventdriven_sleeve_strategy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_eventdriven_sleeve_strategy
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_eventdriven_sleeve_strategy.py
# [TTL] task_bound
"""事件驱动 sleeve 组装策略测试（CAND-SIG-012 晋升，P0-4① 施工）。

覆盖：
- 空 universe/空 signals → 空 dict（ERROR_CONTRACT 不抛异常）
- 真实 compute_event_score 单因子路径（纯函数无 DB）：利好入选/利空剔除/噪声不动作
- detect_anomaly 经 monkeypatch 隔离：负向异动剔除、契约违反剔除
- EventScoreError 契约违反 → 剔除+不整批抛异常
- 权重和 ≤ 1.0 不变量
- StrategyRegistry 注册幂等
- select() 返回 SelectionResult 且 urgency=next_open（21 号 L255-259 映射）
"""

from __future__ import annotations

import importlib
from datetime import date
from types import SimpleNamespace

import pytest

from zephyr.governance.strategies.strategy_base import StrategyRegistry
from zephyr.intelligence.event_score import EventScoreError
from zephyr.pf_core.strategies import EventDrivenSleeveStrategy
from zephyr.pf_core.strategies import event_driven_sleeve_strategy as sleeve_mod
from zephyr.shared.contracts.selection_result import SelectionResult, SignalInput


def _surprise_payload(direction: float, sentiment: float = 0.8) -> dict:
    """突发类利好/利空负载：score=1.5×direction×sentiment（单因子公式）。"""
    return {
        "event": {
            "class_": "surprise",
            "surprise_direction": direction,
            "sentiment_score": sentiment,
            "decay_stage_factor": 1.0,
            "extreme_reaction_modifier": 1.0,
        },
    }


def test_empty_universe_returns_empty_dict():
    s = EventDrivenSleeveStrategy()
    assert s.generate_target_weights(universe=[], signals={"600001": _surprise_payload(1)}) == {}
    assert s.generate_target_weights(universe=None, signals=None) == {}


def test_empty_signals_returns_empty_dict():
    s = EventDrivenSleeveStrategy()
    assert s.generate_target_weights(universe=["600001"], signals={}) == {}
    assert s.generate_target_weights(universe=["600001"], signals=None) == {}


def test_positive_event_selected_negative_excluded():
    """利好（score≥0.2）入选；利空（score<0，A股不能做空只能剔除）剔除。"""
    s = EventDrivenSleeveStrategy()
    signals = {"600001": _surprise_payload(1), "600002": _surprise_payload(-1)}
    weights = s.generate_target_weights(["600001", "600002"], signals)
    assert set(weights) == {"600001"}
    # 单标的评分归一化=1.0，受默认 max_single=0.10 截顶
    assert weights["600001"] == pytest.approx(0.10)
    assert sum(weights.values()) <= 1.0 + 1e-9


def test_noise_event_excluded():
    """|score|<0.2 噪声不动作（SIGNAL_NOISE_THRESHOLD 同源）。"""
    s = EventDrivenSleeveStrategy()
    # score = 1.5×1×0.1 = 0.15 < 0.2 → 剔除
    weights = s.generate_target_weights(["600001"], {"600001": _surprise_payload(1, sentiment=0.1)})
    assert weights == {}


def test_weight_sum_invariant_leq_one_with_max_single_cap():
    """多标的评分比例归一化 + max_single 截顶后，权重和 ≤ 1.0。"""
    s = EventDrivenSleeveStrategy()
    signals = {
        "600001": _surprise_payload(1, sentiment=0.9),
        "600002": _surprise_payload(1, sentiment=0.8),
        "600003": _surprise_payload(1, sentiment=0.7),
    }
    weights = s.generate_target_weights(["600001", "600002", "600003"], signals, {"top_n": 10, "max_single": 0.2})
    assert len(weights) == 3
    assert sum(weights.values()) <= 1.0 + 1e-9
    assert all(w <= 0.2 + 1e-9 for w in weights.values())


def test_negative_anomaly_excluded(monkeypatch):
    """盘中负向异动确认 → 剔除（detect_anomaly monkeypatch 隔离）。"""
    monkeypatch.setattr(
        sleeve_mod,
        "detect_anomaly",
        lambda *a, **k: SimpleNamespace(degraded=False, is_anomaly=True, anomaly_type="negative"),
    )
    s = EventDrivenSleeveStrategy()
    payload = {**_surprise_payload(1), "intraday_returns": [0.001] * 30, "benchmark_returns": [0.0] * 30}
    assert s.generate_target_weights(["600001"], {"600001": payload}) == {}


def test_anomaly_contract_violation_excluded(monkeypatch):
    """异动识别契约违反 → 剔除+告警（不整批抛异常）。"""

    def _raise(*a, **k):
        raise sleeve_mod.EventAnomalyError("非数值输入")

    monkeypatch.setattr(sleeve_mod, "detect_anomaly", _raise)
    s = EventDrivenSleeveStrategy()
    payload = {**_surprise_payload(1), "intraday_returns": ["bad"], "benchmark_returns": [0.0]}
    assert s.generate_target_weights(["600001"], {"600001": payload}) == {}


def test_event_score_contract_violation_excluded(monkeypatch):
    """EventScoreError 契约违反 → 剔除该标的，其余标的不受影响。"""
    real_compute = sleeve_mod.compute_event_score

    def _guarded(event, data=None):
        if event.symbol == "600001":
            raise EventScoreError("symbol 非法")
        return real_compute(event, data)

    monkeypatch.setattr(sleeve_mod, "compute_event_score", _guarded)
    s = EventDrivenSleeveStrategy()
    signals = {"600001": _surprise_payload(1), "600002": _surprise_payload(1)}
    weights = s.generate_target_weights(["600001", "600002"], signals)
    assert set(weights) == {"600002"}


def test_registry_registration_idempotent():
    """注册幂等：重复 import 不 raise；显式重复 register 同 id 必 raise。"""
    mod1 = importlib.import_module("zephyr.pf_core.strategies.event_driven_sleeve_strategy")
    mod2 = importlib.import_module("zephyr.pf_core.strategies.event_driven_sleeve_strategy")
    assert mod1 is mod2
    if StrategyRegistry.get("eventdriven-sleeve") is None:
        StrategyRegistry.register(mod1.EventDrivenSleeveStrategy)
    with pytest.raises(ValueError, match="already registered"):
        StrategyRegistry.register(mod1.EventDrivenSleeveStrategy)


def test_select_returns_selection_result_with_next_open_urgency():
    """select() → SelectionResult，urgency=next_open（事件驱动映射，21 号 L258）。"""
    s = EventDrivenSleeveStrategy()
    si = SignalInput(
        as_of_date=date(2026, 8, 21),
        universe=["600001"],
        regime_budget=0.4,
        signals=[{"symbol": "600001", **_surprise_payload(1)}],
    )
    res = s.select(si)
    assert isinstance(res, SelectionResult)
    assert len(res.target_portfolio) == 1
    tp = res.target_portfolio[0]
    assert tp.symbol == "600001"
    assert tp.urgency == "next_open"
    assert tp.signal_source == "eventdriven-sleeve"
    assert 0.0 <= res.confidence <= 1.0
    assert res.metadata["dependency_maturity"].startswith("event_score=design")
