# [BLUEPRINT] MOD-SIG-106 | docs/03_modules/_domain_signal/sell_news_overdraft_detector/blueprint.md
# [MODULE] zephyr.signal_ashare.sell_news_overdraft_detector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（纯函数核，不 import zephyr 内部件）
# [CONSUMERS] （候选：L2-C 日历约束升级 / L2-A 落地日卖出信号装配层）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 事件5类→可预测性映射封闭；透支度4维综合>1.2 severe / 0.8~1.2 mild / <0.8 none；落地前severe∧0≤天数≤3→reduce；黑天鹅→applicable=False
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01453 行 + 候选注册表 CAND-TESTB-023
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知事件类型/历史均值≤0/峰值热度≤0/成交额<0/非有限读数/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_sell_news_overdraft_detector.py
# [A_module] module_id=MOD-SIG-106 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
利好落地变利空预期透支检测（MOD-SIG-106，B10-01453，模块28）。

sell-the-news 利好兑现效应：事件可预测性分类 + 预期透支度 4 维量化
+ 时间轴 5 阶段 + 落地前减仓信号。

依据: AUD-DRAFT-001 深挖批 B10-01453（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-106
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: sell_news_overdraft_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SellNewsOverdraftDetector
#   name_en: SellNewsOverdraftDetector
#   intro: 利好落地变利空预期透支检测器。
#   desc: 利好落地变利空预期透支检测器。；公共方法（定义序）: assess；源码 L161-L234
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: SellNewsOverdraftDetector
#   downstream: （候选：L2-C 日历约束升级 / L2-A 落地日卖出信号装配层）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "EVENT_PREDICTABILITY",
    "NewsEventContext",
    "OverdraftConfig",
    "OverdraftLevel",
    "OverdraftAssessment",
    "SellNewsOverdraftDetector",
    "TimelinePhase",
]

# ------------------------------------------------------------------
# 封闭集
# ------------------------------------------------------------------
EVENT_PREDICTABILITY: Final[dict[str, str]] = {
    "policy": "high",
    "earnings": "high",
    "industry": "medium",
    "geopolitical": "medium",
    "black_swan": "unpredictable",
}


class TimelinePhase(str, Enum):
    EARLY_ACCUMULATION = "early_accumulation"
    MID_FERMENTATION = "mid_fermentation"
    LATE_SPRINT = "late_sprint"
    LANDING_DAY = "landing_day"
    POST_LANDING = "post_landing"


class OverdraftLevel(str, Enum):
    NONE = "none"
    MILD = "mild"
    SEVERE = "severe"


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class NewsEventContext:
    event_type: str
    days_to_landing: int = 0
    price_gain_ratio: float = 1.0
    time_advance_days: int = 0
    capital_inflow_ratio: float = 0.0
    sentiment_peak_ratio: float = 0.0
    historical_mean_price: float = 1.0
    avg_turnover_5d: float = 1.0

    def __post_init__(self):
        if self.event_type not in EVENT_PREDICTABILITY:
            raise ValueError(f"未知 event_type: {self.event_type}")
        if self.historical_mean_price <= 0:
            raise ValueError("historical_mean_price 必须 >0")
        if self.avg_turnover_5d < 0:
            raise ValueError("avg_turnover_5d 不可 <0")
        for v in (self.price_gain_ratio, self.capital_inflow_ratio, self.sentiment_peak_ratio):
            if not math.isfinite(v):
                raise ValueError("读数必须有限")
        if self.sentiment_peak_ratio < 0:
            raise ValueError("sentiment_peak_ratio 不可 <0")


@dataclass(frozen=True)
class OverdraftConfig:
    severe_threshold: float = 1.20
    mild_threshold: float = 0.80
    landing_window_days: int = 3
    capital_severe_threshold: float = 1.0
    sentiment_near_peak: float = 0.85

    def __post_init__(self):
        if not (self.mild_threshold < self.severe_threshold):
            raise ValueError("mild_threshold 必须 < severe_threshold")


@dataclass(frozen=True)
class OverdraftAssessment:
    predictability: str
    price_overdraft: float
    time_overdraft: float
    capital_overdraft: float
    sentiment_overdraft: float
    composite: float
    level: OverdraftLevel
    phase: TimelinePhase
    action: str
    applicable: bool = True
    reason: str = ""


# ------------------------------------------------------------------
# 实现
# ------------------------------------------------------------------
class SellNewsOverdraftDetector:
    """利好落地变利空预期透支检测器。"""

    def __init__(self, config: OverdraftConfig | None = None) -> None:
        self.config = config or OverdraftConfig()

    def assess(self, ctx: NewsEventContext) -> OverdraftAssessment:
        predictability = EVENT_PREDICTABILITY.get(ctx.event_type, "unknown")
        if predictability == "unpredictable":
            return OverdraftAssessment(
                predictability=predictability,
                price_overdraft=0.0,
                time_overdraft=0.0,
                capital_overdraft=0.0,
                sentiment_overdraft=0.0,
                composite=0.0,
                level=OverdraftLevel.NONE,
                phase=self._phase(ctx.days_to_landing),
                action="not_applicable",
                applicable=False,
                reason="unpredictable event",
            )
        # 四维透支度
        price_od = ctx.price_gain_ratio  # 累计涨幅/均值
        time_od = min(1.0, ctx.time_advance_days / 30.0)
        capital_od = ctx.capital_inflow_ratio
        sentiment_od = ctx.sentiment_peak_ratio
        composite = (price_od + time_od + capital_od + sentiment_od) / 4.0

        level = self._level(composite)
        phase = self._phase(ctx.days_to_landing)
        action = self._action(level, ctx.days_to_landing)

        return OverdraftAssessment(
            predictability=predictability,
            price_overdraft=price_od,
            time_overdraft=time_od,
            capital_overdraft=capital_od,
            sentiment_overdraft=sentiment_od,
            composite=composite,
            level=level,
            phase=phase,
            action=action,
            applicable=True,
        )

    def _level(self, composite: float) -> OverdraftLevel:
        if composite > self.config.severe_threshold:
            return OverdraftLevel.SEVERE
        if composite >= self.config.mild_threshold:
            return OverdraftLevel.MILD
        return OverdraftLevel.NONE

    def _phase(self, days: int) -> TimelinePhase:
        if days > 15:
            return TimelinePhase.EARLY_ACCUMULATION
        if days > 5:
            return TimelinePhase.MID_FERMENTATION
        if days > 0:
            return TimelinePhase.LATE_SPRINT
        if days == 0:
            return TimelinePhase.LANDING_DAY
        return TimelinePhase.POST_LANDING

    def _action(self, level: OverdraftLevel, days: int) -> str:
        if level != OverdraftLevel.SEVERE:
            if level == OverdraftLevel.MILD:
                return "watch"
            return "none"
        if 0 <= days <= self.config.landing_window_days:
            return "reduce"
        if days < 0:
            return "clear"
        return "watch"
