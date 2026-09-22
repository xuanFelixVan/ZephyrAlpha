# [BLUEPRINT] MOD-ALT-EMOTION-INDEX-BUILDER | docs/_working/emotion_line/emotion_index_skeleton_v0.md
# [MODULE] zephyr.alt_data.emotion_index_builder
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] stdlib; pandas; zephyr.data.ch_reader (经 reader 注入); zephyr.alt_data.cohort_daily_ledger (_col_float 单源共享)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider (_fetch_emotion_index 路由分支，落表由调度器写通道承担)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯计算禁写库（落表=调度器写通道单写通道，cohort/daban 同款）；六成分滚动 250 观测分位，
#              观测<120 → status=insufficient 权重重分配禁硬凑；禁 fear_greed 异轴顶替（t0 判例）；
#              PIT：close_final 只用 ≤当日收盘数据，pre_open 的 C1-C4 复用 T-1 态、C5/C6 as-of 当日；
#              SQL 全部 _SQL_* 模块常量（NO-BARE-SQL）；reader 抽象为唯一数据面（单测 fake 注入）；
#              同 ts 禁循环依赖（板块热度不进本指数）；行结构与 schemas INSERT_COLUMNS 契约一一对应。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单成分查询失败/数据不足→该成分 status=insufficient|missing 降级不出行错；
#                  全成分不可产→返回 None（调用方记空批），禁拍假值。
# [TESTS] tests/alt_data/test_emotion_index_builder.py
# [A_module] module_id=MOD-ALT-EMOTION-INDEX-BUILDER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""emotion_index_builder — A股市场情绪指数日批构建器（骨架设计稿 v0.2，契约 v0.1）。

独立状态变量：今日场内温度计（0=冰点 1=沸点），与大盘明日走势判断解耦；板块层互为
上下游但板块热度不回灌（防同 ts 循环依赖）。

六成分（内部盘点册四态实证选型，全存量表零新采集）：
    C1 limitup_temp 涨停温度 = 0.4*P(触板家数)+0.3*P(最高连板)+0.3*P(封住率)
    C2 promotion    晋级率   = P( T-1 连板梯队 ∩ T 再封住 / T-1 连板梯队 )
    C3 breadth      广度     = 0.6*P(上涨家数占比)+0.4*P(000300 日收益)
    C4 volume       量能     = 0.5*P(两市成交额)+0.5*P(换手率中位数)
    C5 margin       杠杆     = P(两融余额 20 日变化率)，as-of 最近可得日
    C6 news         新闻     = P(市场新闻情绪 5 日均值)
分位=原值在追溯 250 观测窗内的秩分位；观测<120 → insufficient（权重按可用成分等权
重分配）。首版禁 PCA（成分史起点不齐）；合成=可用成分等权。

stage：close_final（T 日 15:10 定格真源态，C1-C6 全量 as-of T）|
       pre_open（T 日 09:15，C1-C4 复用 T-1 收盘态 + C5/C6 as-of T）。
version v0.1.0；成分集变更=升 minor，权重方案变更=升 major（契约红线）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成分原料窗查询（daban/kline_daily/kline_index/margin/news 窗，reader 注入）
# 层: 算法
# - id: A1
#   name_zh: 六成分滚动 250 观测秩分位（<120 观测 insufficient 不参与聚合）
# - id: A2
#   name_zh: ok 成分等权合成 0-1 灰度+components JSON 契约行（全不可产→None 禁拍假值）
# 层: 输出
# - id: O1
#   name: FetchResult 行交调度器写通道（c1_market.emotion_index 单写通道）
"""

from __future__ import annotations

import datetime
import io
import logging
from typing import Any, Protocol

import pandas as pd

from zephyr.alt_data.cohort_daily_ledger import _col_float
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: list[str] = ["build_emotion_index", "EMOTION_INDEX_VERSION", "STAGE_CLOSE_FINAL", "STAGE_PRE_OPEN"]

EMOTION_INDEX_VERSION = "v0.1.0"
STAGE_CLOSE_FINAL = "close_final"
STAGE_PRE_OPEN = "pre_open"

_PCTL_WINDOW = 250  # 滚动分位窗（观测数）；窗口起点按 1.6 倍日历日回拉容忍缺源空洞
_MIN_OBS = 120  # 分位有效性下限（不足→insufficient）
_MARGIN_CHG_DAYS = 20  # 两融余额变化率回看
_NEWS_MEAN_DAYS = 5  # 新闻情绪均值窗

# 表名唯一真源（#ARCH-CH-024 TableRegistry，禁硬编码字符串）
_TBL_DABAN = get_registry().table("market_daban_board_event")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")
_TBL_MARGIN = get_registry().table("market_margin_trading")
_TBL_NSW = get_registry().table("market_news_sentiment_window")

# NO-BARE-SQL：_SQL_* 常量；SELECT 与 FROM 分行（行级扫描互不命中，免行级 noqa）；
# {tbl}/{day}/{start} 构建侧 format 注入（ISO str）；JOIN 子查询自带 FINAL。
_SQL_LIMITUP_DAILY = (
    "SELECT trade_date, count() AS touched, countIf(close_sealed = 1) AS sealed, "
    "max(consec_limit) AS max_consec "
    "FROM {tbl} FINAL "
    "WHERE trade_date BETWEEN '{start}' AND '{day}' GROUP BY trade_date ORDER BY trade_date"
)
_SQL_PROMOTION = (
    "SELECT t1.trade_date AS d, countIf(t2.symbol IS NOT NULL) / count() AS promo "
    "FROM (SELECT trade_date, symbol "
    "      FROM {tbl} FINAL "
    "      WHERE consec_limit >= 1 AND trade_date BETWEEN '{start}' AND '{day}') t1 "
    "LEFT JOIN (SELECT trade_date, symbol "
    "      FROM {tbl} FINAL "
    "      WHERE close_sealed = 1 AND trade_date BETWEEN '{start}' AND '{day}') t2 "
    "ON t2.symbol = t1.symbol AND t2.trade_date = t1.trade_date + INTERVAL 1 DAY "
    "GROUP BY d ORDER BY d"
)
_SQL_AD_DAILY = (
    "SELECT trade_date, round(countIf(pct_change > 0) / count(), 6) AS up_ratio, "
    "sum(amount) AS amt, median(turnover) AS med_turn "
    "FROM {tbl} FINAL "
    "WHERE trade_date BETWEEN '{start}' AND '{day}' "
    "GROUP BY trade_date ORDER BY trade_date"
)
_SQL_INDEX_CLOSE = (
    "SELECT trade_date, close "
    "FROM {tbl} FINAL "
    "WHERE symbol = '000300' AND trade_date BETWEEN '{start}' AND '{day}' ORDER BY trade_date"
)
_SQL_MARGIN_BAL = (
    "SELECT trade_date, sum(margin_balance) AS bal "
    "FROM {tbl} FINAL "
    "WHERE trade_date BETWEEN '{start}' AND '{day}' GROUP BY trade_date ORDER BY trade_date"
)
_SQL_NEWS_MEAN = (
    "SELECT window_date, sentiment_index "
    "FROM {tbl} FINAL "
    "WHERE scope = 'market' AND window_date BETWEEN '{start}' AND '{day}' ORDER BY window_date"
)


class _Reader(Protocol):
    """CH 读取面最小协议（ch_reader/fake reader 结构性满足，ANY-ABUSE 精确化）。"""

    def query(self, sql: str) -> str: ...


def _query_df(reader: _Reader, sql: str, columns: list[str]) -> pd.DataFrame:
    """经 reader 查询转 DataFrame；空/失败返回空表（单成分缺源降级，不拖垮整行）。"""
    try:
        tsv = reader.query(sql)
    except Exception as e:  # noqa: BLE001 — 缺源降级契约
        log.warning("emotion_index_builder 查询失败降级: %s: %s", type(e).__name__, e)
        return pd.DataFrame(columns=columns)
    if not tsv or not tsv.strip():
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(
            io.StringIO(tsv),
            sep="\t",
            header=None,
            names=columns,
            na_values=["\\N", "NULL"],
            keep_default_na=True,
            dtype=str,
        )
    except Exception as e:  # noqa: BLE001 — 解析失败同降级
        log.warning("emotion_index_builder TSV 解析失败降级: %s", e)
        return pd.DataFrame(columns=columns)


def _asof_value(df: pd.DataFrame, date_col: str, val_col: str, day: str) -> float | None:
    """≤day 的最后一行值（as-of 对齐，滞后成分 PIT 真源）。"""
    if df.empty or date_col not in df.columns or val_col not in df.columns:
        return None
    dates = pd.to_datetime(df[date_col]).dt.date.astype(str)
    v = _col_float(df[dates <= day].copy(), val_col).dropna()
    return float(v.iloc[-1]) if len(v) else None


def _asof_series(series: pd.Series, dates: pd.Series, day: str) -> float | None:
    """与日期列对齐的序列上取 ≤day 最后一个有效值。"""
    if series is None or series.empty or dates is None or dates.empty:
        return None
    mask = pd.to_datetime(dates).dt.date.astype(str) <= day
    v = series[mask].dropna()
    return float(v.iloc[-1]) if len(v) else None


def _pctl(series: pd.Series, value: float | None) -> tuple[float | None, int]:
    """value 在序列末 _PCTL_WINDOW 观测内的秩分位与有效观测数。"""
    vals = series.dropna() if series is not None else pd.Series(dtype=float)
    vals = vals.tail(_PCTL_WINDOW)  # 设计保真：分位窗=末 250 观测（拉窗只作数据冗余）
    n = int(len(vals))
    if value is None or value != value or n == 0:
        return None, n
    return float((vals <= value).sum() / n), n


def _shift_days(day: str, days: int) -> str:
    return (datetime.date.fromisoformat(day) + datetime.timedelta(days=days)).isoformat()


def _window_start(day: str) -> str:
    return _shift_days(day, -590)  # 250 观测≈370 日历日，1.6 倍容忍节假日/缺源空洞


def _component_row(
    name: str, raw: float | None, pctl_v: float | None, obs: int, source: str, note: str = ""
) -> dict[str, Any]:
    status = "ok" if pctl_v is not None and obs >= _MIN_OBS else "insufficient" if pctl_v is not None else "missing"
    return {
        "name": name,
        "raw_value": raw,
        "percentile": pctl_v,
        "weight": 0.0,
        "status": status,
        "obs": obs,
        "asof": "",
        "source": source,
        "note": note,
    }


def _sub_component(
    name: str, asof_day: str, sub: list[tuple[str, float | None, int, float]], source: str
) -> dict[str, Any]:
    """多子项成分：子项分位按 frozen 内部权重聚合；任一子项缺失记入 note。"""
    wsum = acc = 0.0
    missing: list[str] = []
    n_min = 10**9
    for sub_name, p, n, weight in sub:
        if p is None:
            missing.append(sub_name)
            continue
        acc += p * weight
        wsum += weight
        n_min = min(n_min, n)
    pctl_v = acc / wsum if wsum > 0 else None
    obs = n_min if n_min < 10**9 else 0
    row = _component_row(name, None, pctl_v, obs, source, note=f"sub_missing={missing}" if missing else "")
    row["asof"] = asof_day
    return row


def _build_components(reader: _Reader, day: str, c1c4_day: str) -> list[dict[str, Any]]:
    """六成分原值+分位（close_final: c1c4_day==day；pre_open: c1c4_day=T-1）。"""
    start = _window_start(day)
    c1c4_start = _window_start(c1c4_day)
    comps: list[dict[str, Any]] = []

    lu = _query_df(
        reader,
        _SQL_LIMITUP_DAILY.format(tbl=_TBL_DABAN, start=c1c4_start, day=c1c4_day),
        ["trade_date", "touched", "sealed", "max_consec"],
    )
    lu_dates = lu["trade_date"] if not lu.empty else pd.Series(dtype=str)
    touched = _col_float(lu, "touched")
    max_consec = _col_float(lu, "max_consec")
    seal_rate = (_col_float(lu, "sealed") / touched).replace([float("inf")], None)
    w1 = {"touched": 0.4, "max_consec": 0.3, "seal_rate": 0.3}
    comps.append(
        _sub_component(
            "C1_limitup_temp",
            c1c4_day,
            [
                ("touched", *_pctl(touched, _asof_series(touched, lu_dates, c1c4_day)), w1["touched"]),
                ("max_consec", *_pctl(max_consec, _asof_series(max_consec, lu_dates, c1c4_day)), w1["max_consec"]),
                ("seal_rate", *_pctl(seal_rate, _asof_series(seal_rate, lu_dates, c1c4_day)), w1["seal_rate"]),
            ],
            "daban_board_event",
        )
    )

    pr = _query_df(reader, _SQL_PROMOTION.format(tbl=_TBL_DABAN, start=start, day=day), ["d", "promo"])
    pr_dates = pr["d"] if not pr.empty else pd.Series(dtype=str)
    promo = _col_float(pr, "promo")
    pr_val = _asof_series(promo, pr_dates, day)
    pr_p, pr_n = _pctl(promo, pr_val)
    comps.append(_component_row("C2_promotion", pr_val, pr_p, pr_n, "daban_board_event(self-join)"))

    ad = _query_df(
        reader,
        _SQL_AD_DAILY.format(tbl=_TBL_KLINE_DAILY, start=c1c4_start, day=c1c4_day),
        ["trade_date", "up_ratio", "amt", "med_turn"],
    )
    ic = _query_df(
        reader, _SQL_INDEX_CLOSE.format(tbl=_TBL_KLINE_INDEX, start=c1c4_start, day=c1c4_day), ["trade_date", "close"]
    )
    ad_dates = ad["trade_date"] if not ad.empty else pd.Series(dtype=str)
    ic_dates = ic["trade_date"] if not ic.empty else pd.Series(dtype=str)
    up, amt, mt = _col_float(ad, "up_ratio"), _col_float(ad, "amt"), _col_float(ad, "med_turn")
    ret = _col_float(ic, "close").pct_change()
    wb, wv = {"up_ratio": 0.6, "index_ret": 0.4}, {"amt": 0.5, "med_turn": 0.5}
    comps.append(
        _sub_component(
            "C3_breadth",
            c1c4_day,
            [
                ("up_ratio", *_pctl(up, _asof_series(up, ad_dates, c1c4_day)), wb["up_ratio"]),
                ("index_ret", *_pctl(ret, _asof_series(ret, ic_dates, c1c4_day)), wb["index_ret"]),
            ],
            "kline_daily+kline_index",
        )
    )
    comps.append(
        _sub_component(
            "C4_volume",
            c1c4_day,
            [
                ("amt", *_pctl(amt, _asof_series(amt, ad_dates, c1c4_day)), wv["amt"]),
                ("med_turn", *_pctl(mt, _asof_series(mt, ad_dates, c1c4_day)), wv["med_turn"]),
            ],
            "kline_daily",
        )
    )

    mb = _query_df(reader, _SQL_MARGIN_BAL.format(tbl=_TBL_MARGIN, start=start, day=day), ["trade_date", "bal"])
    chg = _col_float(mb, "bal").pct_change(_MARGIN_CHG_DAYS)
    mb_dates = mb["trade_date"] if not mb.empty else pd.Series(dtype=str)
    g_val = _asof_series(chg, mb_dates, day)
    g_p, g_n = _pctl(chg, g_val)
    c5 = _component_row("C5_margin", g_val, g_p, g_n, "margin_trading(as-of)")
    c5["asof"] = day
    comps.append(c5)

    nw = _query_df(
        reader, _SQL_NEWS_MEAN.format(tbl=_TBL_NSW, start=start, day=day), ["window_date", "sentiment_index"]
    )
    nm = _col_float(nw, "sentiment_index").rolling(_NEWS_MEAN_DAYS, min_periods=1).mean()
    nw_dates = nw["window_date"] if not nw.empty else pd.Series(dtype=str)
    e_val = _asof_series(nm, nw_dates, day)
    e_p, e_n = _pctl(nm, e_val)
    c6 = _component_row("C6_news", e_val, e_p, e_n, "news_sentiment_window(rule)")
    c6["asof"] = day
    comps.append(c6)
    return comps


def build_emotion_index(
    day: str, stage: str = STAGE_CLOSE_FINAL, reader: _Reader | None = None
) -> dict[str, Any] | None:
    """构建单个 (trade_date, stage) 的 emotion_index 行（契约 v0.1）。

    返回 dict（trade_date/stage/ts/emotion_index/components/version），全成分不可产
    时返回 None。pre_open：C1-C4 复用 T-1 收盘态（asof 标注）+ C5/C6 as-of T。
    """
    day = datetime.date.fromisoformat(day).isoformat()
    if reader is None:
        from zephyr.data import ch_reader

        reader = ch_reader
    if stage == STAGE_PRE_OPEN:
        c1c4_day, hh, mm = _shift_days(day, -1), 9, 15
    elif stage == STAGE_CLOSE_FINAL:
        c1c4_day, hh, mm = day, 15, 10
    else:
        raise ValueError(f"未知 stage: {stage}")
    comps = _build_components(reader, day, c1c4_day)
    usable = [c for c in comps if c["status"] == "ok"]  # insufficient 有分位但观测不足，不参与聚合
    if not usable:
        return None
    w_each = round(1.0 / len(usable), 6)  # 等权按可用成分数重分配（禁硬凑）
    for c in comps:
        c["weight"] = w_each if c["status"] == "ok" else 0.0
    index_value = round(sum(c["percentile"] * c["weight"] for c in usable), 6)
    ts = datetime.datetime.fromisoformat(f"{day}T{hh:02d}:{mm:02d}:00").replace(
        tzinfo=datetime.timezone(datetime.timedelta(hours=8))
    )
    return {
        "trade_date": datetime.date.fromisoformat(day),
        "stage": stage,
        "ts": ts,
        "emotion_index": index_value,
        "components": comps,
        "version": EMOTION_INDEX_VERSION,
    }
