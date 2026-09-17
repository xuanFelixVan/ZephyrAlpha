# [BLUEPRINT] MOD-BT-001 | tests/metamorphic/test_s12_metamorphic_invariants.py
# [MODULE] tests.metamorphic.test_s12_metamorphic_invariants
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.core.portfolio
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] S12-E1 metamorphic 增补三不变式（真源 docs/_working/kimi_audit/S12_实验规格.md §E1）：
#   INV-5 成本单调性——同一 run 佣金/滑点 ×2 → 净值逐日不增且收益差 ≈ 成本差（±5% 容差）；
#   INV-6 账本闭合——引擎真跑后 reconcile_cash_ledger 残差 ≤0.01 且 within_tolerance=True
#         （H3/H4 链测试提升为不变式层；CLI 路径接线=E2，本文件钉 helper 层）；
#   INV-7 市值恒等——逐日 nav == cash + Σ qty×price（缺价结转最后已知价时也成立）。
#   每条带注入反例（成本倒挂/双计佣金/缺价 NaN）——反例必须让对应断言真的变红。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/metamorphic/test_s12_metamorphic_invariants.py
# [TTL] permanent
"""S12-E1 metamorphic 增补三不变式（合成数据，不触库不触网）。

被测真源（2026-09-17 工作区）：
- DefaultBacktestEngine.run  src/zephyr/backtest/implementations/vectorized_engine.py
- Portfolio.update_market_value / cash_history / trades_log
  src/zephyr/backtest/core/portfolio.py
- reconcile_cash_ledger      src/zephyr/backtest/core/portfolio.py:386（H4-A 真源）
- CLI 接线 helper            scripts/run_backtest.py::_cash_ledger_reconciliation（E2 落地件）
"""

from __future__ import annotations

import random
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.backtest.core.portfolio import Portfolio, reconcile_cash_ledger
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

_N_DAYS = 42
_SYMBOLS = ("SYM_A", "SYM_B", "SYM_C")
# INV-5 收益差≈成本差容差（规格写死 ±5%）
_COST_DIFF_TOL = 0.05
# INV-5 逐日不增容差（Decimal→float 转换噪声界，实测 <<1e-9）
_MONO_TOL = 1e-6

_BASE_COMMISSION = Decimal("0.0000854")  # 万0.854（matching_logic 同口径）
_BASE_SLIPPAGE = Decimal("1")  # 1bp 平口径


def _make_market(seed: int = 7) -> pd.DataFrame:
    """合成 flat 行情（0.25 网格随机游走，二进制精确表示）。"""
    rng = random.Random(seed)
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    rows = []
    for si, symbol in enumerate(_SYMBOLS):
        quarters = 40 + 8 * si
        for d in dates:
            quarters = max(8, quarters + rng.choice((-2, -1, -1, 0, 1, 1, 2)))
            rows.append({"date": d, "symbol": symbol, "close": quarters * 0.25})
    return pd.DataFrame(rows)


def _make_signals(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """每 7 日切换目标权重（含清仓腿），制造多次调仓。"""
    regimes = ([0.6, 0.4, 0.0], [0.1, 0.3, 0.6], [0.0, 0.5, 0.5])
    rows = {}
    for i, d in enumerate(dates):
        rows[d] = regimes[(i // 7) % len(regimes)]
    return pd.DataFrame.from_dict(rows, orient="index", columns=list(_SYMBOLS))


def _run(data, signals, capital: Decimal, *, cost_mult: float = 1):
    """成本多倍率引擎跑批。cost_mult=2 → 佣金/滑点 ×2（INV-5 处理臂）；0=零成本基准臂。"""
    cfg = BacktestConfig(
        initial_capital=capital,
        enable_pit_universe_filter=False,
        commission_rate=_BASE_COMMISSION * cost_mult,
        slippage_bps=_BASE_SLIPPAGE * cost_mult,
    )
    engine = DefaultBacktestEngine(config=cfg, enable_stk_limit_provider=False)
    result = engine.run(data=data, signals=signals, strategy_name="s12-meta")
    return result, engine.last_portfolio


def _assert_nav_not_increasing(nav_base: pd.Series, nav_dear: pd.Series, tol: float = _MONO_TOL) -> None:
    """INV-5 判定器：成本加倍臂 NAV 逐日不增（相对容差）。"""
    assert len(nav_base) == len(nav_dear)
    for (d0, v0), (d1, v1) in zip(nav_base.items(), nav_dear.items()):
        assert float(v1) <= float(v0) * (1 + tol), f"成本倒挂@{d0}: base={v0} dear={v1}"


def _ledger_view(portfolio):
    """从 Portfolio 取 reconcile 三件套（cash_history/trades_log/initial_capital）。"""
    return portfolio.cash_history, portfolio.trades_log, portfolio.initial_capital


def _assert_market_identity(records: list[dict]) -> None:
    """INV-7 判定器：逐日 nav == cash + Σ qty×price（缺价结转最后已知价口径）。

    容差 1e-9（相对）：nav_series 落 float（portfolio.py:306 float(nav)），
    Decimal 恒等经 float 往返引入 ≤1e-10 相对噪声；断裂判据=超此界（反例差 1 元
    相对 1e7 净值 = 1e-7，远在界外）。
    """
    assert records, "空快照=没跑起来"
    for rec in records:
        mv = sum(qty * rec["last_prices"].get(sym, Decimal("0")) for sym, qty in rec["qty"].items())
        expect = rec["cash"] + mv
        tol = max(abs(expect) * Decimal("1e-9"), Decimal("1e-6"))
        assert abs(rec["nav"] - expect) <= tol, (
            f"市值恒等断裂@{rec['date']}: nav={rec['nav']} cash={rec['cash']} mv={mv}"
        )


# ── INV-5：成本单调性 ─────────────────────────────────────────────────────────


def test_inv5_cost_doubling_nav_monotone_and_diff_tracks_cost():
    """同一 run 佣金/滑点 ×2 → NAV 逐日不增，且收益差 ≈ 成本差（±5% 容差）。

    大资金（1e8）压整手粒度噪声，避免 affordability 翻转引入非线性。
    成本差口径=**零成本臂实测摩擦层**：摩擦对费率线性（佣金∝rate、滑点∝bps），
    故 ×2 臂新增成本 ≈ 基准臂摩擦层 = pnl(零成本) − pnl(基准)。冲击成本腿
    （Almgren-Chriss 标定件）不随费率缩放、两臂相同，在差值中抵消。
    """
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))
    capital = Decimal("100000000")

    zero_result, zero_pf = _run(data, signals, capital, cost_mult=0)
    base_result, base_pf = _run(data, signals, capital, cost_mult=1)
    dear_result, dear_pf = _run(data, signals, capital, cost_mult=2)
    assert base_result.trades_count > 0  # sanity：非空跑
    assert dear_result.trades_count == base_result.trades_count  # 同成交笔数（无 affordability 翻转）

    _assert_nav_not_increasing(base_pf.nav_series, dear_pf.nav_series)
    _assert_nav_not_increasing(zero_pf.nav_series, base_pf.nav_series)

    pnl_zero = float(zero_pf.nav_series.iloc[-1]) - float(capital)
    pnl_base = float(base_pf.nav_series.iloc[-1]) - float(capital)
    pnl_dear = float(dear_pf.nav_series.iloc[-1]) - float(capital)
    friction_layer = pnl_zero - pnl_base  # 基准臂实际摩擦（零成本臂实测）
    assert friction_layer > 0  # 基准线有效性：摩擦非零（防"恒等满足一切"假通过）
    ret_diff = pnl_base - pnl_dear
    assert ret_diff == pytest.approx(friction_layer, rel=_COST_DIFF_TOL), (
        f"收益差 {ret_diff:.2f} 与成本差 {friction_layer:.2f} 偏离超 ±5%"
    )


def test_inv5_counterexample_inverted_cost_curve_detected():
    """注入反例（成本倒挂）：构造"成本高 NAV 反而高"的曲线 → 判定器必须红。

    防假绿钉扎：若 _assert_nav_not_increasing 对倒挂曲线不报错，本测试失败=
    INV-5 判定器本身失效。
    """
    idx = pd.bdate_range("2026-01-05", periods=5)
    nav_base = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0], index=idx)
    nav_inverted = pd.Series([100.0, 101.5, 102.5, 103.5, 104.5], index=idx)  # 倒挂
    with pytest.raises(AssertionError, match="成本倒挂"):
        _assert_nav_not_increasing(nav_base, nav_inverted)


# ── INV-6：账本闭合（引擎层不变式化；CLI 接线钉 E2 helper） ───────────────────


def test_inv6_engine_run_ledger_closes():
    """引擎真跑（含佣金/滑点）后 reconcile_cash_ledger 残差 ≤0.01 且 within_tolerance。

    把 H3/H4 的链测试锁提升为 metamorphic 不变式层：任何引擎改动破账本恒等式，
    本件当天红。
    """
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))
    result, pf = _run(data, signals, Decimal("10000000"), cost_mult=1)
    assert result.trades_count > 0

    cash_history, trades_log, initial_capital = _ledger_view(pf)
    recon = reconcile_cash_ledger(cash_history, trades_log, initial_capital)
    assert recon["samples"] > 0
    assert recon["within_tolerance"] is True, (
        f"账本不闭合: max_abs_residual={recon['max_abs_residual']} worst={recon['worst_date']}"
    )
    assert float(recon["max_abs_residual"]) <= 0.01


def test_inv6_counterexample_dropped_trade_detected():
    """注入反例（漏记成交）：从流水删一笔 → within_tolerance 必须翻 False。"""
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))
    _, pf = _run(data, signals, Decimal("10000000"), cost_mult=1)
    cash_history, trades_log, initial_capital = _ledger_view(pf)
    assert len(trades_log) >= 2

    tampered = trades_log[:-1]  # 删掉最后一笔成交（现金快照里它已生效）
    recon = reconcile_cash_ledger(cash_history, tampered, initial_capital)
    assert recon["within_tolerance"] is False, "删一笔成交后对账仍闭合=对账器假绿"


def test_inv6_counterexample_double_counted_commission_detected():
    """注入反例（双计佣金）：流水 total_cost 加倍 → 重算现金与快照错位 → 必须红。"""
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))
    _, pf = _run(data, signals, Decimal("10000000"), cost_mult=1)
    cash_history, trades_log, initial_capital = _ledger_view(pf)

    tampered = [dict(t) for t in trades_log]
    tampered[0]["total_cost"] = float(tampered[0]["total_cost"]) * 2  # 双计首笔
    recon = reconcile_cash_ledger(cash_history, tampered, initial_capital)
    assert recon["within_tolerance"] is False, "双计佣金后对账仍闭合=对账器假绿"


def test_inv6_cli_wiring_helper_fail_closed_and_close():
    """E2 接线钉：scripts/run_backtest.py::_cash_ledger_reconciliation。

    ① 正常账本 → within_tolerance=True；② 缺 cash_history → fail-closed False；
    ③ 缺引擎（None）→ False。不触 CH（helper 层纯函数）。
    """
    import importlib.util
    from pathlib import Path
    from types import SimpleNamespace

    path = Path(__file__).resolve().parents[2] / "scripts" / "run_backtest.py"
    spec = importlib.util.spec_from_file_location("run_backtest_under_test_s12", path)
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)

    d1 = pd.Timestamp("2026-01-05")
    good_pf = SimpleNamespace(
        cash_history=[(None, Decimal("100000")), (d1, Decimal("89995"))],
        trades_log=[{"date": d1, "side": "BUY", "total_cost": 10005.0}],
        initial_capital=Decimal("100000"),
    )
    recon = rb._cash_ledger_reconciliation(SimpleNamespace(last_portfolio=good_pf))
    assert recon["within_tolerance"] is True

    no_cash_pf = SimpleNamespace(cash_history=[], trades_log=[], initial_capital=Decimal("100000"))
    assert rb._cash_ledger_reconciliation(SimpleNamespace(last_portfolio=no_cash_pf))[
        "within_tolerance"
    ] is False
    assert rb._cash_ledger_reconciliation(None)["within_tolerance"] is False


# ── INV-7：市值恒等（含缺价结转） ─────────────────────────────────────────────


def test_inv7_nav_equals_cash_plus_market_value_daily():
    """逐日 nav == cash + Σ qty×price（spy 取证 update_market_value 同刻快照）。"""
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))

    records: list[dict] = []
    orig = Portfolio.update_market_value

    def spy(self, date, prices):
        nav = orig(self, date, prices)
        records.append(
            {
                "date": date,
                "cash": self._cash,
                "qty": {s: p.quantity for s, p in self._positions.items() if p.quantity > 0},
                "last_prices": dict(self._last_prices),
                "nav": Decimal(str(nav)),
            }
        )
        return nav

    Portfolio.update_market_value = spy
    try:
        result, _pf = _run(data, signals, Decimal("10000000"), cost_mult=1)
    finally:
        Portfolio.update_market_value = orig
    assert result.trades_count > 0
    _assert_market_identity(records)


def test_inv7_nan_price_days_identity_holds_via_last_price():
    """缺价 NaN 注入：NaN 收盘日引擎结转最后已知价估值 → 恒等式仍逐日成立。"""
    data = _make_market()
    dirty = data.copy()
    dirty.loc[dirty.index[10:14], "close"] = float("nan")  # 中段 4 日全市场缺价
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))

    records: list[dict] = []
    orig = Portfolio.update_market_value

    def spy(self, date, prices):
        nav = orig(self, date, prices)
        records.append(
            {
                "date": date,
                "cash": self._cash,
                "qty": {s: p.quantity for s, p in self._positions.items() if p.quantity > 0},
                "last_prices": dict(self._last_prices),
                "nav": Decimal(str(nav)),
            }
        )
        return nav

    Portfolio.update_market_value = spy
    try:
        result, _pf = _run(dirty, signals, Decimal("10000000"), cost_mult=1)
    finally:
        Portfolio.update_market_value = orig
    assert result.trades_count > 0
    _assert_market_identity(records)


def test_inv7_counterexample_broken_identity_detected():
    """注入反例：构造 nav ≠ cash+mv 的快照 → 判定器必须红（防恒等判定器假绿）。"""
    good = {
        "date": "2026-01-05",
        "cash": Decimal("90000"),
        "qty": {"SYM_A": Decimal("1000")},
        "last_prices": {"SYM_A": Decimal("10")},
        "nav": Decimal("100000"),
    }
    _assert_market_identity([good])  # sanity：正确快照不红
    broken = dict(good, nav=Decimal("99999"))  # 少 1 元
    with pytest.raises(AssertionError, match="市值恒等断裂"):
        _assert_market_identity([broken])
