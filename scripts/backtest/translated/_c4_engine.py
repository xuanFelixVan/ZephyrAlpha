# [BLUEPRINT] MOD-BT-039 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated._c4_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 批量翻译件（c4_*.py）；c4_batch_screen.py（C4 快筛批测）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日信号用 ≤T-1 数据，T+1 收盘起算收益）；成本=冻结土规（佣金 2.5bp+印花 10bp 卖+滑点 5bp，
#   与 pilot_002 完全一致）；回测引擎口径全 C4 批次统一（可比性）；数据只用健康表
#   （kline_daily_hfq/kline_index/kline_etf_daily/stk_limit/index_constituent/stock_basic）
# [MODIFY-GUARD] tests/backtest/test_c4_engine.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_engine.py
# [A_module] module_id=MOD-BT-039 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 批量翻译共享引擎——数据装载+统一回测+Deflated Sharpe。

C4 批测约定（与 pilot_002_ma_cross 试点一致，保证可比）:
  - 信号: T 日执行用 ≤T-1 数据（PIT）；收益自 T+1 收盘起算（w.shift(1) 口径）；
  - 成本: 佣金 2.5bp 双边 + 印花 10bp 卖 + 滑点 5bp 比例（冻结土规，见 backtest_backlog.yaml BT-P0 批）；
  - 窗口: IS 2020-01-01..2023-12-31（ETF 族 2021-04-01 起，kline_etf_daily 覆盖起点，D 声明）；
  - 股票池: 默认沪深300 成分快照（index_constituent，D1 声明）；个股择时策略用原文标的。

Deflated Sharpe（Bailey & López de Prado 2014）: 以批内 N 条策略为试验集，
SR0 = sqrt(V[SR]) * ((1-γ)*Φ⁻¹(1-1/N) + γ*Φ⁻¹(1-1/(N·e)))，γ≈0.5772；
DSR = Φ( (SR-SR0)·sqrt(T-1) / sqrt(1 - γ3·SR + ((γ4-1)/4)·SR²) )，γ3/γ4 为批内日收益合并偏度/峰度。
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# 冻结土规成本（与 pilot_002_ma_cross 一致，禁改）
COMMISSION_BP = 2.5
STAMP_BP = 10.0
SLIPPAGE_BP = 5.0

C4_START = "2020-01-01"
C4_END = "2023-12-31"
ETF_START = "2021-04-01"  # kline_etf_daily 覆盖起点 2021-03-08，留缓冲


_client_cache: dict[str, Any] = {}


def get_client():
    """ClickHouse 只读客户端（进程内缓存）。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

    key = "ch"
    if key not in _client_cache:
        ensure_ch_env_loaded()
        cfg = load_ch_reader_config()
        from clickhouse_driver import Client

        _client_cache[key] = Client(
            host=cfg["host"], port=int(cfg.get("port", 9000)),
            user=cfg.get("user", "default"), password=cfg.get("password", ""),
            connect_timeout=5,
        )
    return _client_cache[key]


def _q(sql: str) -> list[tuple]:
    return get_client().execute(sql)


def run_query(sql: str) -> list[tuple]:
    """只读查询公开入口（翻译件需要表内未封装字段时用，禁裸连接）。"""
    return _q(sql)


def load_px(start: str, end: str, fields: tuple[str, ...] = ("close",)) -> pd.DataFrame:
    """股票后复权行情宽表。返回 index=trade_date, columns=[symbol 字段组] 的长表。

    fields 从 close/open/high/low/volume/turnover/amount/pct_change 中选；
    返回长表 (trade_date, symbol, *fields)，调用方自行 pivot。
    """
    cols = ", ".join(f"toFloat64({f}) AS {f}" for f in fields)
    rows = _q(
        f"SELECT trade_date, symbol, {cols} FROM c1_market.kline_daily_hfq "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND close > 0"
    )
    px = pd.DataFrame(rows, columns=["trade_date", "symbol", *fields])
    if px.empty:
        raise RuntimeError("kline_daily_hfq 数据缺失")
    px["trade_date"] = pd.to_datetime(px["trade_date"])
    return px


def wide(px: pd.DataFrame, field: str = "close") -> pd.DataFrame:
    """长表 → 宽表（index=trade_date, columns=symbol）。"""
    return px.pivot(index="trade_date", columns="symbol", values=field).sort_index()


def load_index(symbol: str, start: str, end: str, fields: tuple[str, ...] = ("close",)) -> pd.DataFrame:
    """指数日 K 宽序列（kline_index）。返回 DataFrame(index=trade_date, columns=fields)。"""
    cols = ", ".join(f"toFloat64({f}) AS {f}" for f in fields)
    rows = _q(
        f"SELECT trade_date, {cols} FROM c1_market.kline_index "
        f"WHERE symbol = '{symbol}' AND trade_date >= '{start}' AND trade_date <= '{end}' "
        f"ORDER BY trade_date"
    )
    df = pd.DataFrame(rows, columns=["trade_date", *fields]).set_index("trade_date")
    if df.empty:
        raise RuntimeError(f"kline_index {symbol} 数据缺失")
    df.index = pd.to_datetime(df.index)
    return df


def load_breadth(start: str, end: str, symbol: str = "000002") -> pd.DataFrame:
    """市场宽度（涨/跌家数，挂在上证A指 000002 等指数上）。"""
    return load_index(symbol, start, end, fields=("advance_count", "decline_count"))


def load_etf(symbols: list[str], start: str, end: str, field: str = "close") -> pd.DataFrame:
    """ETF 日 K 宽表（kline_etf_daily）。symbols 为纯 6 位代码列表。"""
    sym_list = ", ".join(f"'{s}'" for s in symbols)
    rows = _q(
        f"SELECT trade_date, symbol, toFloat64({field}) AS {field} FROM c1_market.kline_etf_daily "
        f"WHERE symbol IN ({sym_list}) AND trade_date >= '{start}' AND trade_date <= '{end}'"
    )
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", field])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return wide(df, field)


def load_valuation(start: str, end: str, fields: tuple[str, ...] = ("pe", "pb")) -> dict[str, pd.DataFrame]:
    """个股估值宽面板（stock_indicator，tushare_daily_basic 源，2020-01 起覆盖）。

    返回 {field: 宽表(index=trade_date, columns=symbol)}。
    """
    cols = ", ".join(f"toFloat64({f}) AS {f}" for f in fields)
    rows = _q(
        f"SELECT trade_date, symbol, {cols} FROM c1_market.stock_indicator "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND data_source = 'tushare_daily_basic' "
        f"ORDER BY ingest_ts DESC LIMIT 1 BY trade_date, symbol"
    )
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", *fields])
    if df.empty:
        raise RuntimeError("stock_indicator 估值数据缺失（回补窗口不足）")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    out = {}
    for f in fields:
        out[f] = wide(df[["trade_date", "symbol", f]].copy(), f)
    return out


_FIN_METRICS: tuple[str, ...] = (
    "announce_date", "report_period", "np_excl_cum", "equity_incl_minority",
    "rev_q_yoy", "np_q_yoy", "total_current_assets", "total_current_liabilities",
    "fcff_cum", "np_q", "np_cum",
)
_fin_cache: dict[str, pd.DataFrame] = {}


def fin_snapshot(as_of: str, metrics: tuple[str, ...] | None = None) -> pd.DataFrame:
    """财务快照：每 symbol 取 announce_date<=as_of 的最新一期（PIT 安全，DS-230 派生层）。

    整表一次入进程缓存（~40 万行），as-of 在 pandas 内选。返回 index=symbol。
    """
    if "fin" not in _fin_cache:
        cols = ", ".join(_FIN_METRICS)
        rows = _q(f"SELECT symbol, {cols} FROM c3_fundamental.financial_derived")
        df = pd.DataFrame(rows, columns=["symbol", *_FIN_METRICS])
        df["announce_date"] = pd.to_datetime(df["announce_date"])
        df = df.sort_values(["symbol", "announce_date"])
        _fin_cache["fin"] = df
    df = _fin_cache["fin"]
    asof_ts = pd.Timestamp(as_of)
    ok = df[df["announce_date"] <= asof_ts]
    keep = ["symbol", "announce_date", "report_period", *(metrics or ())] if metrics else None
    if keep:
        ok = ok[keep]
    return ok.groupby("symbol").last()


def load_hs300() -> set[str]:
    """沪深300 成分快照（纯 6 位代码）。失败时抛 RuntimeError（D1 不静默降级）。"""
    rows = _q(
        "SELECT symbol_canonical FROM c1_market.index_constituent "
        "WHERE index_code = '000300.SH' AND valid_to IS NULL"
    )
    hs = {(r[0] or "")[:6] for r in rows if r[0]}
    if not hs:
        latest = _q("SELECT max(trade_date) FROM c1_market.index_constituent WHERE index_code = '000300.SH'")[0][0]
        rows = _q(
            f"SELECT symbol FROM c1_market.index_constituent "
            f"WHERE index_code = '000300.SH' AND trade_date = '{latest}'"
        )
        hs = {(r[0] or "")[:6] for r in rows if r[0]}
    if not hs:
        raise RuntimeError("index_constituent 沪深300 成分缺失")
    return hs


def load_index_constituents(index_code: str) -> set[str]:
    """任意指数成分快照（如 000905.SH 中证500）。"""
    rows = _q(
        f"SELECT symbol_canonical FROM c1_market.index_constituent "
        f"WHERE index_code = '{index_code}' AND valid_to IS NULL"
    )
    return {(r[0] or "")[:6] for r in rows if r[0]}


def load_st_flags(start: str, end: str) -> pd.DataFrame:
    """ST 标记长表 (trade_date, symbol, st_flag)，来自 stk_limit。"""
    rows = _q(
        f"SELECT trade_date, symbol, toUInt8(st_flag) AS st_flag FROM c1_market.stk_limit "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{end}'"
    )
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "st_flag"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def filter_st(wide_close: pd.DataFrame, flags: pd.DataFrame) -> pd.DataFrame:
    """把 ST 股从宽表中置 NaN（禁止持有）。flags=(trade_date,symbol,st_flag)。"""
    st = flags[flags["st_flag"] > 0]
    if st.empty:
        return wide_close
    st_pairs = set(zip(st["trade_date"], st["symbol"]))
    mask = pd.DataFrame(False, index=wide_close.index, columns=wide_close.columns)
    idx_map = {d: i for i, d in enumerate(wide_close.index)}
    col_map = {s: i for i, s in enumerate(wide_close.columns)}
    for d, s in st_pairs:
        i = idx_map.get(d)
        j = col_map.get(s)
        if i is not None and j is not None:
            mask.iat[i, j] = True
    return wide_close.mask(mask)


def run_backtest(weights: pd.DataFrame, px_close: pd.DataFrame) -> dict[str, Any]:
    """T+1 收盘执行向量化回测——与 pilot_002_ma_cross.run_backtest 逐行同口径。

    weights: index=trade_date, columns=symbol，目标权重（收盘再平衡）；
    px_close: 同结构收盘价宽表（可含额外列，内部 reindex 对齐）。
    """
    closes = px_close.reindex(weights.index.union(weights.index)).ffill()
    rets = closes.pct_change()
    w = weights.reindex(closes.index).ffill().fillna(0.0)
    gross = (w.shift(1) * rets).sum(axis=1).fillna(0.0)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0) / 2.0
    cost = turnover * (COMMISSION_BP * 2 + STAMP_BP + SLIPPAGE_BP * 2) / 10000.0
    net = gross - cost
    equity = (1.0 + net).cumprod()
    years = max(len(net) / 244.0, 1e-9)
    sharpe = float(net.mean() / net.std() * np.sqrt(244)) if net.std() > 0 else 0.0
    mdd = float((equity / equity.cummax() - 1.0).min())
    return {
        "days": int(len(net)),
        "sharpe": round(sharpe, 3),
        "ann_return": round(float(equity.iloc[-1] ** (1 / years) - 1.0), 4),
        "max_drawdown": round(mdd, 4),
        "avg_turnover_1side": round(float(turnover.mean()), 4),
        "equity_final": round(float(equity.iloc[-1]), 4),
        "hold_days_pct": round(float((weights.sum(axis=1) > 0).mean()), 3),
    }


def daily_net_returns(weights: pd.DataFrame, px_close: pd.DataFrame) -> pd.Series:
    """与 run_backtest 同口径的净收益序列（供 DSR 批内偏度/峰度合并计算）。"""
    closes = px_close.reindex(weights.index.union(weights.index)).ffill()
    rets = closes.pct_change()
    w = weights.reindex(closes.index).ffill().fillna(0.0)
    gross = (w.shift(1) * rets).sum(axis=1).fillna(0.0)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0) / 2.0
    cost = turnover * (COMMISSION_BP * 2 + STAMP_BP + SLIPPAGE_BP * 2) / 10000.0
    return (gross - cost).fillna(0.0)


def batch_deflated_sharpe(nets_by_id: dict[str, pd.Series]) -> dict[str, float | None]:
    """批内 Deflated Sharpe 折减——全委托官方件（SSOT）。

    zephyr.backtest.regime_validation.c4_deflated_sharpe_runner.run_deflated_sharpe_batch
    （num_trials=变体数口径）。序列不可用（<3 点/含非有限值）的策略返回 None。
    """
    clean: dict[str, list[float]] = {}
    for sid, net in nets_by_id.items():
        vals = pd.to_numeric(net, errors="coerce").dropna()
        if len(vals) >= 3 and bool(np.isfinite(vals.values).all()) and float(vals.std()) > 0:
            clean[sid] = [float(v) for v in vals.values]
    if not clean:
        return {sid: None for sid in nets_by_id}
    from zephyr.backtest.regime_validation.c4_deflated_sharpe_runner import (
        C4DeflatedSharpeError,
        run_deflated_sharpe_batch,
    )

    try:
        rep = run_deflated_sharpe_batch(clean)
    except C4DeflatedSharpeError as exc:
        # 静默吞错=排查灾难（2026-09-13 OOS 批全 None 教训）：留日志可见
        import logging

        logging.getLogger(__name__).warning("batch_deflated_sharpe 官方件拒绝: %s", exc)
        return {sid: None for sid in nets_by_id}
    out: dict[str, float | None] = {sid: None for sid in nets_by_id}
    for v in rep.variants:
        out[v.name] = round(float(v.dsr), 4)
    return out


def window_for(kind: str = "stock") -> tuple[str, str]:
    """C4 批测窗口：股票/指数=IS 冻结窗口；ETF=2021-04 起（覆盖起点声明）。"""
    return (ETF_START, C4_END) if kind == "etf" else (C4_START, C4_END)


def emit(strategy_id: str, stats: dict[str, Any], diffs: list[str], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """统一输出结构（单策略 main() 打印 + C4 runner 消费）。"""
    out = {"strategy_id": strategy_id, "stats": stats, "translation_diffs": diffs}
    if extra:
        out.update(extra)
    return out
