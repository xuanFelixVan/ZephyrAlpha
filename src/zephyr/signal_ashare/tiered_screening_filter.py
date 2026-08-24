# [BLUEPRINT] MOD-SIG-046 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [MODULE] zephyr.signal_ashare.tiered_screening_filter
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.selection_funnel_skeleton（MOD-SIG-086 共享骨架）
# [CONSUMERS] zephyr.signal_ashare.coarse_screening_funnel; zephyr.signal_ashare.screening_funnel_report
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只排除不评分；kept ∩ excluded = ∅；降级路径仅做物理排除；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法板块枚举 → ValueError；prev_close<=0 → 该标的按 limit 状态不明放行并记 unknown_limit
# [TESTS] tests/signal_ashare/test_tiered_screening_filter.py
# [A_module] module_id=MOD-SIG-046 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: TieredFilterRecord（symbol/board/close/prev_close/停牌/ST/上市天数/日均成交额/弃庄概率）
# A1: limit_pct_for(board, is_st) → 板块涨跌停幅度（宪章§2约束四：主板±10%/科创创业±20%/ST±10%/北交所±30%）
# A2: is_limit_locked_price(close, prev_close, limit_pct) → 涨跌停封死推导（|涨幅|≥幅度−ε）
# A3: 四排除机制——委托骨架 run_graded_exclusion（板块幅度自推导经 is_limit_locked 钩子闭包注入）：物理(封死/停牌/ST)/门禁(次新<30天)/分级(日均成交额<500万)/概率(弃庄>0.95)
# O1: TieredFilterResult(kept/excluded{symbol:reason}/degraded)
# [/ALGO_FLOW]
"""选股漏斗第一层——分级指标过滤（BM-SEL-16，~7000→~1200）——A 股信号域薄适配层。

SIGNAL-ARCH-001 归并裁定落地：层序/接口/数据流唯一真源为
zephyr.signal_ashare.selection_funnel_skeleton（MOD-SIG-086 共享骨架），
本模块只保留 A 股域板块幅度表与记录/结果类型，四排除机制执行委托骨架，
对外公开 API 签名不变（既有调用方/测试零适配）。

本域注入特性（区别于 signal_fundamental/selection_funnel.py 的预计算布尔标记）：
自带 A 股板块涨跌停幅度表（宪章 §2 约束四：主板 ±10%/科创创业板 ±20%/ST ±10%/
北交所 ±30%），从原始 close/prev_close 推导涨跌停封死状态，经骨架
is_limit_locked 钩子闭包注入，服务 A 股信号域候选池入口过滤。

降级：过滤模块未就绪 → 仅排除涨跌停封死/停牌，其余放行（degraded=True）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from operator import attrgetter
from typing import Final

from zephyr.signal_ashare.selection_funnel_skeleton import (
    GradedExclusionHooks,
    GradedFilterThresholds,
    run_graded_exclusion,
)

__all__: Final = [
    "Board",
    "TieredFilterConfig",
    "TieredFilterRecord",
    "TieredFilterResult",
    "filter_tiered",
    "is_limit_locked_price",
    "limit_pct_for",
]

#: 涨跌停判定容差（吸收分位舍入与一档价差，初拟）
_LIMIT_EPS: Final = 0.001

_SYMBOL_OF: Final = attrgetter("symbol")


class Board(str, Enum):
    """A 股板块（决定涨跌停幅度，宪章 §2 约束四）。"""

    MAIN = "MAIN"  # 沪深主板 ±10%
    STAR_CHINEXT = "STAR_CHINEXT"  # 科创板/创业板 ±20%
    BJ = "BJ"  # 北交所 ±30%


def limit_pct_for(board: Board | str, *, is_st: bool = False) -> float:
    """板块 → 涨跌停幅度（小数）。

    规则（宪章 §2 约束四 + 2026-07-06 新规）：主板 ±10%（ST ±10%，原 5% 已上调）/
    科创创业板 ±20%（ST 同板块幅度）/ 北交所 ±30%。

    Args:
        board: 板块枚举或其值字符串
        is_st: 是否 ST/*ST（主板 ST 现与主板同幅度 ±10%，参数保留以便北交所/科创差异演化）

    Returns:
        涨跌停幅度（如 0.10 / 0.20 / 0.30）

    Raises:
        ValueError: 未知板块
    """
    try:
        b = Board(board)
    except ValueError:
        raise ValueError(f"未知板块: {board!r}（合法值: {[e.value for e in Board]}）") from None
    if b is Board.STAR_CHINEXT:
        return 0.20
    if b is Board.BJ:
        return 0.30
    return 0.10


def is_limit_locked_price(
    close: float,
    prev_close: float,
    limit_pct: float,
    *,
    eps: float = _LIMIT_EPS,
) -> bool | None:
    """从收盘价推导涨跌停封死（|close/prev_close − 1| ≥ limit_pct − ε）。

    涨停封死与跌停封死均视为"当日无法按正常价格成交"——第一层过滤对两个方向
    都排除（涨停买不进、跌停卖不出/接飞刀）。

    Returns:
        True/False；prev_close<=0（数据缺失/复牌首日）返回 None 表示状态不明。
    """
    if prev_close <= 0:
        return None
    return abs(close / prev_close - 1.0) >= limit_pct - eps


@dataclass(frozen=True)
class TieredFilterConfig:
    """第一层过滤阈值（21 号 memo §3.6 ① 契约值，G05 回测校准前初拟）。

    Attributes:
        new_stock_min_list_days: 门禁排除——次新上市 <N 天绝对排除
        min_avg_daily_amount: 分级排除——日均成交额 <N 元剔除（流动性失效保护）
        dealer_abandon_prob_max: 概率排除——庄家弃庄概率 >N 剔除（BM-SEL-05 输出）
        limit_eps: 涨跌停判定容差
    """

    new_stock_min_list_days: int = 30
    min_avg_daily_amount: float = 5_000_000.0
    dealer_abandon_prob_max: float = 0.95
    limit_eps: float = _LIMIT_EPS


@dataclass(frozen=True)
class TieredFilterRecord:
    """第一层过滤候选标的记录（只消费本层字段，上游负责装配）。"""

    symbol: str
    board: str = "MAIN"
    close: float = 0.0
    prev_close: float = 0.0
    is_suspended: bool = False  # 停牌
    is_st: bool = False  # ST/*ST/退市风险
    list_days: int = 9999  # 上市天数
    avg_daily_amount: float = 1e12  # 日均成交额（元）
    dealer_abandon_prob: float = 0.0  # 庄家弃庄概率 [0,1]（BM-SEL-05 主力行为输出）


@dataclass(frozen=True)
class TieredFilterResult:
    """第一层过滤输出。"""

    kept: tuple[str, ...]  # 保留标的（输入顺序）
    excluded: dict[str, str] = field(default_factory=dict)  # {symbol: 排除原因}
    degraded: bool = False  # True=降级路径（仅排除涨跌停封死/停牌）


def filter_tiered(
    records: list[TieredFilterRecord],
    *,
    config: TieredFilterConfig | None = None,
    degraded: bool = False,
) -> TieredFilterResult:
    """四排除机制批处理过滤（~7000→~1200）——委托 MOD-SIG-086 共享骨架。

    排除优先级（先命中先生效）：物理排除（涨跌停封死/停牌/ST）→ 门禁排除（次新）
    → 分级排除（流动性）→ 概率排除（弃庄）。
    degraded=True：仅排除涨跌停封死/停牌，其余放行（memo 既定降级路径）。
    prev_close 缺失（<=0）的标的涨跌停状态不明，不据此排除，其余规则照常。
    """
    cfg = config or TieredFilterConfig()
    hooks = GradedExclusionHooks(
        # 板块幅度自推导注入：board→limit_pct→close/prev_close 推导封死；状态不明 None→不排除
        is_limit_locked=lambda rec: is_limit_locked_price(
            rec.close, rec.prev_close, limit_pct_for(rec.board, is_st=rec.is_st), eps=cfg.limit_eps
        )
        is True,
        is_suspended=attrgetter("is_suspended"),
        is_st=attrgetter("is_st"),
        list_days=attrgetter("list_days"),
        avg_daily_amount=attrgetter("avg_daily_amount"),
        dealer_abandon_prob=attrgetter("dealer_abandon_prob"),
    )
    out = run_graded_exclusion(
        records,
        symbol_of=_SYMBOL_OF,
        hooks=hooks,
        thresholds=GradedFilterThresholds(
            new_stock_min_list_days=cfg.new_stock_min_list_days,
            min_avg_daily_amount=cfg.min_avg_daily_amount,
            dealer_abandon_prob_max=cfg.dealer_abandon_prob_max,
        ),
        degraded=degraded,
    )
    return TieredFilterResult(kept=out.kept, excluded=out.excluded, degraded=degraded)
