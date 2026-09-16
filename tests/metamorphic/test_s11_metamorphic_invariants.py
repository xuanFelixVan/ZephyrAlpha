# [BLUEPRINT] MOD-BT-001+MOD-FWCOMP-001 | tests/metamorphic/test_s11_metamorphic_invariants.py
# [MODULE] tests.metamorphic.test_s11_metamorphic_invariants
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine; zephyr.pf_core.strategy_engine.framework_composer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] metamorphic 双不变式（真源 docs/_working/sop_review_nodes/subnode_mining_round1.md §47 子节点3）：
#   INV-1 价格缩放不变——价格×k 且资金×k -> NAV 曲线恰 ×k、收益率/夏普/回撤不变、P&L×k；
#         同资金变体（仅价格×k）收益率在 A 股整手取整误差界内不变；
#         信号强度×c -> 引擎 Σ=1 归一化后结果不变。
#   INV-2 资产置换不变——标的列/数据行置换 -> 组合 NAV 不变（引擎级）；
#         成员面板列置换 -> 合成面板列对应置换（compose 级）。
#   合成数据（0.25 网格价，二进制精确表示），不触库不触网。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/metamorphic/test_s11_metamorphic_invariants.py
# [TTL] permanent
"""S11 整装回测 metamorphic 不变式（立卡首批 4 条中的前两条）。

被测真源（file:line 以 2026-09-16 工作区为准）：
- DefaultBacktestEngine.run  src/zephyr/backtest/implementations/vectorized_engine.py:170
  （S11 整装回测唯一执行引擎，framework_composer.py:1218 消费）
- compose_weight_panels      src/zephyr/pf_core/strategy_engine/framework_composer.py:381
  （W(t,s)=Σα_i·w_i 线性合成+Σ=1 行归一）

容差依据（实测包络，2026-09-16 试点）：缩放资金变体在 Decimal 层非逐位成立——
28 位上下文的除法舍入在整手地板/滑点链路累积（实测 NAV 相对偏差 <=2.1e-7、
P&L 相对偏差 <=1.1e-6、远小于一手粒度 >=800 元），容差=实测包络×5。
零费用置换场景（资金恰好够、无佣金扣现）单次运行内为 Decimal 精确相等。
"""

from __future__ import annotations

import random
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.pf_core.strategy_engine.framework_composer import (
    FrameworkPlan,
    PlanWeight,
    compose_weight_panels,
)

_N_DAYS = 42
_SYMBOLS = ("SYM_A", "SYM_B", "SYM_C")
# 同资金变体容差（整手地板误差界，见文件头推导）
_FIXED_CAPITAL_TOL = 1e-3
# 缩放资金/置换场景容差（实测包络×5，见文件头；缩放链路 28 位 Decimal 除法舍入累积）
_EXACT_TOL = 1e-6
_PNL_TOL = 1e-5


def _make_market(seed: int = 7) -> pd.DataFrame:
    """合成 flat 行情（date/symbol/close）：0.25 网格随机游走，量级 10-60 元。"""
    rng = random.Random(seed)
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    rows = []
    for si, symbol in enumerate(_SYMBOLS):
        quarters = 40 + 8 * si  # 起始价 10/12/14 元（0.25=1 quarter 网格）
        for d in dates:
            quarters = max(8, quarters + rng.choice((-2, -1, -1, 0, 1, 1, 2)))
            rows.append({"date": d, "symbol": symbol, "close": quarters * 0.25})
    return pd.DataFrame(rows)


def _make_signals(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """信号面板（date×symbol）：每 7 日切换目标权重，制造多次调仓（含清仓腿）。"""
    regimes = ([0.6, 0.4, 0.0], [0.1, 0.3, 0.6], [0.0, 0.5, 0.5])
    rows = {}
    for i, d in enumerate(dates):
        rows[d] = regimes[(i // 7) % len(regimes)]
    return pd.DataFrame.from_dict(rows, orient="index", columns=list(_SYMBOLS))


def _engine_config(capital: Decimal, *, costs: bool = True) -> DefaultBacktestEngine:
    """测试专用引擎：关 CH 依赖（涨跌停提供器/PIT 过滤）；可选零费用精确模式。"""
    cfg = BacktestConfig(
        initial_capital=capital,
        enable_pit_universe_filter=False,
        commission_rate=Decimal("0.0000854") if costs else Decimal("0"),
        slippage_bps=Decimal("1") if costs else Decimal("0"),
    )
    return DefaultBacktestEngine(config=cfg, enable_stk_limit_provider=False)


def _run(data: pd.DataFrame, signals: pd.DataFrame, capital: Decimal, *, costs: bool = True):
    engine = _engine_config(capital, costs=costs)
    result = engine.run(data=data, signals=signals, strategy_name="metamorphic")
    return result, engine.last_portfolio.nav_series


def _dates_equal(d0, d1) -> bool:
    """NaT 感知日期相等（nav 序列含 NaT 起始行，NaT==NaT 为 False 需特判）。"""
    if pd.isna(d0) and pd.isna(d1):
        return True
    return d0 == d1


def _assert_nav_scaled(nav_base: pd.Series, nav_scaled: pd.Series, k: Decimal, tol: float) -> None:
    assert len(nav_base) == len(nav_scaled)
    for (d0, v0), (d1, v1) in zip(nav_base.items(), nav_scaled.items()):
        assert _dates_equal(d0, d1)
        assert float(v1) == pytest.approx(float(v0) * float(k), rel=tol), f"NAV@{d0}: {v0}*{k} != {v1}"


# ── INV-1：价格缩放不变 ───────────────────────────────────────────────────────


@pytest.mark.parametrize("k", [Decimal("2"), Decimal("10"), Decimal("0.5")])
def test_price_scaling_with_scaled_capital_exact(k):
    """价格×k 且资金×k -> NAV 逐点恰 ×k、收益率/夏普/回撤不变、P&L×k。

    持仓数量逐笔不变（target_value/price 比值不变 -> 整手地板同值），
    佣金/滑点比例制随 k 线性缩放 -> 本组断言走 _EXACT_TOL。
    """
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))
    capital = Decimal("100000000")  # 1e8：压低整手粒度噪声（文件头误差界）

    base_result, base_nav = _run(data, signals, capital)
    assert base_result.trades_count > 0  # 场景自检：非空跑（sanity_guard 同款前提）

    scaled_data = data.copy()
    scaled_data["close"] = data["close"] * float(k)
    scaled_result, scaled_nav = _run(scaled_data, signals, capital * k)

    _assert_nav_scaled(base_nav, scaled_nav, k, tol=_EXACT_TOL)
    assert scaled_result.trades_count == base_result.trades_count
    assert scaled_result.total_return == pytest.approx(base_result.total_return, abs=_EXACT_TOL)
    assert scaled_result.sharpe_ratio == pytest.approx(base_result.sharpe_ratio, abs=1e-4)
    assert scaled_result.max_drawdown == pytest.approx(base_result.max_drawdown, abs=_EXACT_TOL)
    assert scaled_result.win_rate == base_result.win_rate

    pnl_base = float(base_nav.iloc[-1]) - float(capital)
    pnl_scaled = float(scaled_nav.iloc[-1]) - float(capital * k)
    assert pnl_scaled == pytest.approx(pnl_base * float(k), rel=_PNL_TOL)
    # 基准线有效性：P&L 非零（防"恒 0 满足一切"的假通过）
    assert abs(pnl_base) > 1.0


def test_price_scaling_fixed_capital_return_invariant():
    """同资金、仅价格×k -> 收益率/夏普在整手取整+舍入误差界内不变（单位 bug 探测器）。

    容差 1e-3 = 整手地板误差界（单次 <=lot×p/NAV≈7.2e-5）与 Decimal 舍入
    累积（<=1.1e-6）共同覆盖的多调仓余量。k∈{2,3}：×3 也保持在 0.25 网格的
    0.75 步长上（仍为二进制可精确表示）。
    """
    data = _make_market()
    signals = _make_signals(pd.bdate_range("2026-01-05", periods=_N_DAYS))
    capital = Decimal("100000000")

    base_result, _ = _run(data, signals, capital)
    for k in (2.0, 3.0):
        scaled = data.copy()
        scaled["close"] = data["close"] * k
        r, _ = _run(scaled, signals, capital)
        assert r.total_return == pytest.approx(base_result.total_return, rel=_FIXED_CAPITAL_TOL)
        assert r.sharpe_ratio == pytest.approx(base_result.sharpe_ratio, abs=5e-2)


def test_signal_strength_scale_invariant():
    """信号强度×c -> 引擎逐日 Σ=1 归一化后完全不变（抓归一化/列错位 bug）。"""
    data = _make_market()
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    signals = _make_signals(dates)
    base_result, base_nav = _run(data, signals, Decimal("10000000"), costs=False)

    for c in (0.01, 100.0):
        r, nav = _run(data, signals * c, Decimal("10000000"), costs=False)
        assert r.total_return == pytest.approx(base_result.total_return, abs=_EXACT_TOL)
        assert r.trades_count == base_result.trades_count
        for (d0, v0), (d1, v1) in zip(base_nav.items(), nav.items()):
            assert _dates_equal(d0, d1)
            assert v0 == v1  # 零费用+同持仓 -> Decimal 精确相等


def test_signal_all_zero_rows_preserved_as_cash_days():
    """退化情形：全零信号日=现金日（compose 不做除零归一，引擎无调仓）。

    compose 级钉扎：全零行保留（非 NaN），行级归一只作用于 Σ>0 行。
    """
    plan = FrameworkPlan(
        plan_id="fw-meta", name="meta", risk_profile="balanced", description="",
        weights=(PlanWeight(strategy_id="m1", weight=0.6), PlanWeight(strategy_id="m2", weight=0.4)),
    )
    idx = pd.bdate_range("2026-01-05", periods=4)
    panels = {
        "m1": pd.DataFrame(0.0, index=idx, columns=list(_SYMBOLS)),
        "m2": pd.DataFrame(0.0, index=idx, columns=list(_SYMBOLS)),
    }
    report = compose_weight_panels(plan, panels)
    assert (report.panel == 0.0).all().all()  # 全零行保留=现金日
    assert report.participants == ["m1", "m2"]


# ── INV-2：资产置换不变 ───────────────────────────────────────────────────────


@pytest.mark.parametrize("seed", [11, 29])
def test_asset_permutation_engine_nav_exact(seed):
    """引擎级：行情行序+信号列序置换 -> NAV 曲线 Decimal 精确不变。

    零费用配置：买单整手地板后资金必足（gross < NAV·w 严格），无现金竞争 ->
    fill 顺序无关 -> 逐笔成交与估值与求和顺序解耦。
    """
    data = _make_market()
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    signals = _make_signals(dates)
    capital = Decimal("10000000")

    base_result, base_nav = _run(data, signals, capital, costs=False)
    assert base_result.trades_count > 0

    perm = list(_SYMBOLS)
    random.Random(seed).shuffle(perm)

    shuffled = data.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    permuted_signals = signals[perm]

    r, nav = _run(shuffled, permuted_signals, capital, costs=False)
    assert r.trades_count == base_result.trades_count
    assert r.total_return == pytest.approx(base_result.total_return, abs=_EXACT_TOL)
    assert r.sharpe_ratio == pytest.approx(base_result.sharpe_ratio, abs=1e-9)
    for (d0, v0), (d1, v1) in zip(base_nav.items(), nav.items()):
        assert _dates_equal(d0, d1)
        assert v0 == v1  # Decimal 精确相等


def test_asset_permutation_compose_panel_column_exact():
    """compose 级：成员面板列置换 -> 合成面板逐格不变（输出列 canonical 排序）。

    compose 的 union_cols=sorted(并集)，输出列序与输入列序无关；不变式语义=
    同一 (日期, 标的) 格子的合成值不因输入列排列而变，断言逐格精确相等。
    """
    plan = FrameworkPlan(
        plan_id="fw-meta", name="meta", risk_profile="balanced", description="",
        weights=(PlanWeight(strategy_id="m1", weight=0.5), PlanWeight(strategy_id="m2", weight=0.3),
                 PlanWeight(strategy_id="m3", weight=0.2)),
    )
    idx = pd.bdate_range("2026-01-05", periods=10)
    rng = random.Random(5)
    cols = ["S1", "S2", "S3", "S4"]
    panels = {
        sid: pd.DataFrame(
            [[rng.uniform(0, 1) for _ in cols] for _ in idx], index=idx, columns=cols
        )
        for sid in ("m1", "m2", "m3")
    }
    base = compose_weight_panels(plan, panels).panel

    perm_cols = ["S3", "S1", "S4", "S2"]
    perm_panels = {sid: p[perm_cols] for sid, p in panels.items()}
    permuted = compose_weight_panels(plan, perm_panels).panel

    pd.testing.assert_frame_equal(permuted, base, check_exact=True)
    # 值级 oracle：逐列独立复算 W[:,s]=Σ_i α_i·w_i[:,s]（同 plan.weights 求和序），
    # 若 compose 对置换输入发生列错位（按位置而非标签对齐），此锚点必炸。
    alpha = {"m1": 0.5, "m2": 0.3, "m3": 0.2}
    for s in ("S1", "S2", "S3", "S4"):
        raw = sum(alpha[sid] * panels[sid][s] for sid in ("m1", "m2", "m3"))
        # compose 语义=线性合成后再做行级 Σ=1 归一（全零行保留）——oracle 同口径
        row_sums = sum(
            (alpha[sid] * panels[sid]).sum(axis=1) for sid in ("m1", "m2", "m3")
        )
        expected = raw / row_sums
        pd.testing.assert_series_equal(
            permuted[s], expected, check_exact=False, rtol=1e-12, check_names=False, check_freq=False
        )


@pytest.mark.parametrize("seed", [13])
def test_asset_permutation_compose_member_order_invariant(seed):
    """compose 级：成员（α_i 加权）顺序置换 -> 合成面板不变（float 求和序容差 1e-12）。"""
    plan_a = FrameworkPlan(
        plan_id="fw-meta", name="meta", risk_profile="balanced", description="",
        weights=(PlanWeight(strategy_id="m1", weight=0.5), PlanWeight(strategy_id="m2", weight=0.3),
                 PlanWeight(strategy_id="m3", weight=0.2)),
    )
    order = ["m1", "m2", "m3"]
    random.Random(seed).shuffle(order)
    w_by_id = {"m1": 0.5, "m2": 0.3, "m3": 0.2}
    plan_b = FrameworkPlan(
        plan_id="fw-meta", name="meta", risk_profile="balanced", description="",
        weights=tuple(PlanWeight(strategy_id=s, weight=w_by_id[s]) for s in order),
    )
    idx = pd.bdate_range("2026-01-05", periods=10)
    rng = random.Random(5)
    cols = ["S1", "S2", "S3"]
    panels = {
        sid: pd.DataFrame([[rng.uniform(0, 1) for _ in cols] for _ in idx], index=idx, columns=cols)
        for sid in order
    }
    a = compose_weight_panels(plan_a, panels).panel
    b = compose_weight_panels(plan_b, panels).panel
    pd.testing.assert_frame_equal(b, a, check_exact=False, rtol=1e-12, atol=1e-15)


def test_portfolio_return_invariant_to_member_panel_permutation_endtoend():
    """端到端：对世界做一致的标的重标（行情与合成面板同步换标）-> 组合净值不变。

    S11 链路语义：compose(plan, panel).panel -> engine.run(data, W)。把标的标签
    用同一置换 π 重命名（data.symbol -> π(s)，W 列 -> π(s)），经济内容逐位不变，
    组合 NAV 必须逐日 Decimal 相等（零费用）。
    """
    plan = FrameworkPlan(
        plan_id="fw-meta", name="meta", risk_profile="balanced", description="",
        weights=(PlanWeight(strategy_id="m1", weight=1.0),),
    )
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    data = _make_market()
    rng = random.Random(23)
    panel = pd.DataFrame(
        [[rng.uniform(0, 1) for _ in _SYMBOLS] for _ in dates], index=dates, columns=list(_SYMBOLS)
    )
    composed = compose_weight_panels(plan, {"m1": panel}).panel

    capital = Decimal("10000000")
    r0, nav0 = _run(data, composed, capital, costs=False)

    perm = list(_SYMBOLS)
    random.Random(31).shuffle(perm)
    pi = dict(zip(_SYMBOLS, perm))  # 标签重命名映射（双射）

    data_perm = data.copy()
    data_perm["symbol"] = data_perm["symbol"].map(pi)
    composed_perm = composed.rename(columns=pi)
    r1, nav1 = _run(data_perm, composed_perm, capital, costs=False)

    assert r1.total_return == pytest.approx(r0.total_return, abs=_EXACT_TOL)
    for (d0, v0), (d1, v1) in zip(nav0.items(), nav1.items()):
        assert _dates_equal(d0, d1)
        assert v0 == v1


# ── 红蓝对抗：退化情形特征化（不变式自身的自洽攻击） ─────────────────────────


def test_redblue_all_zero_prices_fail_closed():
    """全零收盘价 -> 全市场"停牌"无成交 -> sanity_guard 拦截（fail-closed 钉扎）。"""
    data = _make_market()
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    zero = data.copy()
    zero["close"] = 0.0
    with pytest.raises(Exception, match="空跑"):
        _run(zero, _make_signals(dates), Decimal("1000000"))


def test_redblue_all_zero_signals_fail_closed():
    """全零信号面板 -> 无调仓空跑 -> sanity_guard 拦截（fail-closed 钉扎）。"""
    data = _make_market()
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    with pytest.raises(Exception, match="空跑"):
        _run(data, _make_signals(dates) * 0.0, Decimal("1000000"))


def test_redblue_nan_prices_tolerated_clean_output():
    """NaN 收盘价 -> 引擎容错不崩（NaN 格视为无价），产出净值序列无 NaN 污染。

    特征化现状（fail-tolerant 路径，非 fail-closed）：不崩、有成交、
    NAV 序列零 NaN——钉扎防"NaN 静默污染资金曲线"回归（见试点报告 F-4）。
    """
    data = _make_market()
    dates = pd.bdate_range("2026-01-05", periods=_N_DAYS)
    dirty = data.copy()
    dirty.loc[dirty.index[:5], "close"] = float("nan")
    result, nav = _run(dirty, _make_signals(dates), Decimal("1000000"))
    assert result.trades_count > 0
    assert not nav.isna().any()
