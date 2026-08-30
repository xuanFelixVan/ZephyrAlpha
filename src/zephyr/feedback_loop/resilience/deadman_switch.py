# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.deadman_switch
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
Deadman Switch — v0.15.0 R212

Blindspot: FLE runs autonomously with no external kill-switch; runaway unstoppable.
Risk: R212 — Malicious skill takes over; FLE keeps running; no external forced shutdown.

Mitigation: 60s heartbeat; 3 consecutive misses -> automatic self-lock + external alert.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: deadman_switch.py
# 层: 算法
# - id: A1
#   name_zh: ① DeadmanSwitch
#   name_en: DeadmanSwitch
#   intro: class DeadmanSwitch 源码 L68-L95
#   desc: 公共方法（定义序）: heartbeat, check, is_locked；源码 L68-L95
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DeadmanSwitch
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


class DeadmanState(str, Enum):
    ALIVE = "ALIVE"
    WARNING = "WARNING"
    LOCKED = "LOCKED"


@dataclass
class DeadmanSwitch:
    heartbeat_interval: float = 60.0
    max_missed: int = 3
    state: DeadmanState = DeadmanState.ALIVE
    missed_count: int = 0
    last_beat: float = field(default_factory=time.time)

    def heartbeat(self) -> DeadmanState:
        self.last_beat = time.time()
        self.missed_count = 0
        if self.state is DeadmanState.WARNING:
            self.state = DeadmanState.ALIVE
        return self.state

    def check(self) -> DeadmanState:
        elapsed = time.time() - self.last_beat
        if elapsed > self.heartbeat_interval:
            self.missed_count += 1
            self.last_beat = time.time()
        if self.missed_count >= self.max_missed:
            self.state = DeadmanState.LOCKED
        elif self.missed_count > 0:
            self.state = DeadmanState.WARNING
        return self.state

    @property
    def is_locked(self) -> bool:
        return self.state is DeadmanState.LOCKED
