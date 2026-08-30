# [BLUEPRINT] MOD-INT-NEWS-NIGHT | 待统筹登记（92号清单 §8.4 M3-② / tracker #138）
# [MODULE] zephyr.intelligence.nightly_sentiment_window
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] pandas; zephyr.data.news_collector; zephyr.data.ch_writer（persist 时）; zephyr.intelligence.news_sentiment_analyzer; zephyr.intelligence.news_symbol_linker（可选注入）
# [CONSUMERS] 夜间批/盘前流程调用方（92号 §8.4③）；MOD-PLAN-004 overnight_boundary_reviser 消费接线待统筹裁定（本模块输出契约预留 plan004_input 对接字段，MOD-PLAN-004 零改动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 夜间窗口=前一交易日18:00(含)→交易日08:00(不含)左闭右开；sentiment_index=窗口平均极性（与 SentimentAggregator 口径一致）；news_data 为 SCD 多版本表按 news_id 去重（keep first=最早版本 PIT 语义）；空窗口→total_count=0+degraded=True 不抛；persist 默认关，写表经 ReplacingMergeTree(scope,symbol,window_type,window_ts) 同键替换幂等；情绪分数作事件信号维度非独立 alpha（26号备忘 §2.7 裁定）
# [MODIFY-GUARD] 待统筹登记（92号清单 §8.4）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NightlySentimentError(ZA-IT-0008)——仅 trade_date 非法时抛 ValueError（契约违反）；CH 查询/写表异常走降级（degraded/persisted=False+reasons 留痕）不抛
# [TESTS] tests/intelligence/test_nightly_sentiment_window.py
# [A_module] module_id=MOD-INT-NEWS-NIGHT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] tracker #138 情绪持久化表闭环（news_sentiment_window，DS-107）

"""
MOD-INT-NEWS-NIGHT NightlySentimentWindow — 夜间新闻情绪窗口聚合器（92号清单 §8.4 M3-②）。

功能边界：
- 夜间窗口：前一交易日 18:00（含）→ 交易日 08:00（不含），左闭右开
- 读取：复用 news_collector.collect_news（PIT 严格查询）后按窗口过滤
- 打分：复用 NewsSentimentAnalyzer（默认规则法；LLM 扩展口经 analyzer 注入）
- 关联：可选注入 NewsSymbolLinker（tracker #139），统计标的关联覆盖/歧义/market 级条数
- 落库：persist=True 时写 c1_market.news_sentiment_window（tracker #138，DS-107），
  ReplacingMergeTree 同键替换 → 重跑幂等；writer 可注入（测试 mock）
- 输出：NightlySentimentResult（纯 dataclass，JSON 可序列化），to_dict() 含
  plan004_input 对接预留字段（news_sentiment/news_total/degraded）——MOD-PLAN-004
  overnight_boundary_reviser 当前无 news_sentiment 入参（实证 compute(trade_date,
  bs005_triggered=False)），消费接线由统筹后续波次裁定，本模块不改 MOD-PLAN-004

依据: 92号清单 §8.4 + 44号备忘 §4 表 M3-② 行 + 26号备忘 §2.7 + tracker #138/#139
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: trade_date 参数
#   fields: 参数 trade_date，类型注解 datetime.date
#   code: nightly_sentiment_window.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: analyzer 参数
#   fields: 参数 analyzer（无注解）
#   code: nightly_sentiment_window.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: linker 参数
#   fields: 参数 linker（无注解）
#   code: nightly_sentiment_window.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: persist 参数
#   fields: 参数 persist（无注解）
#   code: nightly_sentiment_window.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① NightlySentimentResult
#   name_en: NightlySentimentResult
#   intro: 夜间新闻情绪窗口聚合结果（JSON 可序列化）。
#   desc: 夜间新闻情绪窗口聚合结果（JSON 可序列化）。 window 归属日=交易日（次日）：窗口=[前一交易日 18:00, 交易日 08:00)。 degraded=True 表示…；公共方法（定义序）: to_dict…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② nightly_window
#   name_en: nightly_window
#   intro: 夜间窗口边界：[前一交易日 18:00, 交易日 08:00)，左闭右开。
#   desc: 夜间窗口边界：[前一交易日 18:00, 交易日 08:00)，左闭右开。 注：前一"交易日"按自然日前推一天（周末/节假日新闻同样落入窗口， 窗口语义=时间窗非交易日历推导——…；源码 L203-L212
#   inputs: trade_date
#   outputs: tuple[datetime.datetime, datetime.datet…
# - id: A3
#   name_zh: ③ compute_nightly_sentiment
#   name_en: compute_nightly_sentiment
#   intro: 夜间新闻情绪窗口聚合主入口（M3-②）。
#   desc: 夜间新闻情绪窗口聚合主入口（M3-②）。 Args: trade_date: 交易日（ISO 字符串或 date，窗口归属日=次日）。 analyzer: 情绪分析器（None=…；源码 L249-L397
#   inputs: trade_date analyzer linker persist writer top_n
#   outputs: NightlySentimentResult
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[datetime.datetime, datetime.datet…
#   name_en: tuple[datetime.datetime, datetime.datet…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 夜间批/盘前流程调用方（92号 §8.4③）；MOD-PLAN-004 overnight_boundary_reviser 消费接线待统筹裁定（本模块输出契…
# - id: O2
#   name_zh: NightlySentimentResult
#   name_en: NightlySentimentResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 夜间批/盘前流程调用方（92号 §8.4③）；MOD-PLAN-004 overnight_boundary_reviser 消费接线待统筹裁定（本模块输出契…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Callable, Final

import pandas as pd

from zephyr.data.news_collector import collect_news
from zephyr.intelligence.news_sentiment_analyzer import NewsSentimentAnalyzer
from zephyr.intelligence.news_symbol_linker import NewsSymbolLinker, SymbolLinkage

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约
# ============================================================================


class NightlySentimentError(ZephyrBaseError):
    """ZA-IT-0008: NightlySentimentWindow 错误（输入契约违反）。"""

    error_code = "ZA-IT-0008"


# ============================================================================
# 2. 常量（44号 §4 M3-② 夜间窗口口径；写表列序=DDL-as-Code 真源 INSERT_COLUMNS）
# ============================================================================

NIGHT_WINDOW_START_HOUR: Final = 18  # 前一交易日 18:00 起（含）
NIGHT_WINDOW_END_HOUR: Final = 8  # 交易日 08:00 止（不含，左闭右开）

WINDOW_TYPE_NIGHT: Final = "night"
SCOPE_MARKET: Final = "market"

# 目标表（DDL-as-Code 真源 schemas/categories/market_news_sentiment_window.py；
# 本模块为写入器，列序必须与真源 INSERT_COLUMNS 一致——business_data_categories.yaml
# 品类补登为统筹后续项，暂用常量表名，与 overnight_boundary_reviser fallback 同约定）
_TARGET_TABLE: Final = "c1_market.news_sentiment_window"
_INSERT_COLUMNS: Final = (
    "(window_ts, window_end, window_type, scope, symbol, sentiment_index, avg_polarity, "
    "positive_count, negative_count, neutral_count, total_count, top_events_json, data_source)"
)

DEFAULT_TOP_N: Final = 5  # top_events_json 头部事件条数（按 |polarity| 降序）


# ============================================================================
# 3. 输出契约
# ============================================================================


@dataclass(frozen=True)
class NightlySentimentResult:
    """夜间新闻情绪窗口聚合结果（JSON 可序列化）。

    window 归属日=交易日（次日）：窗口=[前一交易日 18:00, 交易日 08:00)。
    degraded=True 表示无新闻/读取异常等降级（sentiment_index 按 0.0 中性处理）。
    """

    date: str  # 交易日（ISO，窗口归属日）
    window_start: datetime.datetime  # 前一交易日 18:00
    window_end: datetime.datetime  # 交易日 08:00
    sentiment_index: float  # 夜间窗口综合情绪指数 [-1, 1]（=窗口平均极性）
    avg_polarity: float
    positive_count: int
    negative_count: int
    neutral_count: int
    total_count: int  # news_id 去重后窗口新闻条数
    top_events: tuple[dict[str, Any], ...] = field(default_factory=tuple)  # 按 |polarity| 降序 TopN
    linked_symbol_count: int = 0  # 关联到标的的新闻条数（#139；未注入 linker 时恒 0）
    ambiguous_count: int = 0  # 歧义关联条数
    market_level_count: int = 0  # 无关联 market 级条数
    persisted: bool = False  # 是否已写 news_sentiment_window 表
    degraded: bool = False  # 无新闻/读取异常降级标记
    reasons: tuple[str, ...] = field(default_factory=tuple)  # 决策/降级理由链留痕

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典；含 plan004_input 对接预留字段（MOD-PLAN-004 消费接线挂账）。"""
        d = asdict(self)
        d["window_start"] = self.window_start.isoformat()
        d["window_end"] = self.window_end.isoformat()
        d["plan004_input"] = {
            "news_sentiment": self.sentiment_index,
            "news_total": self.total_count,
            "degraded": self.degraded,
        }
        return d


# ============================================================================
# 4. 内部工具
# ============================================================================


def nightly_window(trade_date: datetime.date) -> tuple[datetime.datetime, datetime.datetime]:
    """夜间窗口边界：[前一交易日 18:00, 交易日 08:00)，左闭右开。

    注：前一"交易日"按自然日前推一天（周末/节假日新闻同样落入窗口，
    窗口语义=时间窗非交易日历推导——周五 18:00→周一 08:00 跨周末新闻自然覆盖）。
    """
    prev_day = trade_date - datetime.timedelta(days=1)
    start = datetime.datetime.combine(prev_day, datetime.time(NIGHT_WINDOW_START_HOUR, 0))
    end = datetime.datetime.combine(trade_date, datetime.time(NIGHT_WINDOW_END_HOUR, 0))
    return start, end


def _to_naive_wall(ts: Any) -> pd.Timestamp:
    """统一转 Asia/Shanghai 墙面时间 naive Timestamp（CH 时区口径；NaT 透传）。"""
    t = pd.to_datetime(ts, errors="coerce")
    if pd.isna(t):
        return pd.NaT
    if getattr(t, "tzinfo", None) is not None:
        return t.tz_convert("Asia/Shanghai").tz_localize(None)
    return t


def _build_insert_row(result: NightlySentimentResult, data_source: str) -> tuple:
    """NightlySentimentResult → news_sentiment_window 插入行（列序=_INSERT_COLUMNS）。"""
    return (
        result.window_start.strftime("%Y-%m-%d %H:%M:%S"),
        result.window_end.strftime("%Y-%m-%d %H:%M:%S"),
        WINDOW_TYPE_NIGHT,
        SCOPE_MARKET,
        "",  # symbol（market 级空串；symbol 级为 #139 后续聚合预留）
        result.sentiment_index,
        result.avg_polarity,
        result.positive_count,
        result.negative_count,
        result.neutral_count,
        result.total_count,
        json.dumps(list(result.top_events), ensure_ascii=False),
        data_source,
    )


# ============================================================================
# 5. 主入口
# ============================================================================


def compute_nightly_sentiment(
    trade_date: str | datetime.date,
    *,
    analyzer: NewsSentimentAnalyzer | None = None,
    linker: NewsSymbolLinker | None = None,
    persist: bool = False,
    writer: Callable[[Any], bool] | None = None,
    top_n: int = DEFAULT_TOP_N,
) -> NightlySentimentResult:
    """夜间新闻情绪窗口聚合主入口（M3-②）。

    Args:
        trade_date: 交易日（ISO 字符串或 date，窗口归属日=次日）。
        analyzer: 情绪分析器（None=默认规则法 NewsSentimentAnalyzer()）。
        linker: 标的关联器（None=不关联，market 级聚合，linked_symbol_count=0 留痕）。
        persist: 是否写 news_sentiment_window 表（默认关；重跑同键替换幂等）。
        writer: 写表函数注入（签名 FetchResult→bool；None=ch_writer.write_result）。
        top_n: top_events 头部事件条数（按 |polarity| 降序）。

    Returns:
        NightlySentimentResult：纯 dataclass，to_dict() JSON 可序列化。

    Raises:
        ValueError: trade_date 非法（ERROR_CONTRACT 唯一抛出点）。
    """
    if isinstance(trade_date, str):
        d = datetime.date.fromisoformat(trade_date)  # 非法日期抛 ValueError（ERROR_CONTRACT）
    else:
        d = trade_date
    iso = d.isoformat()
    win_start, win_end = nightly_window(d)
    reasons: list[str] = []

    analyzer = analyzer or NewsSentimentAnalyzer()

    # ── 读取（collect_news 日级 PIT 查询 → 窗口过滤；SCD 按 news_id 去重 keep first）──
    prev_iso = (d - datetime.timedelta(days=1)).isoformat()
    try:
        news_df = collect_news(prev_iso, iso)
    except Exception as exc:  # noqa: BLE001 — 读取异常降级空窗口不抛
        log.warning("夜间新闻读取异常，降级空窗口: %s", exc)
        news_df = pd.DataFrame()
        reasons.append(f"新闻读取异常降级空窗口（fail-open）：{exc}")

    if news_df.empty:
        reasons.append("夜间窗口无新闻（degraded）")
        result = NightlySentimentResult(
            date=iso,
            window_start=win_start,
            window_end=win_end,
            sentiment_index=0.0,
            avg_polarity=0.0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            total_count=0,
            degraded=True,
            reasons=tuple(reasons),
        )
        return _maybe_persist(result, persist, writer, reasons)

    # 窗口过滤 + SCD 去重（keep first=最早版本，与 analyzer P1-3 口径一致）
    work = news_df.copy()
    work["_ts"] = work["publish_time"].map(_to_naive_wall)
    work = work.dropna(subset=["_ts"]).sort_values("_ts")
    work = work.drop_duplicates(subset="news_id", keep="first")
    mask = (work["_ts"] >= win_start) & (work["_ts"] < win_end)
    window_df = work.loc[mask]

    if window_df.empty:
        reasons.append(
            f"窗口 [{win_start:%m-%d %H:%M}, {win_end:%m-%d %H:%M}) 内无新闻（共扫描 {len(work)} 条，degraded）"
        )
        result = NightlySentimentResult(
            date=iso,
            window_start=win_start,
            window_end=win_end,
            sentiment_index=0.0,
            avg_polarity=0.0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            total_count=0,
            degraded=True,
            reasons=tuple(reasons),
        )
        return _maybe_persist(result, persist, writer, reasons)

    # ── 打分（规则法默认；LLM 经 analyzer 注入扩展口）──
    scored = analyzer.analyze_news_df(window_df)
    polarities = scored["polarity"].astype(float)

    # ── 标的关联（#139，可选注入）──
    linkages: list[SymbolLinkage] = []
    linkage_by_id: dict[str, SymbolLinkage] = {}
    if linker is not None:
        linkages = linker.link_df(window_df)
        linkage_by_id = {lk.news_id: lk for lk in linkages}
    linked_n = sum(1 for lk in linkages if lk.symbols)
    ambiguous_n = sum(1 for lk in linkages if lk.ambiguous)
    # market_level_count 仅注入 linker 时有评估语义；未注入=未评估记 0
    market_n = (len(window_df) - linked_n) if linker is not None else 0

    # ── 聚合（sentiment_index=窗口平均极性，与 SentimentAggregator 口径一致）──
    total = len(scored)
    pos_n = int((polarities > 0).sum())
    neg_n = int((polarities < 0).sum())
    neu_n = total - pos_n - neg_n
    avg_p = round(float(polarities.mean()), 4)

    # 头部事件（按 |polarity| 降序 TopN，附关联标的）
    merged = scored.copy()
    merged["_abs_p"] = merged["polarity"].abs()
    top_df = merged.sort_values("_abs_p", ascending=False).head(top_n)
    top_events = tuple(
        {
            "news_id": str(row["news_id"]),
            "title": str(row["title"]),
            "polarity": float(row["polarity"]),
            "symbols": list(linkage_by_id.get(str(row["news_id"]), SymbolLinkage(news_id="")).symbols),
        }
        for _, row in top_df.iterrows()
    )

    reasons.append(f"夜间窗口 {total} 条（正 {pos_n}/负 {neg_n}/中性 {neu_n}），sentiment_index={avg_p:+.4f}")
    if linker is not None:
        reasons.append(f"标的关联：{linked_n} 条关联标的（歧义 {ambiguous_n}），{market_n} 条 market 级")

    # 打分方法留痕（单一方法→该值；混合→mixed；写表 data_source 列）
    methods = set(scored["method"].astype(str).unique())
    data_source = methods.pop() if len(methods) == 1 else "mixed"

    result = NightlySentimentResult(
        date=iso,
        window_start=win_start,
        window_end=win_end,
        sentiment_index=avg_p,
        avg_polarity=avg_p,
        positive_count=pos_n,
        negative_count=neg_n,
        neutral_count=neu_n,
        total_count=total,
        top_events=top_events,
        linked_symbol_count=linked_n,
        ambiguous_count=ambiguous_n,
        market_level_count=market_n,
        reasons=tuple(reasons),
    )
    return _maybe_persist(result, persist, writer, list(reasons), data_source=data_source)


def _maybe_persist(
    result: NightlySentimentResult,
    persist: bool,
    writer: Callable[[Any], bool] | None,
    reasons: list[str],
    *,
    data_source: str = "rule",
) -> NightlySentimentResult:
    """persist=True 时写 news_sentiment_window 表（写表异常降级 persisted=False 不抛）。"""
    if not persist:
        return result
    try:
        from zephyr.data.provider_base import FetchResult

        row = _build_insert_row(result, data_source=data_source)
        fetch = FetchResult(
            table=_TARGET_TABLE,
            columns=[c.strip() for c in _INSERT_COLUMNS.strip("()").split(",")],
            rows=[row],
            last_key="",
            elapsed_sec=0.0,
        )
        if writer is not None:
            ok = bool(writer(fetch))
        else:
            from zephyr.data import ch_writer

            ok = ch_writer.write_result(fetch, columns=_INSERT_COLUMNS)
    except Exception as exc:  # noqa: BLE001 — 写表异常降级不抛
        log.warning("news_sentiment_window 写表异常，降级 persisted=False: %s", exc)
        reasons.append(f"写表异常降级（fail-open）：{exc}")
        return _replace_result(result, persisted=False, reasons=reasons)
    reasons.append(
        "已写 news_sentiment_window（ReplacingMergeTree 同键替换幂等）" if ok else "写表返回 False（降级留痕）"
    )
    return _replace_result(result, persisted=ok, reasons=reasons)


def _replace_result(result: NightlySentimentResult, *, persisted: bool, reasons: list[str]) -> NightlySentimentResult:
    """frozen dataclass 字段替换（persist 状态/理由链回填）。"""
    return replace(result, persisted=persisted, reasons=tuple(reasons))


# ============================================================================
# 6. 模块导出
# ============================================================================

__all__: Final = [
    "NightlySentimentError",
    "NightlySentimentResult",
    "compute_nightly_sentiment",
    "nightly_window",
    "NIGHT_WINDOW_START_HOUR",
    "NIGHT_WINDOW_END_HOUR",
    "WINDOW_TYPE_NIGHT",
    "SCOPE_MARKET",
]
