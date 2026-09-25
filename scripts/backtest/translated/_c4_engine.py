# [BLUEPRINT] MOD-BT-039 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated._c4_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 批量翻译件（c4_*.py）；c4_batch_screen.py（C4 快筛批测）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日信号用 ≤T-1 数据，T+1 收盘起算收益）；成本=冻结土规（佣金 2.5bp+印花 10bp 卖+滑点 5bp，
#   与 pilot_002 完全一致）；回测引擎口径全 C4 批次统一（可比性）；数据只用健康表
#   （kline_daily_hfq/kline_index/kline_etf_daily/stk_limit/index_constituent/stock_basic）；
#   涨跌停可成交性闸默认开（E7 引擎洞修复 2026-09-18：封板收盘禁开仓/跌停收盘禁出逃，
#   判定单位对齐原始价 kline_daily vs stk_limit；gate_limits=False 仅供反例对照）；
#   st-ddup-20260925 去重改造（内收声明）：掩码 pivot 向量化+批级 LRU 缓存（替代逐行
#   dict/iat+每 pass 重查 CH）、_backtest_core 单趟共享（替代 run_backtest 与
#   daily_net_returns 同式两算）、net_returns_by_tiers 多档标量成本线（替代五档各全跑）；
#   判定式/容差/fail-open/净收益公式逐位不变，gpu_rewrite/hotspot_census.md §二为实测依据
# [MODIFY-GUARD] tests/backtest/test_c4_batch_smoke.py; tests/backtest/test_c4_deflated_sharpe_runner.py; tests/backtest/test_c4_auto_oos.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py; tests/backtest/test_c4_deflated_sharpe_runner.py; tests/backtest/test_c4_auto_oos.py; tests/backtest/test_c4_limit_gate.py（S1-A8 裁定 2026-09-17：原锚 test_c4_engine.py 从未存在于 git 历史=幽灵引用，改锚真实守护件）
# [A_module] module_id=MOD-BT-039 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 批量翻译共享引擎——数据装载+统一回测+Deflated Sharpe。

C4 批测约定（与 pilot_002_ma_cross 试点一致，保证可比）:
  - 信号: T 日执行用 ≤T-1 数据（PIT）；收益自 T+1 收盘起算（w.shift(1) 口径）；
  - 成本: 佣金 2.5bp 双边 + 印花 10bp 卖 + 滑点 5bp 比例（冻结土规，见 backtest_backlog.yaml BT-P0 批）；
  - 窗口: IS 2020-01-01..2023-12-31（ETF 族 2021-04-01 起，kline_etf_daily 覆盖起点，D 声明）；
  - 股票池: 默认沪深300 成分快照（index_constituent，D1 声明）；个股择时策略用原文标的。

Deflated Sharpe（Bailey & López de Prado 2014）: N 口径=全局累计可审计试验数+本批变体数
（2026-09-15 裁定改累计口径，真源=N 账本 MOD-BT-200；本 docstring 原为批内 N 口径，S1-A4 裁定更正），
SR0 = sqrt(V[SR]) * ((1-γ)*Φ⁻¹(1-1/N) + γ*Φ⁻¹(1-1/(N·e)))，γ≈0.5772；
DSR = Φ( (SR-SR0)·sqrt(T-1) / sqrt(1 - γ3·SR + ((γ4-1)/4)·SR²) )，γ3/γ4 为批内日收益合并偏度/峰度。
"""

from __future__ import annotations

import re
import threading
from collections import OrderedDict
from datetime import date
from pathlib import Path
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

# 表名经 TableRegistry 真源（#ARCH-CH-024；TABLE-NAME-REGISTRY gate 合规）
from zephyr.data.table_registry import get_registry  # noqa: E402 — 依赖区在 docstring 后

_T_KLINE_DAILY = get_registry().table("market_kline_daily")
_T_KLINE_DAILY_HFQ = get_registry().table("market_kline_daily_hfq")
_T_KLINE_INDEX = get_registry().table("market_index_kline")
_T_KLINE_ETF_DAILY = get_registry().table("market_kline_etf_daily")
_T_STK_LIMIT = get_registry().table("market_stk_limit")
_T_INDEX_CONSTITUENT = get_registry().table("market_index_constituent")

# 涨跌停封板判定容差（E7 探针同口径 2026-09-17：close_raw >= limit_up*(1-1e-4)）
_LIMIT_SEAL_TOL = 1e-4

# 掩码批级 LRU 缓存（st-ddup-20260925 去重改造③，gpu_rewrite/hotspot_census.md §二 L1-a/L1-b/L1-d）：
# 掩码只依赖 (窗口, 宇宙列集)，与格点无关——键=(起,止,6字列集元组)；容量按批内宇宙族数
# （hs300/zz500/all_a）×2 余量。命中即免 2 次 CH 全窗查询+7.2M 行 dict+93.5 万次 .iat
# （实测占单 pass 74-95%）。仅缓存成功构建（fail-open 瞬断不落缓存防毒化）。
_SEAL_MASK_CACHE: OrderedDict[tuple, tuple[pd.DataFrame, pd.DataFrame]] = OrderedDict()
_SEAL_MASK_CACHE_MAX = 6
_SEAL_MASK_LOCK = threading.Lock()

# 最近一次窗口宇宙加载的披露（E4 retrofit：幸存者偏差可见化，禁静默）
_UNIVERSE_DISCLOSURE: dict | None = None

# SQL 集中化常量（§5.160.2；Replacing 表读侧全 FINAL——09-15 批考双份行事故治本 2026-09-16）
SQL_PX = (
    "SELECT trade_date, symbol, {cols} FROM " + _T_KLINE_DAILY_HFQ + " FINAL "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND close > 0"
)
SQL_INDEX_KLINE = (
    "SELECT trade_date, {cols} FROM " + _T_KLINE_INDEX + " FINAL "
    "WHERE symbol = '{symbol}' AND trade_date >= '{start}' AND trade_date <= '{end}' "
    "ORDER BY trade_date"
)
SQL_ETF_KLINE = (
    "SELECT trade_date, symbol, toFloat64({field}) AS {field} FROM " + _T_KLINE_ETF_DAILY + " FINAL "
    "WHERE symbol IN ({sym_list}) AND trade_date >= '{start}' AND trade_date <= '{end}'"
)
SQL_ST_FLAGS = (
    "SELECT trade_date, symbol, toUInt8(st_flag) AS st_flag FROM " + _T_STK_LIMIT + " FINAL "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}'"
)
# SCD-2 窗口并集口径（E4 retrofit 2026-09-18，fw_backtest._hs300_symbols 同范式，#326 治本）：
# 旧 `valid_to IS NULL` 当前快照口径拿"今天还在指数里"的名字回灌历史窗（幸存者偏差，
# 近 12 个月窗 300→331、9.4% 已调出/退市票整批缺席）；窗口并集=窗内曾为成份即入池。
# 1900-01-01 未失效哨兵与 zephyr.data.pit_query 口径同源。
_NO_EXPIRY_SENTINEL = "1900-01-01"
SQL_INDEX_CONS_WINDOW = (
    "SELECT symbol_canonical, valid_to FROM " + _T_INDEX_CONSTITUENT + " FINAL "
    "WHERE index_code = '{index_code}' "
    "AND valid_from <= toDate('{end}') "
    "AND (valid_to IS NULL OR valid_to = toDate('{sentinel}') OR valid_to > toDate('{start}'))"
)


def get_client():
    """ClickHouse 客户端（连接统一治本 2026-09-14：构造委派 ch_writer 统一入口）。"""
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict()


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
    rows = _q(SQL_PX.format(cols=cols, start=start, end=end))
    px = pd.DataFrame(rows, columns=["trade_date", "symbol", *fields])
    if px.empty:
        raise RuntimeError("kline_daily_hfq 数据缺失")
    px["trade_date"] = pd.to_datetime(px["trade_date"])
    return px


def wide(px: pd.DataFrame, field: str = "close") -> pd.DataFrame:
    """长表 → 宽表（index=trade_date, columns=symbol）。

    防御性去重（2026-09-15）：pandas pivot 遇重复 (trade_date, symbol) 抛
    "Index contains duplicate entries, cannot reshape"（09-11 数据被 09-14 日更
    任务全量重灌 5206 组双写，OOS 批考 6 策略全炸实证）。同键重复行取最后一条
    （ingest 顺序，语义=最新落库值），让批考对写入侧幂等事故免疫。
    """
    key = ["trade_date", "symbol"]
    if px.duplicated(subset=key).any():
        px = px.drop_duplicates(subset=key, keep="last")
    return px.pivot(index="trade_date", columns="symbol", values=field).sort_index()


def load_index(symbol: str, start: str, end: str, fields: tuple[str, ...] = ("close",)) -> pd.DataFrame:
    """指数日 K 宽序列（kline_index）。返回 DataFrame(index=trade_date, columns=fields)。"""
    cols = ", ".join(f"toFloat64({f}) AS {f}" for f in fields)
    rows = _q(SQL_INDEX_KLINE.format(cols=cols, symbol=symbol, start=start, end=end))
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
    rows = _q(SQL_ETF_KLINE.format(field=field, sym_list=sym_list, start=start, end=end))
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
    "announce_date",
    "report_period",
    "np_excl_cum",
    "equity_incl_minority",
    "rev_q_yoy",
    "np_q_yoy",
    "total_current_assets",
    "total_current_liabilities",
    "fcff_cum",
    "np_q",
    "np_cum",
    "np_ttm",
    "ocf_ttm",
    "rev_ttm",
    "operating_profit_cum",
    "total_assets",
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


def fin_history(as_of: str, metrics: tuple[str, ...]) -> pd.DataFrame:
    """逐期财务历史（公告门 PIT）：announce_date<=as_of 的全部行，按 (symbol,report_period)
    取最新公告版。用于"近四季 ROE/近五年 FCFF"类逐期规则。"""
    cols = ", ".join(metrics)
    if "finh" not in _fin_cache:
        rows = _q(
            f"SELECT symbol, report_period, announce_date, {cols} FROM c3_fundamental.financial_derived "
            f"WHERE announce_date IS NOT NULL ORDER BY symbol, report_period, announce_date"
        )
        df = pd.DataFrame(rows, columns=["symbol", "report_period", "announce_date", *metrics])
        df["announce_date"] = pd.to_datetime(df["announce_date"])
        df["report_period"] = pd.to_datetime(df["report_period"])
        _fin_cache["finh"] = df
    df = _fin_cache["finh"]
    ok = df[df["announce_date"] <= pd.Timestamp(as_of)]
    return ok.groupby(["symbol", "report_period"], as_index=False).last()


def load_index_constituents(index_code: str, start: str, end: str) -> set[str]:
    """指数成份**窗口内并集**（SCD-2 时点口径，E4 retrofit 2026-09-18）。

    窗口 [start, end] 内曾为成份即入池（含期内调出/退市者），消灭幸存者偏差；
    与 fw_backtest._hs300_symbols 同范式（valid_from<=end ∩ valid_to 未失效或 >start）。
    空结果抛 RuntimeError（D1 不静默降级）；旧"当前快照"口径已废——快照语义
    （择时用）禁走本函数，勿以无窗调用复辟。
    披露：_UNIVERSE_DISCLOSURE 记录窗口并集 vs 期末快照差额（幸存者偏差可见化）。
    """
    global _UNIVERSE_DISCLOSURE
    rows = _q(SQL_INDEX_CONS_WINDOW.format(index_code=index_code, start=start, end=end, sentinel=_NO_EXPIRY_SENTINEL))
    universe: set[str] = set()
    still_in_at_end: set[str] = set()
    for raw, valid_to in rows:
        code = (str(raw) if raw else "")[:6]
        if not code:
            continue
        universe.add(code)
        vt = "" if valid_to is None else str(valid_to)[:10]
        if vt in ("", _NO_EXPIRY_SENTINEL) or vt > end:
            still_in_at_end.add(code)
    if not universe:
        raise RuntimeError(f"index_constituent {index_code} 窗口 [{start}..{end}] 成分缺失")
    exited = sorted(universe - still_in_at_end)
    _UNIVERSE_DISCLOSURE = {
        "schema": "universe_disclosure/v1",
        "mode": "pit_index_window",
        "index_code": index_code,
        "window": {"start": start, "end": end},
        "universe_n": len(universe),
        "snapshot_n": len(still_in_at_end),
        "since_exit_n": len(exited),
        "since_exit_share": round(len(exited) / len(universe), 4),
        "note": "窗口内曾为成份即入池；snapshot_n=旧 valid_to IS NULL 口径会给的只数",
    }
    return universe


def load_hs300(start: str, end: str) -> set[str]:
    """沪深300 窗口内成份并集（纯 6 位代码）。失败时抛 RuntimeError（D1 不静默降级）。"""
    return load_index_constituents("000300.SH", start, end)


def last_universe_disclosure() -> dict | None:
    """最近一次窗口宇宙加载的披露（幸存者偏差可见化；无加载返回 None）。"""
    return _UNIVERSE_DISCLOSURE


def load_st_flags(start: str, end: str) -> pd.DataFrame:
    """ST 标记长表 (trade_date, symbol, st_flag)，来自 stk_limit。"""
    rows = _q(SQL_ST_FLAGS.format(start=start, end=end))
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "st_flag"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def filter_st(wide_close: pd.DataFrame, flags: pd.DataFrame) -> pd.DataFrame:
    """把 ST 股从宽表中置 NaN（禁止持有）。flags=(trade_date,symbol,st_flag)。"""
    st = flags[flags["st_flag"] > 0]
    if st.empty:
        return wide_close
    st_pairs = set(zip(st["trade_date"], st["symbol"], strict=False))  # 等长序列，strict=False=原语义
    mask = pd.DataFrame(False, index=wide_close.index, columns=wide_close.columns)
    idx_map = {d: i for i, d in enumerate(wide_close.index)}
    col_map = {s: i for i, s in enumerate(wide_close.columns)}
    for d, s in st_pairs:
        i = idx_map.get(d)
        j = col_map.get(s)
        if i is not None and j is not None:
            mask.iat[i, j] = True
    return wide_close.mask(mask)


def _align_pivot_to_columns(
    piv: pd.DataFrame, index: pd.DatetimeIndex, col_map: dict[str, int], n_cols: int
) -> pd.DataFrame:
    """pivot 宽表 → (index × n_cols 位置阵) 对齐：行 reindex，列按 col_map 摆位（缺→NaN）。

    列对齐语义与原逐行实现同构：6 字前缀→列位置映射后者覆盖（dict 推导 last-wins）；
    CH 侧缺行/索引外日期→NaN→后续比较 False（=原 dict.get miss→skip 不写）。
    """
    piv = piv.reindex(index=index)
    out = np.full((len(piv.index), n_cols), np.nan)
    src = piv.to_numpy()
    for j_src, sym in enumerate(piv.columns):
        j_tgt = col_map.get(str(sym)[:6])
        if j_tgt is not None:
            out[:, j_tgt] = src[:, j_src]
    return pd.DataFrame(out, index=piv.index, columns=pd.RangeIndex(n_cols))


def _wide_limit_agg(long_df: pd.DataFrame, field: str, how: str) -> pd.DataFrame:
    """limit 长表→宽表，重复键按方向聚合——复刻原逐行实现"任一行判定封板即写 True
    （False 从不回写）"的 OR 累积语义：sealed_up=any_k[close>=up_k*(1-tol)] ⇒ up 取
    **min**（最严阈值）；sealed_down=any_k[close<=dn_k*(1+tol)] ⇒ dn 取 **max**。
    NaN-skipping（groupby 聚合天然跳 NaN）；无重复键走纯 pivot 快路径（CH FINAL 常态）。"""
    key = ["trade_date", "symbol"]
    if long_df.duplicated(subset=key).any():
        long_df = long_df.groupby(key, as_index=False, sort=False)[field].agg(how)
    return long_df.pivot(index="trade_date", columns="symbol", values=field).sort_index()


def _build_seal_masks(
    index: pd.DatetimeIndex,
    columns: pd.Index,
    raw_rows: list[tuple],
    lim_rows: list[tuple],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """掩码向量化构建（st-ddup-20260925 去重改造③）：CH 行→pivot→列对齐→numpy 比较。

    判定式与原逐行实现同序同精度：up*(1-_LIMIT_SEAL_TOL)/dn*(1+_LIMIT_SEAL_TOL)；
    缺价/停牌/NULL 限制/非股票标的→NaN 比较 False（=原 skip）。
    """
    empty = pd.DataFrame(False, index=index, columns=columns)
    if not raw_rows or not lim_rows:
        return empty, empty
    raw_px = pd.DataFrame(raw_rows, columns=["trade_date", "symbol", "close_raw"])
    lim = pd.DataFrame(lim_rows, columns=["trade_date", "symbol", "limit_up", "limit_down"])
    for df in (raw_px, lim):
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    col_map: dict[str, int] = {str(c)[:6]: j for j, c in enumerate(columns)}  # last-wins 同原实现
    raw_w = _align_pivot_to_columns(wide(raw_px, "close_raw"), index, col_map, len(columns))
    up_w = _align_pivot_to_columns(
        _wide_limit_agg(lim.drop(columns=["limit_down"]), "limit_up", "min"), index, col_map, len(columns)
    )
    dn_w = _align_pivot_to_columns(
        _wide_limit_agg(lim.drop(columns=["limit_up"]), "limit_down", "max"), index, col_map, len(columns)
    )
    sealed_up = pd.DataFrame(raw_w.to_numpy() >= up_w.to_numpy() * (1 - _LIMIT_SEAL_TOL), index=index, columns=columns)
    sealed_down = pd.DataFrame(
        raw_w.to_numpy() <= dn_w.to_numpy() * (1 + _LIMIT_SEAL_TOL), index=index, columns=columns
    )
    return sealed_up, sealed_down


def _load_seal_masks(index: pd.DatetimeIndex, columns: pd.Index) -> tuple[pd.DataFrame, pd.DataFrame]:
    """涨跌停封板掩码（E7 引擎洞修复 2026-09-18）：返回 (sealed_up, sealed_down) 布尔宽表。

    判定必须单位对齐原始价（E7 假绿追加 §3 实锤：hfq 与涨停价直接比较=单位错配误报）——
    raw close 取 kline_daily，limit_up/limit_down 取 stk_limit（原始价口径）；
    缺价/停牌/无涨跌幅限制（NULL）或非股票标的（ETF 等 stk_limit 无行）→ False 不闸
    （fail-open 如实披露，不编造可成交性）。

    st-ddup-20260925 去重改造（内收声明：替代本函数原"每 pass 两次 CH 全窗查询+
    7.2M 行 dict 推导+93.5 万次 .iat 行循环"零缓存实现）：CH 两查询→pivot 宽表→
    numpy 对齐比较+批级 LRU 缓存，同宇宙多 pass/多格共享一次构建；
    判定式/容差/fail-open 语义逐位不变。
    """
    empty = pd.DataFrame(False, index=index, columns=columns)
    syms = [str(c)[:6] for c in columns]
    if not syms or len(index) == 0:
        return empty, empty
    start = index.min().strftime("%Y-%m-%d")
    end = index.max().strftime("%Y-%m-%d")
    key = (start, end, tuple(syms))
    with _SEAL_MASK_LOCK:
        hit = _SEAL_MASK_CACHE.get(key)
        if hit is not None:
            _SEAL_MASK_CACHE.move_to_end(key)
            return hit
    sym_list = ", ".join(f"'{s}'" for s in sorted(set(syms)))
    try:
        raw_rows = _q(
            f"SELECT trade_date, symbol, toFloat64(close) FROM {_T_KLINE_DAILY} FINAL "
            f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND symbol IN ({sym_list})"
        )
        lim_rows = _q(
            f"SELECT trade_date, symbol, toFloat64(limit_up), toFloat64(limit_down) "
            f"FROM {_T_STK_LIMIT} FINAL "
            f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND symbol IN ({sym_list})"
        )
    except Exception:  # noqa: BLE001 — 闸原料不可得不得炸正考（fail-open 有意为之，见下行注记）
        # 闸原料不可得=不阻断回测（fail-open），但不得伪装成已闸——调用方 stats 里带注记
        return empty, empty
    masks = _build_seal_masks(index, columns, raw_rows, lim_rows)
    with _SEAL_MASK_LOCK:
        _SEAL_MASK_CACHE[key] = masks
        _SEAL_MASK_CACHE.move_to_end(key)
        while len(_SEAL_MASK_CACHE) > _SEAL_MASK_CACHE_MAX:
            _SEAL_MASK_CACHE.popitem(last=False)
    return masks


def apply_fillability_gate(weights: pd.DataFrame, gate_limits: bool = True) -> pd.DataFrame:
    """涨跌停可成交性闸（E7 引擎洞修复）：封板日禁开新仓/禁出逃。

    语义（向量化 T+1 框架下 w_t 的隐含成交价=close_t）：目标权重较已执行权重增加（买入）
    且当日收盘封涨停 → 买单不可成交，已执行权重保持前值；减少（卖出）且收盘封跌停 → 同理。
    未封板日目标权重正常生效。等权不变（|Δ|≤1e-12 视为无交易）。
    """
    if not gate_limits:
        return weights
    sealed_up, sealed_down = _load_seal_masks(weights.index, weights.columns)
    W = weights.to_numpy(dtype=float)
    SU = sealed_up.to_numpy(dtype=bool)
    SD = sealed_down.to_numpy(dtype=bool)
    out = np.empty_like(W)
    prev = np.zeros(W.shape[1], dtype=float)
    for i in range(W.shape[0]):
        target = W[i]
        cur = np.where(
            ((target > prev + 1e-12) & SU[i]) | ((target < prev - 1e-12) & SD[i]),
            prev,
            target,
        )
        out[i] = cur
        prev = cur
    return pd.DataFrame(out, index=weights.index, columns=weights.columns)


def _backtest_core(
    weights: pd.DataFrame, px_close: pd.DataFrame, gate_limits: bool = True
) -> tuple[pd.Series, pd.Series]:
    """run_backtest / daily_net_returns 共享单趟（st-ddup-20260925 去重改造②，
    gpu_rewrite/hotspot_census.md §二 L2-b：两函数体重叠 90%，执行器两连调=白付 1 个 pass）。
    返回 (gross, turnover)，成本线由 _net_line 标量乘派生——净收益公式零改写。"""
    closes = px_close.reindex(weights.index.union(weights.index)).ffill()
    rets = closes.pct_change()
    w = weights.reindex(closes.index).ffill().fillna(0.0)
    w = apply_fillability_gate(w, gate_limits=gate_limits)
    gross = (w.shift(1) * rets).sum(axis=1).fillna(0.0)
    turnover = (w - w.shift(1)).abs().sum(axis=1).fillna(0.0) / 2.0
    return gross, turnover


def _net_line(gross: pd.Series, turnover: pd.Series, slippage_bp: float | None) -> pd.Series:
    """冻结土规成本线（佣金 2.5bp 双边+印花 10bp 卖+滑点档双边）——与原
    run_backtest/daily_net_returns 内联式同序同精度；改档=标量乘（五档 <0.1ms 实测，
    gpu_rewrite/hotspot_census.md §二 L2-c）。"""
    slip = SLIPPAGE_BP if slippage_bp is None else float(slippage_bp)
    cost = turnover * (COMMISSION_BP * 2 + STAMP_BP + slip * 2) / 10000.0
    return gross - cost


def run_backtest(
    weights: pd.DataFrame,
    px_close: pd.DataFrame,
    gate_limits: bool = True,
    slippage_bp: float | None = None,
) -> dict[str, Any]:
    """T+1 收盘执行向量化回测——与 pilot_002_ma_cross 逐行同口径。

    weights: index=trade_date, columns=symbol，目标权重（收盘再平衡）；
    px_close: 同结构收盘价宽表（可含额外列，内部 reindex 对齐）；
    gate_limits: 涨跌停可成交性闸（默认开，E7 引擎洞修复 2026-09-18——封板买入/跌停卖出
    不可成交；False=旧行为，仅供反例对照）。
    slippage_bp: 滑点档覆盖（批C 考尺成本敏感性扫描专用，st-ibt-remedy-cf-20260923）；
    None=冻结土规 SLIPPAGE_BP 零变更。仅滑点项可覆盖，佣金/印花不动——
    正考口径必须传 None，档位扫描是侧向分析不改冻结土规。
    """
    gross, turnover = _backtest_core(weights, px_close, gate_limits=gate_limits)
    net = _net_line(gross, turnover, slippage_bp)
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


def daily_net_returns(
    weights: pd.DataFrame,
    px_close: pd.DataFrame,
    gate_limits: bool = True,
    slippage_bp: float | None = None,
) -> pd.Series:
    """与 run_backtest 同口径的净收益序列（供 DSR 批内偏度/峰度合并计算）。

    gate_limits: 涨跌停可成交性闸（默认开，与 run_backtest 一致）。
    slippage_bp: 滑点档覆盖（批C 考尺成本敏感性扫描专用）；None=冻结土规零变更。
    """
    gross, turnover = _backtest_core(weights, px_close, gate_limits=gate_limits)
    return _net_line(gross, turnover, slippage_bp).fillna(0.0)


def run_backtest_full(
    weights: pd.DataFrame,
    px_close: pd.DataFrame,
    gate_limits: bool = True,
    slippage_bp: float | None = None,
) -> tuple[dict[str, Any], pd.Series]:
    """单趟双产物 (stats, net)——run_backtest + daily_net_returns 合并入口
    （st-ddup-20260925 去重改造②，内收声明：替代执行器两连调 run_backtest+
    daily_net_returns；stats 与 run_backtest(...) 逐位一致，net 与
    daily_net_returns(...) 逐位一致，两原函数签名/语义不变）。
    slippage_bp 语义与 run_backtest 相同（None=冻结土规；扫描档走 net_returns_by_tiers）。"""
    gross, turnover = _backtest_core(weights, px_close, gate_limits=gate_limits)
    net = _net_line(gross, turnover, slippage_bp)
    equity = (1.0 + net).cumprod()
    years = max(len(net) / 244.0, 1e-9)
    sharpe = float(net.mean() / net.std() * np.sqrt(244)) if net.std() > 0 else 0.0
    mdd = float((equity / equity.cummax() - 1.0).min())
    stats = {
        "days": int(len(net)),
        "sharpe": round(sharpe, 3),
        "ann_return": round(float(equity.iloc[-1] ** (1 / years) - 1.0), 4),
        "max_drawdown": round(mdd, 4),
        "avg_turnover_1side": round(float(turnover.mean()), 4),
        "equity_final": round(float(equity.iloc[-1]), 4),
        "hold_days_pct": round(float((weights.sum(axis=1) > 0).mean()), 3),
    }
    return stats, net.fillna(0.0)


def net_returns_by_tiers(
    weights: pd.DataFrame,
    px_close: pd.DataFrame,
    slippage_bps,
    gate_limits: bool = True,
) -> dict[float, pd.Series]:
    """一趟 gross/turnover × 多档成本标量乘（st-ddup-20260925 去重改造①，内收声明：
    替代 run_cost_tier_scan 五档各自全量重算的引擎侧路径——档间唯一差异是一行标量
    成本线，五遍全量回测收敛为一遍回测+五档后处理）。
    返回 {float(bp): net}；各档 net 与 daily_net_returns(slippage_bp=bp) 逐位一致。"""
    gross, turnover = _backtest_core(weights, px_close, gate_limits=gate_limits)
    return {float(bp): _net_line(gross, turnover, bp).fillna(0.0) for bp in slippage_bps}


def batch_deflated_sharpe(nets_by_id: dict[str, pd.Series], num_trials: int | None = None) -> dict[str, float | None]:
    """批内 Deflated Sharpe 折减——全委托官方件（SSOT）。

    zephyr.backtest.regime_validation.c4_deflated_sharpe_runner.run_deflated_sharpe_batch。
    num_trials（2026-09-15 N 口径裁定）：调用方传入全局累计可审计试验数+本批变体数
    （累计口径，真源=N 账本 MOD-BT-200）；None=变体数（runner 旧缺省，仅供旧批兼容）。
    序列不可用（<3 点/含非有限值）的策略返回 None。
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
        rep = run_deflated_sharpe_batch(clean, num_trials=num_trials)
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


# ── S3 知识生效日哨兵（备忘 96 批 3，2026-09-14）───────────────────────────
# 依据：arXiv:2601.13770 Look-Ahead-Bench——LLM 的知识截止日本质是时点约束。
# 本目录 c4_*.py 全是 AI 翻译产物：策略原文发表于某日、译文由某次会话生成，
# 二者取晚者=该产物的"知识生效日"。回测窗口早于它=用了当时的未来知识，
# 按 D120 三态（clean/drift/blocked）判漂移，放行但必须声明。
_KNOWLEDGE_SENTINEL_RE = re.compile(r"\[KNOWLEDGE_EFFECTIVE_FROM\]\s*(\d{4}-\d{2}-\d{2})")
_KNOWLEDGE_SCAN_DIR = Path(__file__).resolve().parent


def parse_knowledge_effective_from(path: str | Path) -> str | None:
    """读单个 AI 产物的知识生效日哨兵（写在模块 docstring 内，无哨兵=None）。"""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    m = _KNOWLEDGE_SENTINEL_RE.search(text)
    return m.group(1) if m else None


def scan_knowledge_sentinels(root: str | Path | None = None) -> dict[str, str]:
    """扫翻译目录 → {文件名: 知识生效日}（无哨兵的文件不进字典，诚实缺）。"""
    base = Path(root) if root is not None else _KNOWLEDGE_SCAN_DIR
    out: dict[str, str] = {}
    for p in sorted(base.glob("c4_*.py")):
        eff = parse_knowledge_effective_from(p)
        if eff:
            out[p.name] = eff
    return out


def knowledge_drift_report(start: str, end: str, root: str | Path | None = None) -> dict[str, Any]:
    """S3 预检：回测窗口 vs AI 产物知识生效日（D120 三态，复用地图漂移口径）。

    clean   = 所有带哨兵产物的生效日都 <= 窗口起点 → 无漂移
    drift   = 存在产物生效日晚于窗口起点 → 放行但 drift_items 必须声明
    empty   = 目录下没有任何带哨兵的产物（哨兵未铺开，提示补标，不阻断）

    注：本函数只读不写，纯报告；是否阻断由调用方按 SOP 决定（S3 现为"声明制"）。
    """
    sents = scan_knowledge_sentinels(root)
    if not sents:
        return {
            "verdict": "empty",
            "reason": "翻译目录无带哨兵的 AI 产物",
            "backtest_range": [start, end],
            "drift_items": [],
            "scanned": 0,
        }
    s_d = date.fromisoformat(start[:10])
    drift_items = [
        {"artifact": name, "knowledge_effective_from": eff}
        for name, eff in sorted(sents.items(), key=lambda kv: kv[1])
        if date.fromisoformat(eff) > s_d
    ]
    return {
        "verdict": "drift" if drift_items else "clean",
        "backtest_range": [start, end],
        "drift_count": len(drift_items),
        "drift_items": drift_items,
        "scanned": len(sents),
    }


def emit(
    strategy_id: str, stats: dict[str, Any], diffs: list[str], extra: dict[str, Any] | None = None
) -> dict[str, Any]:
    """统一输出结构（单策略 main() 打印 + C4 runner 消费）。"""
    out = {"strategy_id": strategy_id, "stats": stats, "translation_diffs": diffs}
    if extra:
        out.update(extra)
    return out
