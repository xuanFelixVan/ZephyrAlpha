# [BLUEPRINT] MOD-SIG-142 | docs/03_modules/_domain_signal/blueprint.md | §
# [MODULE] zephyr.signal_ashare.core.analysis_utils
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.table_registry（延迟导入）；zephyr.data.ch_reader（延迟导入）——纯函数路径零 DB 依赖
# [CONSUMERS] zephyr.signal_ashare.mainline_candidates / mainline_probability / position_sector_context /
#   adjustment_cycle_tracker / sector.sector_leader / sector.sector_divergence /
#   ml_forecast.next_day_8state_forecast / ml_forecast.regime_change_detector（8 宿主别名赋值消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 台账只读（本模块零写入零 DB 常连——table_registry/ch_reader 均为调用点延迟导入）；
#   逐字节等价合并真源（2026-09-13 DEDUP 批 AST 实证），宿主以别名赋值保持调用点不变，禁宿主再复制
# [MODIFY-GUARD] 新增共享原语须先证两宿主以上重复（DEDUP 门槛）；修改函数签名须全宿主同 commit 适配
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数异常=宿主契约（ValueError 非法日期格式等）；延迟导入失败=宿主 fail-fast
# [TESTS] tests/signal_ashare/sector/test_sector_leader.py; tests/signal_ashare/sector/test_sector_divergence.py; tests/signal_ashare/test_mainline_candidates.py; tests/signal_ashare/test_mainline_probability.py
# [A_module] module_id=MOD-SIG-142 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""signal_ashare 域内共享分析原语（2026-09-13 DEDUP 批：6 组 15 副本克隆合并落点）。

提取自 mainline_candidates / mainline_probability / position_sector_context /
sector_leader / sector_divergence / adjustment_cycle_tracker /
next_day_8state_forecast / regime_change_detector 的逐字节等价副本（AST 实证）。
宿主文件以别名赋值（`_as_date = analysis_utils.as_date`）保持内部调用点不变。
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Callable


def normalize_trade_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def as_date(v: object) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else normalize_trade_date(v)  # type: ignore[arg-type]


def daily_returns(series: list[tuple[date, float, float]]) -> dict[date, float]:
    """(日期, 收盘, 成交额) 序列 → {日期: 日收益}（相邻收盘比，基准 ≤0 跳过）。"""
    out: dict[date, float] = {}
    for i in range(1, len(series)):
        prev_close = series[i - 1][1]
        if prev_close > 0:
            out[series[i][0]] = series[i][1] / prev_close - 1.0
    return out


def lead_streaks(leaders: dict[date, str], sorted_dates: list[date]) -> dict[date, int]:
    """逐日连续领涨天数（同一板块截至当日连续领涨日数；当日无领涨 → 不出键）。"""
    streaks: dict[date, int] = {}
    prev_leader: str | None = None
    streak = 0
    for dd in sorted_dates:
        leader = leaders.get(dd)
        if leader is None:
            prev_leader = None
            streak = 0
            continue
        streak = streak + 1 if leader == prev_leader else 1
        prev_leader = leader
        streaks[dd] = streak
    return streaks


def rotation_speeds(amounts: dict[str, dict[date, float]], sorted_dates: list[date]) -> dict[date, float]:
    """逐日轮动速度 = 0.5 × Σ|今日成交额占比 − 昨日占比|（22号 §3.1⑨ fast_rotation 口径）。"""
    speeds: dict[date, float] = {}
    prev_shares: dict[str, float] | None = None
    for dd in sorted_dates:
        today = {c: amap[dd] for c, amap in amounts.items() if dd in amap}
        total = sum(today.values())
        shares = {c: a / total for c, a in today.items()} if total > 0 else {}
        if prev_shares is not None and shares:
            codes = set(shares) | set(prev_shares)
            speeds[dd] = 0.5 * sum(abs(shares.get(c, 0.0) - prev_shares.get(c, 0.0)) for c in codes)
        prev_shares = shares
    return speeds


def resolve_registry(registry: object) -> object:
    """TableRegistry 解析（None → get_registry() 单例；TableRegistry.table 的 SSoT 入口）。"""
    if registry is None:
        from zephyr.data.table_registry import get_registry  # 延迟导入，保持纯函数路径零 DB 依赖

        return get_registry()
    return registry


def resolve_table(registry: object, category_id: str = "market_index_kline") -> str:
    """解析全限定表名（adjustment_cycle_tracker/next_day_8state_forecast/regime_change_detector 公共路径）。"""
    return resolve_registry(registry).table(category_id)  # type: ignore[attr-defined]


def resolve_query_fn(query_fn: Callable[..., str] | None) -> Callable[..., str]:
    """CH 查询函数解析（显式注入优先，缺省 ch_reader.query）。"""
    if query_fn is not None:
        return query_fn
    from zephyr.data import ch_reader  # 延迟导入，保持纯函数路径零 DB 依赖

    return ch_reader.query
