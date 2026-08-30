# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.market_event_integrator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Market Event Integrator — v0.14.0 R197

Blindspot: FLE unaware of market events (circuit breaker, FOMC, holidays); normal operations during chaos.
Risk: R197 — Market-wide circuit breaker tripped; FLE diagnoses "missing data" as pipeline failure.

Mitigation: Market calendar + event-driven mode switching for FLE behavior.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: market_event_integrator.py
# 层: 算法
# - id: A1
#   name_zh: ① MarketEventIntegrator
#   name_en: MarketEventIntegrator
#   intro: class MarketEventIntegrator 源码 L77-L116
#   desc: 公共方法（定义序）: on_circuit_breaker, on_fomc, on_holiday, should_suppress_anomaly；源码 L77-L116
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: MarketEventIntegrator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class MarketMode(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    EMERGENCY = "EMERGENCY"
    HOLIDAY = "HOLIDAY"


@dataclass
class MarketEvent:
    event_type: str
    timestamp: float
    mode: MarketMode
    description: str


@dataclass
class MarketEventIntegrator:
    events: list[MarketEvent] = field(default_factory=list)
    current_mode: MarketMode = MarketMode.NORMAL

    def on_circuit_breaker(self, exchange: str) -> None:
        event = MarketEvent(
            event_type="CIRCUIT_BREAKER",
            timestamp=time.time(),
            mode=MarketMode.EMERGENCY,
            description=f"Circuit breaker triggered on {exchange}",
        )
        self.events.append(event)
        self.current_mode = MarketMode.EMERGENCY

    def on_fomc(self) -> None:
        event = MarketEvent(
            event_type="FOMC",
            timestamp=time.time(),
            mode=MarketMode.CAUTION,
            description="FOMC announcement window",
        )
        self.events.append(event)
        self.current_mode = MarketMode.CAUTION

    def on_holiday(self, holiday_name: str) -> None:
        event = MarketEvent(
            event_type="HOLIDAY",
            timestamp=time.time(),
            mode=MarketMode.HOLIDAY,
            description=f"Market holiday: {holiday_name}",
        )
        self.events.append(event)
        self.current_mode = MarketMode.HOLIDAY

    def should_suppress_anomaly(self, anomaly_type: str) -> bool:
        if self.current_mode is MarketMode.HOLIDAY:
            return anomaly_type in ("missing_data", "low_volume")
        if self.current_mode is MarketMode.EMERGENCY:
            return anomaly_type in ("high_volatility", "latency_spike")
        return False
