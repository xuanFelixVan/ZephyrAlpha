# [BLUEPRINT] MOD-SIG-071 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-15 行）
# [MODULE] zephyr.signal_ashare.index_contribution_decomposer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.kline_sector_intraday（只读）; c1_market.index_quote（只读，3秒快照重采样分钟）
# [CONSUMERS] （候选：板块页贡献度图+表、GAP-F-16 逆势榜前置）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 贡献恒等式：Σ板块贡献+残差=指数分钟涨跌（逐分钟成立，权重归一到 weight_sum_target）；指数分钟序列=index_quote 3秒快照分钟末价重采样（无独立指数分钟表，留痕口径）；权重未供给→等权降级（weight_mode=equal_weights 留痕）；分钟缺板该板块该分钟计 0 贡献+覆盖计数；PIT（全部数据 ≤ trade_date）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-15 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可得→对应腿降级 notes 留痕不抛；trade_date 格式非法→ValueError（fail-closed）；指数序列 <2 点→degraded 不出伪拆解
# [TESTS] tests/signal_ashare/test_index_contribution_decomposer.py
# [A_module] module_id=MOD-SIG-071 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-071 — 大盘分时贡献度拆解（GAP-F-15，板块页贡献度图+表后端）。

分钟级板块-指数贡献管线（MVP）：

- **指数分钟序列**：c1_market.index_quote 3 秒快照按分钟桶取末价重采样
  （库内无独立指数分钟 K 线表，重采样口径 notes 留痕）。
- **板块分钟收益**：c1_market.kline_sector_intraday（880xxx 板块 1m/5m 族，默认 1m）
  逐分钟对前收收益。
- **贡献分摊**：contribution[sector,t] = weight[sector] × sector_ret[t]；
  恒等式 Σw·r + residual = index_ret 逐分钟成立（residual=未被板块权重覆盖部分）。
- **权重**：注入位（如沪深300板块权重）；未注入→等权归一（weight_mode=equal_weights，
  明确降级留痕——等权是近似口径，不代表真实指数权重）。
- **日聚合**：板块日贡献=分钟贡献线性求和（近似口径，文档明文化）；
  板块日榜按贡献降序（正贡献榜）+ 升序（负贡献榜）供前端双端展示。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 指数分钟序列 list[(ts, price)]（index_quote 重采样）
# - id: I2 板块分钟价 dict[sector_code → list[(ts, close)]]（kline_sector_intraday）
# - id: I3 板块权重 dict[sector_code → weight]（注入位；None=等权降级）
# 层: 特征
# - id: F1 分钟收益（指数/板块 对前一分钟收盘）
# - id: F2 权重归一（Σw=weight_sum_target）
# 层: 算法
# - id: A1 逐分钟贡献分摊+残差（恒等式）
# - id: A2 日聚合（分钟贡献线性求和）+ 双端榜
# 层: 输出
# - id: O1 IndexContributionResult（minutes 逐分钟拆解 + sector_board 日榜 + 残差）
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1
# I2 --> F1
# I3 --> F2
# F1,F2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "ContributionConfig",
    "IndexContributionResult",
    "MinuteContributionPoint",
    "SectorContributionItem",
    "decompose_index_contribution",
    "decompose_intraday_contribution",
    "resample_quotes_to_minute",
]

# ------------------------------------------------------------------
# 常量（SQL 集中化 §5.160.2）
# ------------------------------------------------------------------

#: 指数 3 秒快照（index_quote，重采样分钟末价）
SQL_INDEX_QUOTES: Final = """
SELECT timestamp, price
FROM c1_market.index_quote
WHERE trade_date = %(trade_date)s AND symbol = %(symbol)s AND quality_flag = 1
ORDER BY timestamp
"""

#: 板块分钟 K 线（kline_sector_intraday，trade_date 为 DateTime）
SQL_SECTOR_MINUTE: Final = """
SELECT trade_date, code, close
FROM c1_market.kline_sector_intraday
WHERE toDate(trade_date) = %(trade_date)s AND period = %(period)s
ORDER BY code, trade_date
"""


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ContributionConfig:
    """贡献度拆解配置（MVP 初拍值，可配常量）。"""

    index_symbol: str = "000001.SH"  # 默认上证指数
    sector_period: str = "1m"  # 板块分钟周期（kline_sector_intraday.period）
    weight_sum_target: float = 1.0  # 权重归一目标（Σw=1 → 残差=未覆盖口径）
    top_n: int = 10  # 日榜双端各取条数
    sector_names: Mapping[str, str] | None = None  # 板块名映射（注入位，展示用）


@dataclass(frozen=True, slots=True)
class MinuteContributionPoint:
    """逐分钟贡献拆解点。"""

    ts: str  # 分钟桶 YYYY-MM-DD HH:MM
    index_ret_pct: float  # 指数分钟涨跌 %
    sector_contrib_pct: dict[str, float] = field(default_factory=dict)  # 板块 → 贡献 %
    residual_pct: float = 0.0  # 残差 %（恒等式：Σ板块+残差=指数）


@dataclass(frozen=True, slots=True)
class SectorContributionItem:
    """板块日聚合贡献条目。"""

    sector_code: str
    sector_name: str
    weight: float
    day_ret_pct: float  # 板块日收益 %（首末分钟收盘）
    day_contribution_pct: float  # 板块日贡献 %（分钟贡献线性求和）
    covered_minutes: int  # 有板块分钟数据的分钟数（覆盖留痕）


@dataclass(frozen=True, slots=True)
class IndexContributionResult:
    """贡献度拆解输出契约（观测层消费，不接交易）。"""

    date: str
    index_symbol: str
    minutes: list[MinuteContributionPoint] = field(default_factory=list)
    sector_board: list[SectorContributionItem] = field(default_factory=list)  # 贡献降序
    total_index_move_pct: float = 0.0  # 指数全天涨跌 %（首末分钟）
    residual_day_pct: float = 0.0  # 全天残差 %
    weight_mode: str = "injected"  # injected / equal_weights
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def resample_quotes_to_minute(quotes: list[tuple[Any, float]]) -> list[tuple[str, float]]:
    """3 秒快照 → 分钟末价序列（分钟桶内最后一条；输出按分钟升序）。

    Args:
        quotes: [(timestamp, price)] 升序；timestamp 为 datetime 或 'YYYY-MM-DD HH:MM:SS'。

    Returns:
        [(分钟桶 'YYYY-MM-DD HH:MM', 末价)]；空输入 → 空列表。
    """
    last_per_minute: dict[str, float] = {}
    for ts, price in quotes:
        minute = str(ts)[:16]
        last_per_minute[minute] = float(price)  # 升序输入 → 后者覆盖 = 分钟末价
    return sorted(last_per_minute.items())


def _pct_returns(series: list[tuple[str, float]]) -> dict[str, float]:
    """分钟价序列 → 逐分钟收益 %（对前一分钟；首分钟无前值跳过）。"""
    out: dict[str, float] = {}
    for i in range(1, len(series)):
        prev = series[i - 1][1]
        if prev:
            out[series[i][0]] = (series[i][1] / prev - 1.0) * 100.0
    return out


def decompose_index_contribution(
    index_series: list[tuple[str, float]],
    sector_series: Mapping[str, list[tuple[str, float]]],
    weights: Mapping[str, float] | None = None,
    config: ContributionConfig | None = None,
) -> IndexContributionResult:
    """贡献拆解主核（纯函数，不触库）。

    Args:
        index_series: 指数分钟序列 [(ts, price)] 升序（resample_quotes_to_minute 产出）。
        sector_series: 板块分钟序列 {sector_code: [(ts, close)]} 升序。
        weights: 板块权重（注入位）；None → 等权归一降级（weight_mode=equal_weights）。
        config: 配置（None 用默认）。

    Returns:
        IndexContributionResult；指数序列 <2 点 → degraded 不出伪拆解。
    """
    cfg = config or ContributionConfig()
    notes: list[str] = []
    date_str = index_series[0][0][:10] if index_series else ""

    if len(index_series) < 2:
        return IndexContributionResult(
            date=date_str,
            index_symbol=cfg.index_symbol,
            degraded=True,
            notes=["指数分钟序列不足 2 点，不出伪拆解"],
        )

    # 权重归一
    sectors = sorted(sector_series)
    if weights:
        raw = {s: float(weights.get(s, 0.0)) for s in sectors}
        weight_mode = "injected"
    else:
        raw = {s: 1.0 for s in sectors}
        weight_mode = "equal_weights"
        notes.append("板块权重未供给，等权归一降级（近似口径，非真实指数权重）")
    wsum = sum(raw.values())
    norm: dict[str, float] = (
        {s: w / wsum * cfg.weight_sum_target for s, w in raw.items()} if wsum > 0 else dict.fromkeys(sectors, 0.0)
    )
    if wsum <= 0:
        notes.append("权重和为 0，全部板块权重置 0（贡献全落残差）")

    index_ret = _pct_returns(index_series)
    sector_ret = {s: _pct_returns(series) for s, series in sector_series.items()}

    minutes: list[MinuteContributionPoint] = []
    day_contrib: dict[str, float] = dict.fromkeys(sectors, 0.0)
    covered: dict[str, int] = dict.fromkeys(sectors, 0)
    for ts, idx_r in index_ret.items():
        contrib: dict[str, float] = {}
        for s in sectors:
            r = sector_ret[s].get(ts)
            if r is None:
                continue  # 该分钟板块缺数据 → 计 0 贡献（covered 留痕）
            c = norm[s] * r
            contrib[s] = round(c, 6)
            day_contrib[s] += c
            covered[s] += 1
        residual = idx_r - sum(contrib.values())
        minutes.append(
            MinuteContributionPoint(
                ts=ts,
                index_ret_pct=round(idx_r, 6),
                sector_contrib_pct=contrib,
                residual_pct=round(residual, 6),
            )
        )

    # 日聚合榜
    names = cfg.sector_names or {}
    board: list[SectorContributionItem] = []
    for s in sectors:
        series = sector_series[s]
        day_ret = (series[-1][1] / series[0][1] - 1.0) * 100.0 if len(series) >= 2 and series[0][1] else 0.0
        board.append(
            SectorContributionItem(
                sector_code=s,
                sector_name=names.get(s, ""),
                weight=round(norm[s], 6),
                day_ret_pct=round(day_ret, 4),
                day_contribution_pct=round(day_contrib[s], 6),
                covered_minutes=covered[s],
            )
        )
    board.sort(key=lambda b: (-b.day_contribution_pct, b.sector_code))

    total_move = 0.0
    if index_series[0][1]:
        total_move = (index_series[-1][1] / index_series[0][1] - 1.0) * 100.0
    residual_day = total_move - sum(day_contrib.values())
    return IndexContributionResult(
        date=date_str,
        index_symbol=cfg.index_symbol,
        minutes=minutes,
        sector_board=board,
        total_index_move_pct=round(total_move, 4),
        residual_day_pct=round(residual_day, 6),
        weight_mode=weight_mode,
        notes=notes,
    )


# ------------------------------------------------------------------
# 加载层（薄封装，ch_client 注入可 mock）
# ------------------------------------------------------------------


def _normalize_date(trade_date: str | date | datetime) -> date:
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
        logger.warning("ch_writer 默认客户端不可用，贡献度拆解降级", exc_info=True)
        return None


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------


def decompose_intraday_contribution(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
    config: ContributionConfig | None = None,
    index_series: list[tuple[str, float]] | None = None,
    sector_series: Mapping[str, list[tuple[str, float]]] | None = None,
    weights: Mapping[str, float] | None = None,
) -> IndexContributionResult:
    """主入口：分钟级板块-指数贡献拆解。

    Args:
        trade_date: 数据日（YYYY-MM-DD，PIT 上限）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取默认客户端。
        config: 配置（None 用默认；index_symbol/sector_period 在此指定）。
        index_series/sector_series: 测试/编排注入位；None 时经 client 现查
            （指数腿=index_quote 重采样；板块腿=kline_sector_intraday）。
        weights: 板块权重注入位；None 等权降级。

    Returns:
        IndexContributionResult；单腿异常独立降级（notes 留痕）；
        指数序列不足 → degraded。
    """
    cfg = config or ContributionConfig()
    current = _normalize_date(trade_date)  # ValueError fail-closed
    date_str = current.isoformat()
    notes: list[str] = []

    need_client = index_series is None or sector_series is None
    client = ch_client if ch_client is not None else (_default_client() if need_client else None)
    if need_client and client is None:
        return IndexContributionResult(
            date=date_str, index_symbol=cfg.index_symbol, degraded=True,
            notes=["CH 客户端不可得，贡献度拆解整体降级"],
        )

    if index_series is None:
        try:
            rows = client.execute(SQL_INDEX_QUOTES, {"trade_date": current, "symbol": cfg.index_symbol})
            index_series = resample_quotes_to_minute([(r[0], float(r[1])) for r in rows])
            notes.append("指数分钟序列=index_quote 3秒快照分钟末价重采样（无独立指数分钟表）")
        except Exception as e:  # noqa: BLE001 — 指数腿异常降级
            index_series = []
            notes.append(f"index_quote 查询异常，指数腿降级: {e!r}")
    if sector_series is None:
        try:
            rows = client.execute(
                SQL_SECTOR_MINUTE, {"trade_date": current, "period": cfg.sector_period}
            )
            by_sector: dict[str, list[tuple[str, float]]] = {}
            for r in rows:
                by_sector.setdefault(str(r[1]), []).append((str(r[0])[:16], float(r[2])))
            sector_series = by_sector
        except Exception as e:  # noqa: BLE001 — 板块腿异常降级
            sector_series = {}
            notes.append(f"kline_sector_intraday 查询异常，板块腿降级: {e!r}")

    result = decompose_index_contribution(index_series, sector_series, weights, cfg)
    merged_notes = notes + result.notes
    if not sector_series:
        merged_notes.append("板块分钟数据为空，贡献全落残差")
    return IndexContributionResult(
        date=result.date or date_str,
        index_symbol=result.index_symbol,
        minutes=result.minutes,
        sector_board=result.sector_board,
        total_index_move_pct=result.total_index_move_pct,
        residual_day_pct=result.residual_day_pct,
        weight_mode=result.weight_mode,
        degraded=result.degraded,
        notes=merged_notes,
    )
