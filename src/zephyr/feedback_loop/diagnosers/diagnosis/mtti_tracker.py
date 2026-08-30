# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis.mtti_tracker
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
MTTI Tracker — v0.16.0 R221

Blindspot: No measurement of Mean-Time-To-Identify; FLE speed at finding anomalies invisible.
Risk: R221 — FLE slow to identify critical anomalies; no SLA tracking for detection speed.

Mitigation: MTTI tracking with adaptive threshold based on historical detection latency.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: mtti_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① MTTITracker
#   name_en: MTTITracker
#   intro: class MTTITracker 源码 L70-L89
#   desc: 公共方法（定义序）: record, current_mtti, sla_breach_rate；源码 L70-L89
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: MTTITracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class MTTIEvent:
    anomaly_id: str
    occurred_at: float
    detected_at: float
    mtti_seconds: float


@dataclass
class MTTITracker:
    target_mtti_seconds: float = 300.0
    events: deque[MTTIEvent] = field(default_factory=lambda: deque(maxlen=1000))

    def record(self, anomaly_id: str, occurred_at: float) -> MTTIEvent:
        now = time.time()
        mtti = now - occurred_at
        event = MTTIEvent(anomaly_id=anomaly_id, occurred_at=occurred_at, detected_at=now, mtti_seconds=mtti)
        self.events.append(event)
        return event

    def current_mtti(self) -> float:
        if not self.events:
            return float("inf")
        return sum(e.mtti_seconds for e in self.events) / len(self.events)

    def sla_breach_rate(self) -> float:
        if not self.events:
            return 0.0
        return sum(1 for e in self.events if e.mtti_seconds > self.target_mtti_seconds) / len(self.events)
