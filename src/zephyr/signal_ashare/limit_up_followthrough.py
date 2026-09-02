# [BLUEPRINT] MOD-SIG-078 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-19 行）
# [MODULE] zephyr.signal_ashare.limit_up_followthrough
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.limit_up_down（只读，昨封板池）; c1_market.kline_daily（只读，今日表现+昨炸板池）; c1_market.stk_limit（只读，昨涨停价）; c1_market.market_breadth_snapshot（只读，市场炸板率 attempted/sealed 字段在码复用）
# [CONSUMERS] （候选：情绪页指标卡「昨日涨停今表现」「炸板率」；MOD-SIG-025 YesterdayLimitUpPerformance 生产侧）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 双池封闭 sealed（昨封板=limit_up_down）/broken（昨炸板=高≥涨停价且收<涨停价，kline_daily×stk_limit 联算）；今日表现=kline_daily.pct_change 直读；市场炸板率=(attempted-sealed)/attempted（attempted=0 → None 守卫）；symbol 归一裸 6 位码关联；单腿异常独立降级 notes 不炸；PIT（全部数据 ≤ trade_date）；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-19 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] trade_date/prev_trade_date 非法→ValueError（fail-closed）；查询异常/客户端不可得→对应腿降级 notes 留痕不抛
# [TESTS] tests/signal_ashare/test_limit_up_followthrough.py
# [A_module] module_id=MOD-SIG-078 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-078 — 昨日涨停今表现 + 炸板率统计（GAP-F-19，情绪页指标卡后端）。

日频统计任务（MVP）三腿：
- **昨封板池今表现**：c1_market.limit_up_down（T-1，limit_type='涨停'）×
  kline_daily（T）pct_change → 均值/中位/正负占比/双端榜（MOD-SIG-025
  YesterdayLimitUpPerformance 的生产侧——消费侧 dataclass 已在码，本模块产出）。
- **昨炸板池今表现**：昨 kline_daily.high ≥ stk_limit.limit_up 且 close < limit_up
  （盘中触板收盘未封）的个股池 × 今日表现——炸板次日接力/核按钮生态观测。
- **市场炸板率**：market_breadth_snapshot 当日最后一分钟快照
  (attempted − sealed)/attempted（字段在码复用，attempted=0 → None 守卫）。

口径写清：封板池与炸板池互斥（收盘是否封板二分）；symbol 归一裸 6 位码关联
（limit_up_down symbol 可能为裸码或 canonical，kline/stk_limit 侧用
symbol_canonical 取裸码）；今日缺数据的票跳过不计入统计+notes 留痕；
超额=封板池均值 − 指数涨幅（注入位，None 不算）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 昨封板池 list[PoolStock]（limit_up_down）
# - id: I2 昨炸板池 list[PoolStock]（kline_daily×stk_limit 联算）
# - id: I3 今日涨跌幅 dict[symbol → pct_change]（kline_daily）
# - id: I4 市场宽度 (attempted, sealed)（market_breadth_snapshot 末快照）
# 层: 算法
# - id: A1 双池×今日表现 join（裸码键）→ 分组统计
# - id: A2 市场炸板率 + 超额收益
# 层: 输出
# - id: O1 LimitUpFollowthroughReport（双池统计+市场炸板率+双端榜）
# [/ALGO_FLOW]
#
# 边:
# I1,I3 --> A1
# I2,I3 --> A1
# I4 --> A2
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "FollowthroughConfig",
    "LimitUpFollowthroughReport",
    "PoolPerformance",
    "PoolStock",
    "StockFollowDetail",
    "compute_followthrough_stats",
    "run_limit_up_followthrough",
]

# ------------------------------------------------------------------
# 常量（SQL 集中化 §5.160.2）
# ------------------------------------------------------------------

#: 昨封板池（limit_up_down 仅 涨停/跌停 两类）
SQL_SEALED_POOL: Final = """
SELECT symbol, name, close
FROM c1_market.limit_up_down
WHERE trade_date = %(trade_date)s AND limit_type = %(limit_type)s
"""

#: 昨炸板池（kline_daily×stk_limit 联算：高≥涨停价 且 收<涨停价；symbol_canonical 关联）
SQL_BROKEN_POOL: Final = """
SELECT k.symbol_canonical, k.high, k.close, s.limit_up
FROM c1_market.kline_daily AS k
INNER JOIN c1_market.stk_limit AS s
  ON k.symbol_canonical = s.symbol_canonical AND s.trade_date = k.trade_date
WHERE k.trade_date = %(trade_date)s AND k.quality_flag = 1
  AND s.limit_up IS NOT NULL AND s.limit_up > 0
  AND k.high >= s.limit_up AND k.close < s.limit_up
"""

#: 今日全市场涨跌幅（单日 ~5400 行，Python 侧 join）
SQL_TODAY_PCT: Final = """
SELECT symbol_canonical, pct_change
FROM c1_market.kline_daily
WHERE trade_date = %(trade_date)s AND quality_flag = 1
"""

#: 市场炸板率源（当日最后一分钟快照；attempted/sealed 字段在码复用）
SQL_BREADTH_LAST: Final = """
SELECT attempted, sealed, degraded
FROM c1_market.market_breadth_snapshot
WHERE trade_date = %(trade_date)s
ORDER BY ts DESC
LIMIT 1
"""

_POOL_SEALED: Final[str] = "sealed"
_POOL_BROKEN: Final[str] = "broken"


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FollowthroughConfig:
    """统计配置（MVP 初拍值）。"""

    limit_type: str = "涨停"  # limit_up_down.limit_type 过滤值
    top_n: int = 10  # 双端榜各取条数
    index_pct_change: float | None = None  # 指数当日涨幅 %（超额口径注入位，None 不算）


@dataclass(frozen=True, slots=True)
class PoolStock:
    """池内个股（昨封板/昨炸板）。"""

    symbol: str  # 裸码或 canonical（内部归一裸码）
    name: str = ""
    y_close: float = 0.0  # 昨收（留痕）


@dataclass(frozen=True, slots=True)
class PoolPerformance:
    """单池今日表现统计。"""

    pool: str  # sealed/broken
    count: int = 0  # 有效统计票数（今日缺数据跳过）
    avg_pct: float = 0.0
    median_pct: float = 0.0
    positive_ratio: float = 0.0
    max_pct: float = 0.0
    min_pct: float = 0.0


@dataclass(frozen=True, slots=True)
class StockFollowDetail:
    """个股今表现明细（双端榜行）。"""

    symbol: str
    name: str
    pool: str
    pct_change: float


@dataclass(frozen=True, slots=True)
class LimitUpFollowthroughReport:
    """昨日涨停今表现+炸板率统计输出（观测层消费，不接交易）。"""

    date: str
    prev_date: str
    sealed: PoolPerformance = field(default_factory=lambda: PoolPerformance(pool=_POOL_SEALED))
    broken: PoolPerformance = field(default_factory=lambda: PoolPerformance(pool=_POOL_BROKEN))
    market_attempted: int = 0
    market_sealed: int = 0
    market_broken_rate: float | None = None  # (attempted-sealed)/attempted；无宽度数据/attempted=0 → None
    excess_avg_pct: float | None = None  # 封板池均值−指数涨幅（index_pct_change 注入才算）
    top_gainers: list[StockFollowDetail] = field(default_factory=list)
    top_losers: list[StockFollowDetail] = field(default_factory=list)
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def _bare(code: str) -> str:
    """symbol 归一裸 6 位码（去 .SH/.SZ/.BJ 后缀+小写交易所前缀）。"""
    c = str(code).strip()
    if "." in c:
        c = c.split(".")[0]
    for pre in ("sh", "sz", "bj"):
        if c.lower().startswith(pre):
            c = c[len(pre) :]
            break
    return c


def _validate_date_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} 非法（须 YYYY-MM-DD 字符串）: {value!r}")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} 非真实日期: {value!r}") from exc
    return value


def _pool_stats(
    pool: str, stocks: list[PoolStock], today_pct: Mapping[str, float], notes: list[str]
) -> tuple[PoolPerformance, list[StockFollowDetail]]:
    vals: list[float] = []
    details: list[StockFollowDetail] = []
    for s in stocks:
        bare = _bare(s.symbol)
        pct = today_pct.get(bare)
        if pct is None:
            notes.append(f"{bare}（{s.name}）今日缺 kline_daily 数据，跳过统计")
            continue
        vals.append(float(pct))
        details.append(StockFollowDetail(symbol=bare, name=s.name, pool=pool, pct_change=round(float(pct), 4)))
    if not vals:
        return PoolPerformance(pool=pool), details
    perf = PoolPerformance(
        pool=pool,
        count=len(vals),
        avg_pct=round(sum(vals) / len(vals), 4),
        median_pct=round(statistics.median(vals), 4),
        positive_ratio=round(sum(1 for v in vals if v > 0) / len(vals), 4),
        max_pct=round(max(vals), 4),
        min_pct=round(min(vals), 4),
    )
    return perf, details


def compute_followthrough_stats(
    trade_date: str,
    prev_trade_date: str,
    sealed_pool: list[PoolStock],
    broken_pool: list[PoolStock],
    today_pct: Mapping[str, float],
    breadth_attempted: int | None,
    breadth_sealed: int | None,
    config: FollowthroughConfig | None = None,
) -> LimitUpFollowthroughReport:
    """统计主核（纯函数，不触库）。

    Args:
        trade_date: 数据日 T（YYYY-MM-DD，fail-closed）。
        prev_trade_date: 前一交易日 T-1（YYYY-MM-DD，fail-closed）。
        sealed_pool: 昨封板池（limit_up_down）。
        broken_pool: 昨炸板池（kline_daily×stk_limit 联算）。
        today_pct: 今日涨跌幅 {裸码或 canonical: pct_change}（内部归一裸码）。
        breadth_attempted/breadth_sealed: 市场宽度末快照（None=宽度腿缺失降级）。
        config: 配置（None 用默认）。

    Returns:
        LimitUpFollowthroughReport；双池全空 → degraded。
    """
    v_date = _validate_date_str(trade_date, "trade_date")
    v_prev = _validate_date_str(prev_trade_date, "prev_trade_date")
    cfg = config or FollowthroughConfig()
    notes: list[str] = []

    norm_today = {_bare(k): float(v) for k, v in today_pct.items()}
    sealed_perf, sealed_details = _pool_stats(_POOL_SEALED, list(sealed_pool), norm_today, notes)
    broken_perf, broken_details = _pool_stats(_POOL_BROKEN, list(broken_pool), norm_today, notes)

    attempted = None if breadth_attempted is None else int(breadth_attempted)
    sealed_n = None if breadth_sealed is None else int(breadth_sealed)
    broken_rate: float | None = None
    if attempted is None or sealed_n is None:
        notes.append("市场宽度末快照缺失（market_breadth_snapshot 腿降级），炸板率不出")
    elif attempted <= 0:
        notes.append("当日曾涨停为 0，炸板率不适用（None）")
    else:
        broken_rate = round((attempted - sealed_n) / attempted, 4)

    excess: float | None = None
    if cfg.index_pct_change is not None and sealed_perf.count > 0:
        excess = round(sealed_perf.avg_pct - float(cfg.index_pct_change), 4)

    all_details = sealed_details + broken_details
    gainers = sorted(all_details, key=lambda d: (-d.pct_change, d.symbol))[: cfg.top_n]
    losers = sorted(all_details, key=lambda d: (d.pct_change, d.symbol))[: cfg.top_n]

    degraded = sealed_perf.count == 0 and broken_perf.count == 0
    if degraded:
        notes.append("双池皆空或全无今日数据，整体降级")
    return LimitUpFollowthroughReport(
        date=v_date,
        prev_date=v_prev,
        sealed=sealed_perf,
        broken=broken_perf,
        market_attempted=attempted or 0,
        market_sealed=sealed_n or 0,
        market_broken_rate=broken_rate,
        excess_avg_pct=excess,
        top_gainers=gainers,
        top_losers=losers,
        degraded=degraded,
        notes=notes,
    )


# ------------------------------------------------------------------
# 主入口（薄加载层，ch_client 注入可 mock）
# ------------------------------------------------------------------


def _normalize_dt(trade_date: str | date | datetime) -> date:
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client() -> Any | None:
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，涨停今表现统计降级", exc_info=True)
        return None


def run_limit_up_followthrough(
    trade_date: str | date | datetime,
    prev_trade_date: str | date | datetime,
    ch_client: Any | None = None,
    config: FollowthroughConfig | None = None,
    *,
    _allow_no_client: bool = False,
) -> LimitUpFollowthroughReport:
    """主入口：昨日涨停今表现+炸板率统计（日频任务）。

    Args:
        trade_date: 数据日 T；prev_trade_date: 前一交易日 T-1（调用方经交易日历解析）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取默认客户端
            （_allow_no_client=True 时客户端不可得→degraded 不抛，测试用）。
        config: 配置（None 用默认）。

    Returns:
        LimitUpFollowthroughReport；单腿异常独立降级（notes 留痕）。
    """
    cfg = config or FollowthroughConfig()
    current = _normalize_dt(trade_date)  # ValueError fail-closed
    prev = _normalize_dt(prev_trade_date)
    date_str, prev_str = current.isoformat(), prev.isoformat()
    notes: list[str] = []

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        if not _allow_no_client:
            raise ValueError("ch_client 不可得（须注入或默认客户端可用）")
        return LimitUpFollowthroughReport(
            date=date_str,
            prev_date=prev_str,
            degraded=True,
            notes=["CH 客户端不可得，涨停今表现统计整体降级"],
        )

    sealed_pool: list[PoolStock] = []
    broken_pool: list[PoolStock] = []
    today_pct: dict[str, float] = {}
    attempted: int | None = None
    sealed_n: int | None = None

    try:
        rows = client.execute(SQL_SEALED_POOL, {"trade_date": prev, "limit_type": cfg.limit_type})
        sealed_pool = [PoolStock(symbol=str(r[0]), name=str(r[1]), y_close=float(r[2])) for r in rows]
    except Exception as e:  # noqa: BLE001 — 封板池腿降级
        notes.append(f"limit_up_down 查询异常，封板池腿降级: {e!r}")
    try:
        rows = client.execute(SQL_BROKEN_POOL, {"trade_date": prev})
        broken_pool = [PoolStock(symbol=str(r[0]), y_close=float(r[2])) for r in rows]
    except Exception as e:  # noqa: BLE001 — 炸板池腿降级
        notes.append(f"kline_daily×stk_limit 联算异常，炸板池腿降级: {e!r}")
    try:
        rows = client.execute(SQL_TODAY_PCT, {"trade_date": current})
        today_pct = {str(r[0]): float(r[1]) for r in rows}
    except Exception as e:  # noqa: BLE001 — 今日表现腿降级
        notes.append(f"kline_daily 查询异常，今日表现腿降级: {e!r}")
    try:
        rows = client.execute(SQL_BREADTH_LAST, {"trade_date": current})
        if rows:
            attempted, sealed_n = int(rows[0][0]), int(rows[0][1])
        else:
            notes.append("market_breadth_snapshot 当日无快照，市场炸板率不出")
    except Exception as e:  # noqa: BLE001 — 宽度腿降级
        notes.append(f"market_breadth_snapshot 查询异常，宽度腿降级: {e!r}")

    rep = compute_followthrough_stats(
        date_str,
        prev_str,
        sealed_pool,
        broken_pool,
        today_pct,
        attempted,
        sealed_n,
        cfg,
    )
    return LimitUpFollowthroughReport(
        date=rep.date,
        prev_date=rep.prev_date,
        sealed=rep.sealed,
        broken=rep.broken,
        market_attempted=rep.market_attempted,
        market_sealed=rep.market_sealed,
        market_broken_rate=rep.market_broken_rate,
        excess_avg_pct=rep.excess_avg_pct,
        top_gainers=rep.top_gainers,
        top_losers=rep.top_losers,
        degraded=rep.degraded,
        notes=notes + rep.notes,
    )
