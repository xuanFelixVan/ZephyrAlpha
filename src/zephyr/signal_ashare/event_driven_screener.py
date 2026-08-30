# [BLUEPRINT] MOD-SIG-049 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.3
# [MODULE] zephyr.signal_ashare.event_driven_screener
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（传导链风险按数值消费，与 causal_inference_engine 解耦）
# [CONSUMERS] (待 sleeve 排序/StrategyBook 接线)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 无事件数据源 → skipped 直通不筛；利空/极端反应/高传导风险仅剔除不做空（宪章§2约束三）；kept ⊆ 输入；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] capacity_target<=0 → ValueError；空输入 → 空结果
# [TESTS] tests/signal_ashare/test_event_driven_screener.py
# [A_module] module_id=MOD-SIG-049 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: EventImpactRecord（事件有无/类别/方向/强度/置信度/年龄/事件日反应/传导链风险）
# A1: 置信度门控（confidence<0.7 视为无事件）+ 利空剔除（direction<0）+ 极端反应剔除（|reaction|>3%，PEAD Inversion）
# A2: 传导链风险剔除（conduction_risk>0.7，消费 BM-SEL-11 因果推演输出）
# A3: 事件衰减权重 weight = 1 + direction×strength×2^(−age/半衰期)，按事件类半衰期表；容量截断 ~50→~30
# O1: EventScreenResult(kept/excluded{symbol:reason}/weights/skipped/degraded)
# [/ALGO_FLOW]
"""
选股漏斗第四层——事件驱动分布筛选（BM-SEL-19，~50→~30）。

事件影响三重门控（26 号 memo §2.3/§2.4 + 21 号 memo §3.6）：
  ① 置信度门控——LLM 事件标签 confidence<0.7 视为无事件（防误读，初拟阈值）；
  ② 方向剔除——利空事件（direction<0）剔除候选（不能做空，alpha 集中在利好多头）；
  ③ 极端反应剔除——事件日 |reaction|>3% 触发 PEAD Inversion 修正：不追涨不杀跌
     （极端正向 20 日中位 −5.58% 反转；极端负向等 day 2-3 确认，均不进入买入候选）。

传导链风险（conduction_risk，可消费 BM-SEL-11 因果推演/MOD-SIG-042 输出）超阈值剔除。
保留标的按事件衰减曲线赋排序权重：weight = 1 + direction×strength×2^(−age/半衰期)，
半衰期按事件类取 26 号 §2.4 经验值中点；容量收敛 ~50→~30 按权重降序截断。

降级/跳过：无事件数据源（event_source_ready=False）→ skipped=True 直通不筛
（memo 契约："没事件数据源就跳过"）；degraded=True → 仅剔除利空，其余放行。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: category 参数
#   fields: 参数 category，类型注解 EventCategory | str
#   code: event_driven_screener.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: records 参数
#   fields: 参数 records，类型注解 list[EventImpactRecord]
#   code: event_driven_screener.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: event_driven_screener.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: event_source_ready 参数
#   fields: 参数 event_source_ready（无注解）
#   code: event_driven_screener.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① event_halflife_days
#   name_en: event_halflife_days
#   intro: 事件类 → rising 半衰期（交易日）。
#   desc: 事件类 → rising 半衰期（交易日）。未知类别 → ValueError 由 Enum 转换抛出。；源码 L135-L137
#   inputs: category
#   outputs: float
# - id: A2
#   name_zh: ② screen_events
#   name_en: screen_events
#   intro: 事件驱动分布筛选（~50→~30）。
#   desc: 事件驱动分布筛选（~50→~30）。 无事件数据源（event_source_ready=False）→ skipped=True 直通不筛（memo 既定跳过路径）。 degr…；源码 L191-L245
#   inputs: records config event_source_ready degraded
#   outputs: EventScreenResult
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 sleeve 排序/StrategyBook 接线)
# - id: O2
#   name_zh: EventScreenResult
#   name_en: EventScreenResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 sleeve 排序/StrategyBook 接线)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

__all__: Final = [
    "EventCategory",
    "EventImpactRecord",
    "EventScreenConfig",
    "EventScreenResult",
    "event_halflife_days",
    "screen_events",
]


class EventCategory(str, Enum):
    """事件六类粗分类（26 号 memo §2.3 首版）。"""

    EARNINGS = "EARNINGS"  # 业绩（预告/快报/盈余惊喜）
    MERGER = "MERGER"  # 并购重组/资产注入
    POLICY = "POLICY"  # 行业/货币/产业政策
    SUDDEN = "SUDDEN"  # 突发（黑天鹅/题材爆发）
    IPO = "IPO"  # IPO/再融资（虹吸）
    GEO = "GEO"  # 地缘/宏观（传导链）


#: 事件类 → rising 半衰期（交易日，26 号 memo §2.4 经验区间中点，初拟待校准）
_EVENT_HALFLIFE: Final = {
    EventCategory.EARNINGS: 4.0,  # 3-5 天
    EventCategory.MERGER: 2.0,  # 1-3 天（复牌后）
    EventCategory.POLICY: 5.0,  # 3-7 天
    EventCategory.SUDDEN: 2.0,  # 1-3 天（题材）
    EventCategory.IPO: 4.0,  # 3-5 天（布局窗）
    EventCategory.GEO: 10.0,  # 5-15 天（远长于业绩/并购）
}


def event_halflife_days(category: EventCategory | str) -> float:
    """事件类 → rising 半衰期（交易日）。未知类别 → ValueError 由 Enum 转换抛出。"""
    return _EVENT_HALFLIFE[EventCategory(category)]


@dataclass(frozen=True)
class EventScreenConfig:
    """第四层事件筛选参数（memo 契约值 + 初拟阈值，G10 校准）。

    Attributes:
        min_confidence: 事件置信度门控（21 号 §3.6 初拟 0.7，低于视为无事件）
        extreme_reaction_pct: PEAD Inversion 极端反应阈值（%，|reaction|>3% 不追涨不杀跌）
        conduction_risk_max: 传导链风险剔除阈值（0-1，越高越宽容）
        capacity_target: 漏斗容量目标（~30）；通过数超容量按权重降序截断
    """

    min_confidence: float = 0.7
    extreme_reaction_pct: float = 3.0
    conduction_risk_max: float = 0.7
    capacity_target: int = 30


@dataclass(frozen=True)
class EventImpactRecord:
    """第四层事件筛选候选标的记录（来自 BM-SEL-18 Top ~50 + 事件源装配）。"""

    symbol: str
    has_event: bool = False  # 是否有有效事件（置信度门控后）
    event_category: str = "EARNINGS"  # EventCategory 值
    direction: int = 0  # 事件冲击方向：+1 利多 / -1 利空 / 0 中性
    strength: float = 0.0  # 冲击强度 [0,1]
    confidence: float = 0.0  # 事件标签置信度 [0,1]（LLM 门控输入）
    age_days: int = 0  # 事件年龄（交易日，盘后事件 T+1 起算）
    reaction_pct: float = 0.0  # 事件日反应（%，PEAD Inversion 判定输入）
    conduction_risk: float = 0.0  # 传导链风险 [0,1]（BM-SEL-11/MOD-SIG-042 输出）


@dataclass(frozen=True)
class EventScreenResult:
    """第四层事件筛选输出。"""

    kept: tuple[str, ...]
    excluded: dict[str, str] = field(default_factory=dict)  # {symbol: 排除原因}
    weights: dict[str, float] = field(default_factory=dict)  # {symbol: 排序权重（kept 内）}
    skipped: bool = False  # True=无事件数据源，直通不筛
    degraded: bool = False  # True=降级路径（仅剔除利空）
    truncated: bool = False  # True=超容量按权重截断


def _event_weight(rec: EventImpactRecord) -> float:
    """事件衰减排序权重 = 1 + direction×strength×2^(−age/半衰期)（rising 相持有）。"""
    halflife = event_halflife_days(rec.event_category)
    decay = math.pow(2.0, -rec.age_days / halflife)
    return 1.0 + rec.direction * rec.strength * decay


def screen_events(
    records: list[EventImpactRecord],
    *,
    config: EventScreenConfig | None = None,
    event_source_ready: bool = True,
    degraded: bool = False,
) -> EventScreenResult:
    """事件驱动分布筛选（~50→~30）。

    无事件数据源（event_source_ready=False）→ skipped=True 直通不筛（memo 既定跳过路径）。
    degraded=True → 仅剔除利空事件标的，不做极端反应/传导链判定。
    """
    cfg = config or EventScreenConfig()
    if cfg.capacity_target <= 0:
        raise ValueError(f"capacity_target 必须为正: {cfg.capacity_target}")
    if not event_source_ready:
        return EventScreenResult(
            kept=tuple(r.symbol for r in records),
            weights={r.symbol: 1.0 for r in records},
            skipped=True,
        )
    kept_records: list[EventImpactRecord] = []
    excluded: dict[str, str] = {}
    for rec in records:
        # 置信度门控：低置信事件视为无事件（不据此剔除，也不加权）
        effective_event = rec.has_event and rec.confidence >= cfg.min_confidence
        if effective_event and rec.direction < 0:
            excluded[rec.symbol] = "event:negative"  # 利空剔除（不能做空）
            continue
        if degraded:
            kept_records.append(rec)
            continue
        if effective_event and abs(rec.reaction_pct) > cfg.extreme_reaction_pct:
            excluded[rec.symbol] = f"event:extreme_reaction({rec.reaction_pct:+.1f}%)"
            continue
        if rec.conduction_risk > cfg.conduction_risk_max:
            excluded[rec.symbol] = "event:conduction_risk"
            continue
        kept_records.append(rec)
    weights = {
        r.symbol: (_event_weight(r) if r.has_event and r.confidence >= cfg.min_confidence else 1.0)
        for r in kept_records
    }
    truncated = False
    if len(kept_records) > cfg.capacity_target:
        kept_records = sorted(kept_records, key=lambda r: (-weights[r.symbol], r.symbol))[: cfg.capacity_target]
        truncated = True
    return EventScreenResult(
        kept=tuple(r.symbol for r in kept_records),
        excluded=excluded,
        weights={s: weights[s] for s in (r.symbol for r in kept_records)},
        skipped=False,
        degraded=degraded,
        truncated=truncated,
    )
