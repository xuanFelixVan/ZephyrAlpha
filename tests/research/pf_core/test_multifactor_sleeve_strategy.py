# [A_test] module_id: MOD-GOV_multifactor_sleeve_strategy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_multifactor_sleeve_strategy
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_multifactor_sleeve_strategy.py
# [TTL] task_bound
"""多因子 sleeve 组装策略测试（CAND-SIG-012 晋升，P0-4① 施工）。

覆盖：
- 空 universe/空 signals → 空 dict（ERROR_CONTRACT 不抛异常）
- 等权/IC 加权两合成路径（真实 multifactor_synthesis，纯 pandas 无 DB）
- 权重和 ≤ 1.0 不变量 + 横截面 top-N 归一化
- ic_ir_calc 经 monkeypatch 隔离（compute_ic_weights 薄封装，不打网络/DB）
- StrategyRegistry 注册幂等
- select() 返回 SelectionResult 且 urgency=gradual（21 号 L255-259 映射）
"""

from __future__ import annotations

import importlib
from datetime import date

import pytest

pd = pytest.importorskip("pandas")

from zephyr.governance.strategies.strategy_base import StrategyRegistry  # noqa: E402
from zephyr.pf_core.strategies import MultifactorSleeveStrategy  # noqa: E402
from zephyr.pf_core.strategies import multifactor_sleeve_strategy as sleeve_mod  # noqa: E402
from zephyr.shared.contracts.selection_result import SelectionResult, SignalInput  # noqa: E402


def _signals() -> dict[str, dict[str, float]]:
    """三标的 × 两因子截面负载（f1/f2 排名一致：600001 最强）。"""
    return {
        "600001": {"f1": 3.0, "f2": 1.0},
        "600002": {"f1": 2.0, "f2": 0.5},
        "600003": {"f1": 1.0, "f2": -0.5},
    }


def test_empty_universe_returns_empty_dict():
    s = MultifactorSleeveStrategy()
    assert s.generate_target_weights(universe=[], signals=_signals()) == {}
    assert s.generate_target_weights(universe=None, signals=None) == {}


def test_empty_signals_returns_empty_dict():
    s = MultifactorSleeveStrategy()
    assert s.generate_target_weights(universe=["600001"], signals={}) == {}
    assert s.generate_target_weights(universe=["600001"], signals=None) == {}


def test_equal_weight_topn_normalized():
    """等权合成 → 截面降序 top-N 等权归一化，权重和 ≤1.0。"""
    s = MultifactorSleeveStrategy()
    weights = s.generate_target_weights(
        ["600001", "600002", "600003"],
        _signals(),
        {"method": "equal_weight", "top_n": 2, "max_single": 0.4},
    )
    assert list(weights) == ["600001", "600002"]  # 截面打分降序前 2
    assert weights["600001"] == pytest.approx(0.4)  # min(1/2, 0.4)
    assert sum(weights.values()) <= 1.0 + 1e-9


def test_ic_weighted_path():
    """IC 加权合成路径（ic_weights 经 constraints 注入）。"""
    s = MultifactorSleeveStrategy()
    # f2 权重为 0 → 退等权语义不走，f1 主导排序（600001 仍最强）
    weights = s.generate_target_weights(
        ["600001", "600002", "600003"],
        _signals(),
        {"method": "ic_weighted", "ic_weights": {"f1": 0.05, "f2": 0.01}, "top_n": 3},
    )
    assert set(weights) == {"600001", "600002", "600003"}
    assert sum(weights.values()) <= 1.0 + 1e-9
    # top_n=3 → min(1/3, 默认 max_single=0.10) = 0.10 等权截顶
    assert all(w == pytest.approx(0.10) for w in weights.values())


def test_all_nan_signals_returns_empty_dict():
    """截面全 NaN → 空 dict（ERROR_CONTRACT）。"""
    s = MultifactorSleeveStrategy()
    nan_signals = {"600001": {"f1": float("nan")}, "600002": {"f1": float("nan")}}
    assert s.generate_target_weights(["600001", "600002"], nan_signals) == {}


def test_compute_ic_weights_monkeypatched(monkeypatch):
    """compute_ic_weights 薄封装：ic_ir_calc 经 monkeypatch 隔离（不打数据层）。"""
    fake_table = pd.DataFrame(
        [
            {"factor_id": "f1", "ic_mean": 0.05, "ic_std": 0.02, "ir": 2.5},
            {"factor_id": "f2", "ic_mean": -0.01, "ic_std": 0.03, "ir": -0.3},
        ]
    )
    monkeypatch.setattr(sleeve_mod, "compute_ic_ir_table", lambda *a, **k: fake_table)
    weights = MultifactorSleeveStrategy.compute_ic_weights(["f1", "f2"], ["600001"], "2026-01-01", "2026-08-01")
    assert weights == {"f1": pytest.approx(0.05), "f2": pytest.approx(-0.01)}


def test_registry_registration_idempotent():
    """注册幂等：重复 import 不 raise；显式重复 register 同 id 必 raise。"""
    mod1 = importlib.import_module("zephyr.pf_core.strategies.multifactor_sleeve_strategy")
    mod2 = importlib.import_module("zephyr.pf_core.strategies.multifactor_sleeve_strategy")
    assert mod1 is mod2
    if StrategyRegistry.get("multifactor-sleeve") is None:
        StrategyRegistry.register(mod1.MultifactorSleeveStrategy)
    with pytest.raises(ValueError, match="already registered"):
        StrategyRegistry.register(mod1.MultifactorSleeveStrategy)


def test_select_returns_selection_result_with_gradual_urgency():
    """select() → SelectionResult，urgency=gradual（多因子映射，21 号 L259）。"""
    s = MultifactorSleeveStrategy()
    si = SignalInput(
        as_of_date=date(2026, 8, 21),
        universe=["600001", "600002"],
        regime_budget=0.5,
        signals=[
            {"symbol": "600001", "factors": {"f1": 3.0}},
            {"symbol": "600002", "factors": {"f1": 2.0}},
        ],
        metadata={"method": "equal_weight", "top_n": 1},
    )
    res = s.select(si)
    assert isinstance(res, SelectionResult)
    assert len(res.target_portfolio) == 1
    tp = res.target_portfolio[0]
    assert tp.symbol == "600001"
    assert tp.urgency == "gradual"
    assert tp.signal_source == "multifactor-sleeve"
    assert 0.0 <= res.confidence <= 1.0
