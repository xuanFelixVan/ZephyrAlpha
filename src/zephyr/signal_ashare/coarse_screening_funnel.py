# [BLUEPRINT] MOD-SIG-047 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [MODULE] zephyr.signal_ashare.coarse_screening_funnel
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.signal_ashare.fine_scoring_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五维均为布尔/门槛式初筛（非评分）；kept ⊆ 输入；容量截断按 liquidity_score 降序；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] capacity_target<=0 → ValueError；空输入 → 空结果
# [TESTS] tests/signal_ashare/test_coarse_screening_funnel.py
# [A_module] module_id=MOD-SIG-047 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: CoarseScreenRecord（技术形态/量比/换手率/板块强度排名/主力阶段/市场状态适配 + liquidity_score）
# A1: 五维门槛初筛——技术(布尔) + 量价(量比>1.5、换手率门槛) + 板块(强度排名前30%) + 主力(C-011布尔) + 状态(C-021布尔)
# A2: 容量收敛——通过数 > capacity_target 时按 liquidity_score 降序截断（截断标记 truncated=True）
# O1: CoarseScreenResult(kept/excluded{symbol:reason}/degraded/truncated)
# [/ALGO_FLOW]
"""
选股漏斗第二层——初筛漏斗（BM-SEL-17，~1200→~300）。

五维布尔/门槛式初筛（21 号 memo §3.6 ② 契约）：技术（均线/KDJ/MACD 形态，
消费 BM-SEL-02）+ 量价（量比/换手率，L0 行情）+ 板块（板块强度排名前 30%）
+ 主力（C-011 主力阶段，BM-SEL-05）+ 状态（C-021 市场状态，BM-SEL-03）。
"60 秒级 trigger"语义按 memo v1.1.19 登记为批处理执行（盘前/盘后批量，盘中不滚动）。

降级：初筛未就绪 → 全量放行进精筛（算力风险告警由调用方负责，degraded=True）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: records 参数
#   fields: 参数 records，类型注解 list[CoarseScreenRecord]
#   code: coarse_screening_funnel.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: coarse_screening_funnel.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: degraded 参数
#   fields: 参数 degraded（无注解）
#   code: coarse_screening_funnel.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① screen_coarse
#   name_en: screen_coarse
#   intro: 五维初筛 + 容量收敛（~1200→~300）。
#   desc: 五维初筛 + 容量收敛（~1200→~300）。 五维顺序执行（先命中先排除）：技术 → 量比 → 换手率 → 板块排名 → 主力 → 状态。 通过数超过 capacity_ta…；源码 L125-L173
#   inputs: records config degraded
#   outputs: CoarseScreenResult
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: CoarseScreenResult
#   name_en: CoarseScreenResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_ashare.fine_scoring_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

__all__: Final = [
    "CoarseScreenConfig",
    "CoarseScreenRecord",
    "CoarseScreenResult",
    "screen_coarse",
]


@dataclass(frozen=True)
class CoarseScreenConfig:
    """第二层初筛阈值（21 号 memo §3.6 ② 契约值，G09 校准前初拟）。

    Attributes:
        volume_ratio_min: 量比下限（>1.5 为放量关注线）
        turnover_rate_min_pct: 换手率下限（%，memo 未定值默认 0=不强制）
        sector_rank_max_pct: 板块强度排名前百分位上限（前 30%）
        capacity_target: 漏斗容量目标（~300）；通过数超容量时按流动性截断
    """

    volume_ratio_min: float = 1.5
    turnover_rate_min_pct: float = 0.0
    sector_rank_max_pct: float = 0.30
    capacity_target: int = 300


@dataclass(frozen=True)
class CoarseScreenRecord:
    """第二层初筛候选标的记录。"""

    symbol: str
    technical_pass: bool = True  # 技术形态初筛（均线/KDJ/MACD，BM-SEL-02 输出）
    volume_ratio: float = 999.0  # 量比
    turnover_rate_pct: float = 999.0  # 换手率（%）
    sector_strength_rank_pct: float = 0.0  # 板块强度排名前百分位 [0,1]（0=最强）
    main_force_pass: bool = True  # C-011 主力阶段适配（BM-SEL-05）
    market_state_pass: bool = True  # C-021 市场状态适配（BM-SEL-03）
    liquidity_score: float = 0.0  # 流动性综合分（容量截断排序键，越大越优先保留）


@dataclass(frozen=True)
class CoarseScreenResult:
    """第二层初筛输出。"""

    kept: tuple[str, ...]
    excluded: dict[str, str] = field(default_factory=dict)  # {symbol: 排除原因}
    degraded: bool = False  # True=降级路径（全量进精筛）
    truncated: bool = False  # True=通过数超容量目标，已按 liquidity_score 截断


def screen_coarse(
    records: list[CoarseScreenRecord],
    *,
    config: CoarseScreenConfig | None = None,
    degraded: bool = False,
) -> CoarseScreenResult:
    """五维初筛 + 容量收敛（~1200→~300）。

    五维顺序执行（先命中先排除）：技术 → 量比 → 换手率 → 板块排名 → 主力 → 状态。
    通过数超过 capacity_target 时按 liquidity_score 降序截断（同分按 symbol 字典序
    保证确定性），被截断标的不计入 excluded（非规则排除）。
    """
    cfg = config or CoarseScreenConfig()
    if cfg.capacity_target <= 0:
        raise ValueError(f"capacity_target 必须为正: {cfg.capacity_target}")
    if degraded:
        return CoarseScreenResult(kept=tuple(r.symbol for r in records), degraded=True)
    kept_records: list[CoarseScreenRecord] = []
    excluded: dict[str, str] = {}
    for rec in records:
        if not rec.technical_pass:
            excluded[rec.symbol] = "dim:technical"
            continue
        if rec.volume_ratio <= cfg.volume_ratio_min:
            excluded[rec.symbol] = f"dim:volume_ratio({rec.volume_ratio:.2f}<={cfg.volume_ratio_min})"
            continue
        if rec.turnover_rate_pct < cfg.turnover_rate_min_pct:
            excluded[rec.symbol] = "dim:turnover_rate"
            continue
        if rec.sector_strength_rank_pct > cfg.sector_rank_max_pct:
            excluded[rec.symbol] = "dim:sector_rank"
            continue
        if not rec.main_force_pass:
            excluded[rec.symbol] = "dim:main_force"
            continue
        if not rec.market_state_pass:
            excluded[rec.symbol] = "dim:market_state"
            continue
        kept_records.append(rec)
    truncated = False
    if len(kept_records) > cfg.capacity_target:
        kept_records = sorted(kept_records, key=lambda r: (-r.liquidity_score, r.symbol))[: cfg.capacity_target]
        truncated = True
    return CoarseScreenResult(
        kept=tuple(r.symbol for r in kept_records),
        excluded=excluded,
        degraded=False,
        truncated=truncated,
    )
