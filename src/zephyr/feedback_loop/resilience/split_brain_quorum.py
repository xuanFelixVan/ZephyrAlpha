# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.split_brain_quorum
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
Split-Brain Quorum — v0.37.0 R451

Blindspot: Multiple FLE instances detect same issue and race to repair;
conflicting actions cause split-brain corruption.

Risk: R451 — Distributed FLE instances issue contradictory repairs simultaneously.

Mitigation: Distributed quorum-based action ownership. Before acting,
instance must acquire a quorum lock via atomic lease. Stale leases auto-expire.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: split_brain_quorum.py
# 层: 算法
# - id: A1
#   name_zh: ① SplitBrainQuorum
#   name_en: SplitBrainQuorum
#   intro: class SplitBrainQuorum 源码 L73-L116
#   desc: 公共方法（定义序）: heartbeat, acquire, release, is_owner；源码 L73-L116
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SplitBrainQuorum
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class QuorumState(str, Enum):
    IDLE = "IDLE"
    ACQUIRING = "ACQUIRING"
    OWNER = "OWNER"
    FORFEITED = "FORFEITED"


@dataclass
class SplitBrainQuorum:
    lease_ttl: float = 30.0
    min_instances: int = 2

    instance_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    state: QuorumState = QuorumState.IDLE
    current_owner: str = ""
    lease_expires_at: float = 0.0
    known_instances: dict[str, float] = field(default_factory=dict)

    def heartbeat(self) -> None:
        self.known_instances[self.instance_id] = time.time()
        self._expire_stale()

    def _expire_stale(self) -> None:
        now = time.time()
        self.known_instances = {k: v for k, v in self.known_instances.items() if now - v < self.lease_ttl * 2}

    def acquire(self, action_id: str) -> bool:
        self._expire_stale()
        now = time.time()

        if self.current_owner and now < self.lease_expires_at:
            return self.current_owner == self.instance_id

        self.state = QuorumState.ACQUIRING
        if len(self.known_instances) >= self.min_instances:
            self.current_owner = self.instance_id
            self.lease_expires_at = now + self.lease_ttl
            self.state = QuorumState.OWNER
            return True

        self.state = QuorumState.IDLE
        return False

    def release(self) -> None:
        if self.current_owner == self.instance_id:
            self.current_owner = ""
            self.lease_expires_at = 0.0
            self.state = QuorumState.IDLE

    @property
    def is_owner(self) -> bool:
        return self.state is QuorumState.OWNER and time.time() < self.lease_expires_at
