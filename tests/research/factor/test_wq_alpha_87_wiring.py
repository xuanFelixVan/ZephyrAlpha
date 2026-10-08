# [A_test] module_id: MOD-L02-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.research.factor.test_wq_alpha_87_wiring
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;合成数据纯内存不触网不触库
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/research/factor/test_wq_alpha_87_wiring.py
# [A_module] module_id=MOD-L02-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WQ87 接线件测试（master_backlog P2-6，st-mx07-W6）。

覆盖：
- 注册册登记：wire_wq_alpha_87 幂等/87 全量/撞他类抛错/降级标注
- 调用链挂载：compute_factor_panel 经 compute_panel 分支与核直算逐位对拍
- 考试链端到端：evaluate_factor/compute_ic_ir_table 走 wq_alpha_* 出 IC（load_history 注入合成）
- ic_hook 委托：make_ic_ir_hook 与 metrics.compute_ic_series 同语义
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

backtest = pytest.importorskip("zephyr.factor.core.evaluation.backtest")
ic_ir_calc = pytest.importorskip("zephyr.factor.analysis.ic_ir_calc")
factor_base = pytest.importorskip("zephyr.factor.factor_base")
wiring = pytest.importorskip("zephyr.factor.wq_alpha_87_wiring")
core87 = pytest.importorskip("zephyr.factor.wq_alpha_87")

FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry
Alpha87Error = core87.Alpha87Error
WqAlpha87 = core87.WqAlpha87
Alpha87WiringError = wiring.Alpha87WiringError
WQ87_DOMAIN = wiring.WQ87_DOMAIN
compute_factor_panel = backtest.compute_factor_panel
evaluate_factor = backtest.evaluate_factor

_DATES = pd.bdate_range("2025-06-02", periods=300)
_SYMBOLS = [f"{i:06d}.SZ" for i in range(8)]


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _history(seed: int = 11) -> pd.DataFrame:
    """合成 load_history 形态长表：MultiIndex(symbol, trade_date)，含 amount/adj_factor。"""
    rng = np.random.default_rng(seed)
    n, m = len(_DATES), len(_SYMBOLS)
    close = pd.DataFrame(10 + rng.normal(0, 0.4, (n, m)).cumsum(axis=0), index=_DATES, columns=_SYMBOLS).clip(lower=1.0)
    open_ = close * (1 + rng.normal(0, 0.005, (n, m)))
    high = pd.DataFrame(np.maximum(open_.values, close.values), index=_DATES, columns=_SYMBOLS) * (
        1 + abs(rng.normal(0, 0.004, (n, m)))
    )
    low = pd.DataFrame(np.minimum(open_.values, close.values), index=_DATES, columns=_SYMBOLS) * (
        1 - abs(rng.normal(0, 0.004, (n, m)))
    )
    volume = pd.DataFrame(rng.integers(1_000_000, 9_000_000, (n, m)).astype(float), index=_DATES, columns=_SYMBOLS)
    amount = volume * close

    frames = {}
    for field, panel in (
        ("open", open_),
        ("high", high),
        ("low", low),
        ("close", close),
        ("volume", volume),
        ("amount", amount),
    ):
        long = panel.stack()
        long.index.names = ["trade_date", "symbol"]
        frames[field] = long
    out = pd.DataFrame(frames)
    out["adj_factor"] = 1.0
    return out.reorder_levels(["symbol", "trade_date"]).sort_index()


class TestWireRegistry:
    """注册册登记：幂等/87 全量/撞位抛错/降级标注。"""

    def test_wire_registers_87(self) -> None:
        assert wiring.wire_wq_alpha_87() == 87
        assert len(wiring.wired_factor_ids()) == 87
        assert wiring.wired_factor_ids()[0] == "wq_alpha_001"
        assert wiring.wired_factor_ids()[-1] == "wq_alpha_101"
        cls = FactorRegistry.get("wq_alpha_101")
        assert cls.meta.domain == WQ87_DOMAIN
        assert cls._wq_alpha_87_alpha_id == 101
        assert len(FactorRegistry.list_by_domain(WQ87_DOMAIN)) == 87

    def test_wire_idempotent(self) -> None:
        assert wiring.wire_wq_alpha_87() == 87
        assert wiring.wire_wq_alpha_87() == 0
        assert len(FactorRegistry.list_all()) == 87

    def test_collision_raises(self) -> None:
        class DecoyWqAlpha005(factor_base.FactorBase):
            meta = FactorMeta(factor_id="wq_alpha_005", name="decoy", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        FactorRegistry.register(DecoyWqAlpha005)
        with pytest.raises(Alpha87WiringError, match="wq_alpha_005"):
            wiring.wire_wq_alpha_87()

    def test_degraded_formula_tagged(self) -> None:
        wiring.wire_wq_alpha_87()
        degraded = FactorRegistry.get("wq_alpha_079")
        clean = FactorRegistry.get("wq_alpha_101")
        assert "ind-neutralize-degraded" in degraded.meta.tags
        assert "ind-neutralize-degraded" not in clean.meta.tags


class TestPanelBridge:
    """调用链挂载：panel 分支与核直算逐位对拍。"""

    def test_compute_factor_panel_parity_with_core(self) -> None:
        wiring.wire_wq_alpha_87()
        history = _history()
        cls = FactorRegistry.get("wq_alpha_101")
        via_chain = compute_factor_panel(cls, history)
        via_core = WqAlpha87().compute(101, wiring.history_to_panels(history))
        assert via_chain.shape == (len(_DATES), len(_SYMBOLS))
        pd.testing.assert_frame_equal(via_chain, via_core, check_exact=True)

    def test_history_to_panels_missing_column_raises(self) -> None:
        history = _history().drop(columns=["amount"])
        with pytest.raises(Alpha87WiringError, match="amount"):
            wiring.history_to_panels(history)

    def test_history_to_panels_missing_symbol_level_raises(self) -> None:
        flat = _history().reset_index(drop=True)
        with pytest.raises(Alpha87WiringError, match="symbol"):
            wiring.history_to_panels(flat)

    def test_single_symbol_compute_raises_honest(self) -> None:
        wiring.wire_wq_alpha_87()
        factor = FactorRegistry.get("wq_alpha_101")()
        single = _history().xs(_SYMBOLS[0], level="symbol")
        with pytest.raises(Alpha87Error, match="cross-sectional"):
            factor.compute(single)


class TestExamChain:
    """考试链端到端：evaluate_factor/compute_ic_ir_table 走 wq_alpha_*。"""

    def test_evaluate_factor_end_to_end(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wiring.wire_wq_alpha_87()
        monkeypatch.setattr(backtest, "load_history", lambda *a, **k: _history())
        result = evaluate_factor("wq_alpha_101", _SYMBOLS, "2025-06-02", "2026-08-01", horizon=5)
        assert result.factor_id == "wq_alpha_101"
        assert result.sample_size > 0
        assert np.isfinite(result.ic_mean)

    def test_unregistered_raises_keyerror(self) -> None:
        with pytest.raises(KeyError, match="wq_alpha_101"):
            evaluate_factor("wq_alpha_101", _SYMBOLS, "2025-06-02", "2026-08-01")

    def test_compute_ic_ir_table_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wiring.wire_wq_alpha_87()
        monkeypatch.setattr(backtest, "load_history", lambda *a, **k: _history())
        table = ic_ir_calc.compute_ic_ir_table(
            ["wq_alpha_101", "wq_alpha_012"], _SYMBOLS, "2025-06-02", "2026-08-01", horizon=5
        )
        assert list(table["factor_id"]) == ["wq_alpha_101", "wq_alpha_012"]
        assert (table["sample_size"] > 0).all()
        assert table["is_overfitted"].any() or (table["ic_mean"] != 0).any()


class TestICHook:
    """ic_hook 委托：make_ic_ir_hook 与 metrics.compute_ic_series 同语义。"""

    def test_hook_matches_metrics(self) -> None:
        from zephyr.factor.core.evaluation.metrics import compute_ic_series

        lib = WqAlpha87()
        panels = wiring.history_to_panels(_history())
        values = lib.compute(12, panels)
        close = panels["close"]
        ret_panel = close.shift(-5) / close - 1  # 同 _compute_forward_returns 语义
        hook = wiring.make_ic_ir_hook(ret_panel, horizon=5)
        out = hook("wq_alpha_012", values)
        ic = compute_ic_series(values, ret_panel, 5)
        assert out["factor_id"] == "wq_alpha_012"
        assert out["sample_size"] == len(ic)
        assert out["ic_mean"] == pytest.approx(float(ic.mean()))

    def test_validate_ic_with_real_hook(self) -> None:
        panels = wiring.history_to_panels(_history())
        ret_panel = panels["close"].pct_change().shift(-5)
        lib = WqAlpha87()
        out = lib.validate_ic(101, panels, wiring.make_ic_ir_hook(ret_panel, horizon=5))
        assert out["sample_size"] > 0
        assert np.isfinite(out["ic_mean"])

    def test_empty_intersection_zeros(self) -> None:
        panels = wiring.history_to_panels(_history())
        values = WqAlpha87().compute(101, panels)
        hook = wiring.make_ic_ir_hook(values.iloc[:0], horizon=5)  # 无交集日期
        out = hook("wq_alpha_101", values)
        assert out == {"factor_id": "wq_alpha_101", "ic_mean": 0.0, "ic_std": 0.0, "ir": 0.0, "sample_size": 0}
