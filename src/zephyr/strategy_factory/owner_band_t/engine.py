# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas; numpy; zephyr.strategy_factory.owner_band_t.td_sequence; zephyr.strategy_factory.owner_band_t.signals; zephyr.strategy_factory.owner_band_t.regime_gate; zephyr.strategy_factory.owner_band_t.costs; zephyr.strategy_factory.owner_band_t.intraday_t
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.exam; tests/strategy_factory/test_s_owner_001_engine.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 信号 ≤t 收盘判定、t+1 开盘成交（PIT 铁律）；滑点流动性输入=t-1 日成交额（当日额收盘才可知）；做T 额度=前收持仓-当日波段卖出（T+1 结构）；回撤熔断 10%+冷静期 20 日（冻结）；波段/做T 分开记账（逐层归因）
# [MODIFY-GUARD] 语义变更=考试冻结口径变更，冻结期禁改
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] KeyError(面板缺列)； ValueError(配置非法)
# [TESTS] tests/strategy_factory/test_s_owner_001_engine.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""S-OWNER-001 组合引擎——波段（金字塔三档+镜像三档减仓）+ 日内做T + regime 门 + 风控。

时序铁律（冻结）:
  * 日线信号用 ≤t 收盘数据判定 → t+1 开盘价成交；
  * 小时级信号在 bar 结束时刻判定 → 该 bar close 成交（零前视）；
  * 门状态=执行日严格早于当日的最近快照行（翻转次日生效）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from zephyr.strategy_factory.owner_band_t.costs import total_cost_yuan
from zephyr.strategy_factory.owner_band_t.intraday_t import (
    LOT_SIZE,
    should_close_t,
    should_open_t,
    round_lot,
)
from zephyr.strategy_factory.owner_band_t.regime_gate import gate_open_series
from zephyr.strategy_factory.owner_band_t.signals import build_signal_panel
from zephyr.strategy_factory.owner_band_t.td_sequence import td_sequential

INITIAL_CAPITAL = 1_000_000.0
DRAWDOWN_BREAKER = 0.10  # 冻结: NAV 自高点回撤 10% 全撤
COOLDOWN_DAYS = 20  # 冻结: 冷静期 20 交易日
LADDER_DEFAULT = (0.4, 0.3, 0.3)
LADDER_ALT = (0.5, 0.25, 0.25)
TRADING_DAYS_PER_YEAR = 244


@dataclass(frozen=True)
class StrategyConfig:
    """考试网格配置（冻结域见 exam.GRID）。"""

    entry_mode: str = "setup9"  # setup8 | setup9 | countdown_neg
    p1: float = 0.7
    exit_arm: str = "bb_upper"  # bb_upper | prior_high | return_quantile
    ladder: tuple[float, float, float] = LADDER_DEFAULT
    gate_min_conf: float = 0.35
    t_max_trips: int = 1
    t_size: float = 0.3
    use_gate: bool = True
    use_t: bool = True

    def validate(self) -> None:
        if self.entry_mode not in ("setup8", "setup9", "countdown_neg"):
            raise ValueError(f"entry_mode 非法: {self.entry_mode}")
        if not 0 < self.p1 < 1:
            raise ValueError("p1 须在 (0,1)")
        if self.exit_arm not in ("bb_upper", "prior_high", "return_quantile"):
            raise ValueError(f"exit_arm 非法: {self.exit_arm}")
        if abs(sum(self.ladder) - 1.0) > 1e-9:
            raise ValueError("金字塔系数和须为 1")
        if self.t_max_trips < 0 or not 0 < self.t_size <= 1:
            raise ValueError("做T 参数非法")


@dataclass
class _DailyState:
    cash: float = INITIAL_CAPITAL
    shares: int = 0
    entry_stage: int = 0  # 已建档数 0..3
    t1_fill_low: float = np.nan  # 档1 成交日 ETF low（档2 触发参考）
    exit_count: int = 0  # 本轮减仓已执行档数
    cooldown_until: int = -1  # 冷静期截止（日期位置索引，含）
    nav_peak: float = INITIAL_CAPITAL
    turnover_band: float = 0.0
    turnover_t: float = 0.0
    t_net_pnl: float = 0.0
    t_trips: int = 0


def build_entry_signal(td: pd.DataFrame, entry_mode: str) -> pd.Series:
    """入场信号（按冻结口径）。"""
    if entry_mode == "setup8":
        return td["setup_count"] == 8
    if entry_mode == "setup9":
        return td["setup_count"] == 9
    # countdown_neg: countdown 进行中 8<=c<=12（c-13<0 且 c>=8）
    c = td["countdown_count"]
    return (c >= 8) & (c <= 12)


def build_exit_flag(sig: pd.DataFrame, close: pd.Series, exit_arm: str) -> pd.Series:
    """减仓上沿判据（冻结三臂）。"""
    if exit_arm == "bb_upper":
        return sig["bb_upper"].astype(bool)
    if exit_arm == "prior_high":
        ref = sig["prior_high_ref"]
        return (close >= ref) & ref.notna()
    if exit_arm == "return_quantile":
        return sig["ret_quantile"].astype(bool)
    raise ValueError(f"exit_arm 非法: {exit_arm}")


def run_backtest(
    panel: dict,
    config: StrategyConfig,
    start: str,
    end: str,
) -> dict[str, Any]:
    """运行单配置回测（IS/OOS 同一实现，窗口切片在面板内完成）。

    :return: dict(nav, metrics, t_net_pnl, t_trips, turnover_band, turnover_t,
                  n_band_trades, exposure_ratio, config)
    """
    config.validate()
    idx = panel["idx"]
    etf = panel["etf"]
    hourly = panel["hourly"]
    regime = panel["regime"]

    dates = etf.index[(etf.index >= pd.Timestamp(start)) & (etf.index <= pd.Timestamp(end))]
    if len(dates) < 30:
        raise RuntimeError(f"窗口过短: {start}~{end} 仅 {len(dates)} 交易日")

    # 信号面（指数）——一次性预计算
    td = td_sequential(idx["close"], idx["low"])
    sig = build_signal_panel(idx["close"], idx["high"])
    entry_sig = build_entry_signal(td, config.entry_mode)
    exit_flag = build_exit_flag(sig, idx["close"], config.exit_arm)
    accel_sig = td["exhaustion"].astype(bool) & (sig["vol_pct"] > config.p1)
    # PIT 对齐: 决策在 t 收盘 → 执行在下一交易日
    entry_exec = entry_sig.shift(1, fill_value=False).reindex(dates).fillna(False).astype(bool)
    exit_exec = exit_flag.shift(1, fill_value=False).reindex(dates).fillna(False).astype(bool)
    accel_exec = accel_sig.shift(1, fill_value=False).reindex(dates).fillna(False).astype(bool)

    gate = (
        gate_open_series(dates, regime, config.gate_min_conf)
        if config.use_gate
        else pd.Series(True, index=dates)
    )

    n = len(dates)
    idx_pos = {d: i for i, d in enumerate(dates)}
    open_px = etf["open"].reindex(dates).to_numpy(dtype=float)
    high_px = etf["high"].reindex(dates).to_numpy(dtype=float)
    low_px = etf["low"].reindex(dates).to_numpy(dtype=float)
    close_px = etf["close"].reindex(dates).to_numpy(dtype=float)
    amount_px = etf["amount"].reindex(dates).to_numpy(dtype=float)
    n_bars = etf["n_bars"].reindex(dates).to_numpy(dtype=float)
    prev_amount = np.concatenate([[np.nan], amount_px[:-1]])  # t-1 成交额（PIT 流动性输入）
    gate_arr = gate.to_numpy(dtype=bool)

    hourly_closes = panel.get("hourly_closes") or {}
    if config.use_t and not hourly_closes:
        sub = hourly.loc[hourly.index.get_level_values(0).isin(dates)]
        for d, grp in sub.groupby(level=0):
            hourly_closes[d] = grp["close"].tolist()

    st = _DailyState()
    nav_series = np.full(n, np.nan)
    exposure = np.zeros(n)
    n_band_trades = 0
    bought_today = 0
    prev_nav = INITIAL_CAPITAL
    full_exit_pending = False

    def _buy(frac: float, price: float, liq: float) -> None:
        nonlocal n_band_trades, bought_today
        target_value = frac * (st.cash + st.shares * price)
        add_shares = round_lot(target_value / price)
        if add_shares < LOT_SIZE:
            return
        notional = add_shares * price
        cost = total_cost_yuan(notional, liq)
        st.cash -= notional + cost
        st.shares += add_shares
        st.turnover_band += notional
        bought_today += add_shares  # T+1: 当日新买不入做T 额度
        n_band_trades += 1

    def _sell_frac(frac: float, price: float, liq: float) -> int:
        nonlocal n_band_trades
        sell_shares = round_lot(st.shares * frac)
        if sell_shares <= 0:
            return 0
        notional = sell_shares * price
        cost = total_cost_yuan(notional, liq)
        st.cash += notional - cost
        st.shares -= sell_shares
        st.turnover_band += notional
        n_band_trades += 1
        return sell_shares

    def _sell_all(price: float, liq: float) -> None:
        nonlocal n_band_trades
        if st.shares <= 0:
            return
        notional = st.shares * price
        cost = total_cost_yuan(notional, liq)
        st.cash += notional - cost
        st.shares = 0
        st.turnover_band += notional
        n_band_trades += 1

    exit_sell_fracs = tuple(reversed(config.ladder))  # 镜像三档（倒序）

    for i, d in enumerate(dates):
        liq = prev_amount[i]
        liq = liq if np.isfinite(liq) else amount_px[i]
        gate_ok = bool(gate_arr[i])
        bought_today = 0

        # --- 开盘: 执行昨日收盘判定的订单 ---
        if full_exit_pending:
            _sell_all(open_px[i], liq)
            full_exit_pending = False
            st.entry_stage = 0
            st.exit_count = 0
        else:
            if st.entry_stage > 0 and exit_exec.iloc[i]:
                if st.exit_count < 2:
                    sold = _sell_frac(exit_sell_fracs[st.exit_count], open_px[i], liq)
                    if sold > 0:
                        st.exit_count += 1
                else:
                    _sell_all(open_px[i], liq)  # 第三档减仓清尾
                    st.entry_stage = 0
                    st.exit_count = 0
                if st.shares == 0:
                    st.entry_stage = 0
                    st.exit_count = 0
            # 建仓档（门关/冷静期不建仓；已有减仓轮次时不重入）
            if (
                st.entry_stage == 0
                and st.exit_count == 0
                and gate_ok
                and i > st.cooldown_until
                and entry_exec.iloc[i]
            ):
                _buy(config.ladder[0], open_px[i], liq)
                if st.shares > 0:
                    st.entry_stage = 1
                    st.t1_fill_low = low_px[i]
                    st.exit_count = 0
            elif (
                i >= 1
                and st.entry_stage == 1
                and st.exit_count == 0
                and gate_ok
                and np.isfinite(st.t1_fill_low)
                and close_px[i - 1] < st.t1_fill_low
            ):
                # 档2: 昨收 < 档1 成交日最低（更低低点加仓）
                _buy(config.ladder[1], open_px[i], liq)
                if st.shares > 0:
                    st.entry_stage = 2
            elif st.entry_stage == 2 and st.exit_count == 0 and gate_ok and accel_exec.iloc[i]:
                # 档3: 底部加速（TD 极值 ∧ 波动率分位>P1）→ 至仓位上限
                _buy(config.ladder[2], open_px[i], liq)
                if st.shares > 0:
                    st.entry_stage = 3

        # --- 日内做T（额度=前收持仓-当日波段卖出；当日新买不入额度）---
        if config.use_t and gate_ok and st.entry_stage > 0 and n_bars[i] >= 4:
            bars = hourly_closes.get(d, [])
            if len(bars) >= 4:
                quota = max(0, st.shares - bought_today)  # T+1: 只能动用旧股
                trips = 0
                realized_today = 0.0
                morning_ret = bars[0] / open_px[i] - 1.0
                if should_open_t(morning_ret, trips, config.t_max_trips, realized_today, prev_nav):
                    t_shares = min(round_lot(config.t_size * quota), quota)
                    if t_shares >= LOT_SIZE:
                        buy_notional = t_shares * bars[0]
                        buy_cost = total_cost_yuan(buy_notional, liq, is_t_trade=True)
                        st.cash -= buy_notional + buy_cost
                        st.turnover_t += buy_notional
                        trips += 1
                        closed = False
                        for b in range(1, 4):
                            if b < 3 and should_close_t(bars[0], bars[b]):
                                sell_notional = t_shares * bars[b]
                                sell_cost = total_cost_yuan(sell_notional, liq, is_t_trade=True)
                                st.cash += sell_notional - sell_cost
                                st.turnover_t += sell_notional
                                realized_today += sell_notional - sell_cost - buy_notional - buy_cost
                                closed = True
                                break
                        if not closed:
                            sell_notional = t_shares * bars[3]  # 15:00 强制平
                            sell_cost = total_cost_yuan(sell_notional, liq, is_t_trade=True)
                            st.cash += sell_notional - sell_cost
                            st.turnover_t += sell_notional
                            realized_today += sell_notional - sell_cost - buy_notional - buy_cost
                        st.t_net_pnl += realized_today
                        st.t_trips += 1

        # --- 收盘: NAV/回撤熔断判定 ---
        nav = st.cash + st.shares * close_px[i]
        nav_series[i] = nav
        exposure[i] = st.shares * close_px[i] / nav if nav > 0 else 0.0
        st.nav_peak = max(st.nav_peak, nav)
        if st.nav_peak > 0 and nav / st.nav_peak - 1.0 <= -DRAWDOWN_BREAKER and not full_exit_pending:
            full_exit_pending = True  # 次日开盘全撤
            st.cooldown_until = min(i + COOLDOWN_DAYS, n - 1)
        prev_nav = nav

    nav = pd.Series(nav_series, index=dates, name="nav")
    metrics = compute_metrics(nav, st.turnover_band + st.turnover_t)
    return {
        "nav": nav,
        "metrics": metrics,
        "t_net_pnl": st.t_net_pnl,
        "t_trips": st.t_trips,
        "turnover_band": st.turnover_band,
        "turnover_t": st.turnover_t,
        "n_band_trades": n_band_trades,
        "exposure_ratio": float(np.nanmean(exposure)),
        "config": config,
    }


def compute_metrics(nav: pd.Series, total_turnover: float) -> dict[str, float]:
    """年化 Sharpe（rf=0, √244）/ 最大回撤 / 年换手（单边名义/年均 NAV）。"""
    ret = nav.pct_change().dropna()
    if len(ret) < 2 or ret.std(ddof=1) == 0 or np.isclose(nav.iloc[0], 0):
        sharpe = 0.0
    else:
        sharpe = float(ret.mean() / ret.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))
    peak = nav.cummax()
    maxdd = float((nav / peak - 1.0).min())
    years = len(nav) / TRADING_DAYS_PER_YEAR
    mean_nav = float(nav.mean())
    ann_turnover = (total_turnover / mean_nav / years) if mean_nav > 0 and years > 0 else 0.0
    return {
        "sharpe": sharpe,
        "maxdd": maxdd,
        "ann_turnover": float(ann_turnover),
        "ann_return": float((nav.iloc[-1] / nav.iloc[0]) ** (1 / years) - 1) if years > 0 and nav.iloc[-1] > 0 else 0.0,
        "n_days": int(len(nav)),
    }


def run_buy_and_hold(panel: dict, start: str, end: str) -> dict[str, Any]:
    """基准: 510300 买入持有（首日开盘买入持有到期末）。"""
    etf = panel["etf"]
    dates = etf.index[(etf.index >= pd.Timestamp(start)) & (etf.index <= pd.Timestamp(end))]
    open_px = etf["open"].reindex(dates).to_numpy(dtype=float)
    close_px = etf["close"].reindex(dates).to_numpy(dtype=float)
    amount_px = etf["amount"].reindex(dates).to_numpy(dtype=float)
    liq = amount_px[0]
    shares = round_lot(INITIAL_CAPITAL / open_px[0])
    notional = shares * open_px[0]
    cost = total_cost_yuan(notional, liq)
    cash = INITIAL_CAPITAL - notional - cost
    nav = cash + shares * close_px
    nav_s = pd.Series(nav, index=dates, name="nav_bh")
    m = compute_metrics(nav_s, notional)
    return {"nav": nav_s, "metrics": m, "turnover": notional}
