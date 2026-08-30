# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.oscillation_damping
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Oscillation Damping — v0.37.0 R450

Blindspot: FLE actions in rapid succession cause oscillatory instability;
system flips between corrective states without convergence.

Risk: R450 — Unstable feedback loop; FLE overcorrects -> re-corrects -> oscillates indefinitely.

Mitigation: PID-style damping with action cooldown windows. Track reversal frequency;
if >3 reversals in 60s -> force cooldown + escalate to owner.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: oscillation_damping.py
# 层: 算法
# - id: A1
#   name_zh: ① OscillationDamping
#   name_en: OscillationDamping
#   intro: class OscillationDamping 源码 L71-L110
#   desc: 公共方法（定义序）: record_action, is_allowed, remaining_cooldown；源码 L71-L110
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: OscillationDamping
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


class DampingState(str, Enum):
    STABLE = "STABLE"
    DAMPING = "DAMPING"
    COOLDOWN = "COOLDOWN"


@dataclass
class OscillationDamping:
    cooldown_seconds: float = 60.0
    max_reversals: int = 3
    reversal_window: float = 60.0

    state: DampingState = DampingState.STABLE
    last_action_type: str = ""
    reversal_count: int = 0
    reversal_history: list[float] = field(default_factory=list)
    cooldown_until: float = 0.0

    def record_action(self, action_type: str) -> DampingState:
        now = time.time()
        self.reversal_history = [t for t in self.reversal_history if now - t < self.reversal_window]

        if action_type != self.last_action_type and self.last_action_type:
            self.reversal_count += 1
            self.reversal_history.append(now)

        self.last_action_type = action_type

        if len(self.reversal_history) >= self.max_reversals:
            self.state = DampingState.COOLDOWN
            self.cooldown_until = now + self.cooldown_seconds
        elif len(self.reversal_history) >= 1:
            self.state = DampingState.DAMPING
        else:
            self.state = DampingState.STABLE

        return self.state

    def is_allowed(self) -> bool:
        if self.state is DampingState.COOLDOWN and time.time() < self.cooldown_until:
            return False
        return True

    def remaining_cooldown(self) -> float:
        if self.state is not DampingState.COOLDOWN:
            return 0.0
        return max(0.0, self.cooldown_until - time.time())
