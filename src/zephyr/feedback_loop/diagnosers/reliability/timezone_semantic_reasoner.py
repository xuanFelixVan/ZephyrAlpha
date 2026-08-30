# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.timezone_semantic_reasoner
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
Timezone Semantic Reasoner — v0.37.0 R456

Blindspot: FLE operates on UTC timestamps only; misinterprets
market hours, settlement deadlines, and regulatory cutoffs across timezones.

Risk: R456 — Cross-timezone misinterpretation causes missed trading windows
or premature shutdown of monitoring.

Mitigation: Multi-timezone calendar reasoning. Map UTC to exchange local times.
Track DST transitions, holiday calendars per venue. Prevent FLE from suppressing
monitoring during active market hours.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: timezone_semantic_reasoner.py
# 层: 算法
# - id: A1
#   name_zh: ① TimezoneSemanticReasoner
#   name_en: TimezoneSemanticReasoner
#   intro: class TimezoneSemanticReasoner 源码 L75-L112
#   desc: 公共方法（定义序）: is_market_active, any_market_active, active_venues, next_transition；源码 L75-L112
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TimezoneSemanticReasoner
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class VenueTZ(str, Enum):
    NYSE = "America/New_York"
    LSE = "Europe/London"
    TSE = "Asia/Tokyo"
    SSE = "Asia/Shanghai"
    HKEX = "Asia/Hong_Kong"


@dataclass
class TimezoneSemanticReasoner:
    venue_active_windows: dict[str, tuple[int, int]] = field(
        default_factory=lambda: {
            "NYSE": (14, 21),
            "LSE": (8, 16),
            "TSE": (0, 6),
            "SSE": (1, 7),
            "HKEX": (1, 8),
        }
    )

    venue_holidays: dict[str, set[str]] = field(default_factory=dict)

    def is_market_active(self, venue: str, dt: datetime | None = None) -> bool:
        dt = dt or datetime.now(UTC)
        window = self.venue_active_windows.get(venue)
        if not window:
            return False
        start_h, end_h = window
        return start_h <= dt.hour < end_h

    def any_market_active(self) -> bool:
        now = datetime.now(UTC)
        return any(self.is_market_active(v, now) for v in self.venue_active_windows)

    def active_venues(self) -> list[str]:
        now = datetime.now(UTC)
        return [v for v in self.venue_active_windows if self.is_market_active(v, now)]

    def next_transition(self, venue: str) -> float:
        window = self.venue_active_windows.get(venue)
        if not window:
            return 86400.0
        now = datetime.now(UTC)
        start_h, end_h = window
        if now.hour < start_h:
            return (start_h - now.hour) * 3600.0
        return (24 - now.hour + start_h) * 3600.0
