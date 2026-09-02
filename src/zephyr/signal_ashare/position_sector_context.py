# [BLUEPRINT] MOD-SIG-065 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-30 + 45号作战手册 §5 数据契约）
# [MODULE] zephyr.signal_ashare.position_sector_context
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.mainline_probability（MOD-SIG-064 复用）; zephyr.signal_ashare.sector_leader（MOD-SIG-062 复用）; c1_market.sector_constituent（只读）; c1_market.kline_sector_880（只读，最新数据日解析）
# [CONSUMERS] （持仓监控页"所属板块"列 GAP-F-30 前端接线；45号 W2b 持仓股边界语境）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 观测先行纪律：只出关联语境（板块归属/主线概率/排名/板内角色），不接交易/不出买卖点；PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）；主线概率/梯队角色缺失独立降级互不累及；positions 必须调用方显式供给（ClickHouse 无持仓表真源，CTR-P1-008 券商通道未接）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-30 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] positions=None→ValueError（调用方契约违例，fail-closed）；trade_date 格式非法→ValueError；sector_constituent 查询异常→degraded=True 空结果不炸；主线概率/龙头榜降级→对应字段 None+notes 留痕不抛；非法 symbol→跳过+notes 留痕
# [TESTS] tests/signal_ashare/test_position_sector_context.py
# [A_module] module_id=MOD-SIG-065 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-065 — 持仓×板块语境关联查询（GAP-F-30，持仓监控页"所属板块"列后端接口）。

关联链（全部复用已在码产出）：
  持仓股（调用方显式供给 positions，CH 无持仓表真源）→ sector_constituent SCD-2
  时点板块归属 → MOD-SIG-064 主线概率/排名（板块 Top10 同一真源）→ MOD-SIG-062
  板内角色（龙头/中军/跟风/中位股）+ 龙头连板高度。

输出每票：板块语境清单（sector_code/名称/主线概率%/主线排名/板内角色/龙头连板数）
+ best_sector（主线概率最高归属板块）。多板块归属全部列出（一股多板属设计内）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓清单（调用方供给）
#   fields: symbol/weight
# - id: I2
#   name: 板块成分映射（sector_constituent，SCD-2 时点有效）
#   fields: sector_code/stock_code
# - id: I3
#   name: MOD-SIG-064 主线概率榜（复用产出）
#   fields: items(sector_code/sector_name/probability_pct)/degraded
# - id: I4
#   name: MOD-SIG-062 龙头识别榜（复用产出）
#   fields: sectors(sector_code/leader/backbones/followers/neutrals)
# 层: 算法
# - id: A1
#   name_zh: 持仓×板块×角色关联
#   desc: symbol 归一化 → 成分反查板块 → 概率/排名/角色三源挂接 → best_sector 选取
# 层: 输出
# - id: O1
#   name_zh: PositionSectorContextResult
#   intro: date/items(symbol/sectors[]/best_sector_code)/degraded/notes/annotations；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final

from zephyr.signal_ashare.mainline_probability import (
    MainlineProbabilityResult,
    compute_mainline_probability,
)
from zephyr.signal_ashare.sector_leader import (
    SectorLeaderBoard,
    identify_sector_leaders,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "PositionHoldingInput",
    "PositionSectorContextItem",
    "PositionSectorContextResult",
    "PositionSectorEntry",
    "query_position_sector_context",
]

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_LATEST_SECTOR_DATE: Final = """
SELECT max(trade_date)
FROM c1_market.kline_sector_880
WHERE period = '1d'
"""

SQL_SECTOR_CONSTITUENTS: Final = """
SELECT sector_code, stock_code
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
"""


@dataclass(frozen=True, slots=True)
class PositionHoldingInput:
    """持仓输入条目（调用方显式供给——CH 无持仓表真源，CTR-P1-008 未接）。"""

    symbol: str  # 6 位裸码或 canonical（600000 / 600000.SH）
    weight: float | None = None  # 持仓权重 ∈ [0,1]（可选，透传给前端排序）
    name: str = ""  # 名称（可选透传）


@dataclass(frozen=True, slots=True)
class PositionSectorEntry:
    """单票单板块语境行。"""

    sector_code: str
    sector_name: str  # 主线概率榜名称映射，缺失回退代码
    mainline_probability_pct: float | None  # MOD-SIG-064 合成评分；榜降级/未入榜 → None
    mainline_rank: int | None  # 主线概率榜 1 基排名；未入榜 → None
    role_in_sector: str | None  # MOD-SIG-062 四档（leader/backbone/follower/neutral）；无记录 → None
    leader_consec: int | None  # 该股连板高度（MOD-SIG-062 透传）；无记录 → None


@dataclass(frozen=True, slots=True)
class PositionSectorContextItem:
    """单票板块语境（多板块归属全列 + 最优归属）。"""

    symbol: str  # canonical
    weight: float | None = None
    name: str = ""
    sectors: list[PositionSectorEntry] = field(default_factory=list)
    best_sector_code: str | None = None  # 主线概率最高归属板块（无概率 → None）
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class PositionSectorContextResult:
    """持仓×板块语境输出契约（查询接口，观测层消费）。"""

    date: str  # 数据日 YYYY-MM-DD
    items: list[PositionSectorContextItem] = field(default_factory=list)
    degraded: bool = False  # 成分映射不可用 → True
    annotations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _as_date(v: Any) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else _normalize_date(v)


def _default_client() -> Any | None:
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，持仓板块语境降级", exc_info=True)
        return None


def _to_canonical(symbol: str) -> str | None:
    """6 位裸码 → canonical（前缀推导交易所）；非法输入 → None（调用方留痕跳过）。"""
    s = str(symbol).strip().upper()
    if "." in s:
        code, _, exch = s.partition(".")
        if len(code) == 6 and code.isdigit() and exch in ("SH", "SZ", "BJ"):
            return s
        return None
    if len(s) != 6 or not s.isdigit():
        return None
    if s[0] in ("5", "6", "9"):
        return f"{s}.SH"
    if s[0] in ("0", "1", "2", "3"):
        return f"{s}.SZ"
    if s[0] in ("4", "8"):
        return f"{s}.BJ"
    return None


def query_position_sector_context(
    trade_date: str | date | datetime | None = None,
    positions: list[PositionHoldingInput] | None = None,
    ch_client: Any | None = None,
    probability_result: MainlineProbabilityResult | None = None,
    leader_board: SectorLeaderBoard | None = None,
) -> PositionSectorContextResult:
    """主入口：持仓×板块语境关联查询（供前端持仓监控页接线）。

    Args:
        trade_date: 数据日；None 时取 kline_sector_880 最新数据日（PIT 口径）。
        positions: 持仓清单（必须显式供给；None → ValueError fail-closed）。
        ch_client: clickhouse-driver 鸭子类型；None 时延迟取默认客户端。
        probability_result: 预计算 MOD-SIG-064 主线概率榜（注入位）；None 现算。
        leader_board: 预计算 MOD-SIG-062 龙头榜（注入位）；None 现算。

    Returns:
        PositionSectorContextResult；成分映射查询异常 → degraded=True 空结果不炸；
        主线概率/龙头榜降级 → 对应字段 None + notes 留痕。

    Raises:
        ValueError: positions=None 或 trade_date 格式非法（调用方契约违例）。
    """
    if positions is None:
        raise ValueError("positions 必须显式供给（ClickHouse 无持仓表真源，CTR-P1-008 券商通道未接）")

    notes: list[str] = []
    annotations: list[str] = []

    client = ch_client if ch_client is not None else _default_client()

    if trade_date is not None:
        d = _normalize_date(trade_date)  # ValueError fail-closed
    elif probability_result is not None:
        d = _normalize_date(probability_result.date)
    elif client is not None:
        try:
            latest = client.execute(SQL_LATEST_SECTOR_DATE, {})
        except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
            return PositionSectorContextResult(date="unknown", degraded=True, notes=[f"最新板块数据日查询异常: {e!r}"])
        if not latest or latest[0][0] is None:
            return PositionSectorContextResult(
                date="unknown", degraded=True, notes=["kline_sector_880 无任何日 K 数据"]
            )
        d = _as_date(latest[0][0])
    else:
        return PositionSectorContextResult(
            date="unknown", degraded=True, notes=["ch_client 不可用且未给 trade_date，无法解析数据日"]
        )
    date_str = d.isoformat()

    # ── 持仓 symbol 归一化（非法跳过留痕） ──
    holdings: list[tuple[str, PositionHoldingInput]] = []
    for pos in positions:
        canon = _to_canonical(pos.symbol)
        if canon is None:
            notes.append(f"非法 symbol 跳过: {pos.symbol!r}")
            continue
        holdings.append((canon, pos))
    if not holdings:
        annotations.append("空仓（持仓清单为空），无板块语境可关联")
        return PositionSectorContextResult(
            date=date_str, items=[], degraded=False, annotations=annotations, notes=notes
        )

    # ── 板块归属反查（成分 SCD-2，degraded 主链） ──
    if client is None:
        return PositionSectorContextResult(date=date_str, degraded=True, notes=["ch_client 不可用，板块归属反查降级"])
    try:
        rows = client.execute(SQL_SECTOR_CONSTITUENTS, {"trade_date": d})
    except Exception as e:  # noqa: BLE001 — 主数据异常 → degraded 空结果不炸
        logger.warning("sector_constituent 查询异常，持仓板块语境降级: %r", e)
        return PositionSectorContextResult(date=date_str, degraded=True, notes=[f"sector_constituent 查询异常: {e!r}"])
    held = {sym for sym, _ in holdings}
    symbol_sectors: dict[str, list[str]] = {sym: [] for sym in held}
    for row in rows:
        code, stock = str(row[0]), str(row[1])
        if stock in held:
            symbol_sectors[stock].append(code)

    # ── 主线概率榜（独立降级） ──
    prob = probability_result
    if prob is None:
        try:
            prob = compute_mainline_probability(date_str, ch_client=client)
        except Exception as e:  # noqa: BLE001 — 概率维独立降级
            notes.append(f"主线概率计算异常，概率/排名字段缺位: {e!r}")
            prob = None
    prob_map: dict[str, tuple[float | None, int]] = {}
    name_map: dict[str, str] = {}
    if prob is not None and not prob.degraded:
        for idx, item in enumerate(prob.items, start=1):
            prob_map[item.sector_code] = (item.probability_pct, idx)
            name_map[item.sector_code] = item.sector_name
    else:
        notes.append("主线概率榜降级/缺失，概率与排名字段缺位")

    # ── 龙头榜角色（独立降级） ──
    board = leader_board
    if board is None:
        try:
            board = identify_sector_leaders(date_str, ch_client=client)
        except Exception as e:  # noqa: BLE001 — 角色维独立降级
            notes.append(f"龙头识别计算异常，板内角色字段缺位: {e!r}")
            board = None
    role_map: dict[tuple[str, str], tuple[str, int]] = {}
    if board is not None and not board.degraded:
        for group in board.sectors:
            for entry in [group.leader, *group.backbones, *group.followers, *group.neutrals]:
                if entry is not None:
                    role_map[(group.sector_code, entry.symbol)] = (entry.role, entry.consec_limit)
    else:
        notes.append("龙头识别榜降级/缺失，板内角色字段缺位")

    # ── 关联组装 ──
    items: list[PositionSectorContextItem] = []
    for canon, pos in holdings:
        entries: list[PositionSectorEntry] = []
        for sector_code in sorted(symbol_sectors.get(canon) or []):
            pct, rank = prob_map.get(sector_code, (None, 0))
            role_info = role_map.get((sector_code, canon))
            entries.append(
                PositionSectorEntry(
                    sector_code=sector_code,
                    sector_name=name_map.get(sector_code, sector_code),
                    mainline_probability_pct=pct,
                    mainline_rank=rank if rank > 0 else None,
                    role_in_sector=role_info[0] if role_info else None,
                    leader_consec=role_info[1] if role_info else None,
                )
            )
        best: str | None = None
        scored = [e for e in entries if e.mainline_probability_pct is not None]
        if scored:
            best = max(scored, key=lambda e: (e.mainline_probability_pct, e.sector_code)).sector_code
        item_notes: list[str] = []
        if not entries:
            item_notes.append("无板块归属（sector_constituent 当日有效成分未覆盖该股）")
        items.append(
            PositionSectorContextItem(
                symbol=canon,
                weight=pos.weight,
                name=pos.name,
                sectors=entries,
                best_sector_code=best,
                notes=item_notes,
            )
        )

    annotations.append(f"持仓 {len(items)} 票板块语境已关联（归属/主线概率/板内角色三源）")
    return PositionSectorContextResult(
        date=date_str,
        items=items,
        degraded=False,
        annotations=annotations,
        notes=notes,
    )
