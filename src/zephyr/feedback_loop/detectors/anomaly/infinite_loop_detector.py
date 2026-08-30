# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.anomaly.infinite_loop_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
Infinite Loop Detector — v0.15.0 R219

Blindspot: FLE repair-recheck cycle can loop indefinitely; no loop detection.
Risk: R219 — Repair->metric improves->threshold triggers another repair->same metric->loop.

Mitigation: Loop detection via action ID repetition tracking with cooldown enforcement.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: infinite_loop_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① InfiniteLoopDetector
#   name_en: InfiniteLoopDetector
#   intro: class InfiniteLoopDetector 源码 L68-L88
#   desc: 公共方法（定义序）: track, clear；源码 L68-L88
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: InfiniteLoopDetector
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
class LoopAction:
    action_signature: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class InfiniteLoopDetector:
    recent_actions: deque[LoopAction] = field(default_factory=lambda: deque(maxlen=50))
    loop_threshold: int = 3
    cooldown_seconds: float = 300.0
    active_loops: set[str] = field(default_factory=set)

    def track(self, action_signature: str) -> bool:
        now = time.time()
        self.recent_actions.append(LoopAction(action_signature=action_signature, timestamp=now))
        recent_matches = [
            a
            for a in self.recent_actions
            if a.action_signature == action_signature and now - a.timestamp < self.cooldown_seconds
        ]
        if len(recent_matches) >= self.loop_threshold:
            self.active_loops.add(action_signature)
            return True
        return False

    def clear(self, action_signature: str) -> None:
        self.active_loops.discard(action_signature)
