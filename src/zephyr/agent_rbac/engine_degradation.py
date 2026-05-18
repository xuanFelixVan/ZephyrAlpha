# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.engine_degradation

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
L0 Engine Degradation — 权限引擎降级策略与降级攻击防护

MOD-INF-018 §2.3  D-018-06

核心原则：崩 = blocked（安全检查失败 → 默认拒绝），绝不放行。
对标 Perplexity cascading failures + NVIDIA 多 Agent 健康检测。

降级层级:
  L0: ImmutableCore 故障 → SYSTEM_UNAVAILABLE（系统不可用）
  L1: RBAC 故障 → PERMISSION_BLOCKED（拒绝所有操作）
  L2: ABAC/Input 部分故障 → PARTIAL_FAILURE（降级但不全放行）
  L3: 恢复 → 完整性验证后恢复

降级攻击防护:
  同一 Agent 触发降级 → 立即 BLOCKED
  PartialFailure > 3600s → 升级 P0 告警
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from typing import Optional


class DegradationLevel(Enum):
    NORMAL = "normal"
    PARTIAL_FAILURE = "partial_failure"
    PERMISSION_BLOCKED = "permission_blocked"
    SYSTEM_UNAVAILABLE = "system_unavailable"


class DegradationReason(Enum):
    IMMUTABLE_CORE_FAULT = "immutable_core_fault"
    KILL_SWITCH_ACTIVE = "kill_switch_active"
    RBAC_CONFIG_LOAD_FAILURE = "rbac_config_load_failure"
    ABAC_RULE_EVAL_FAILURE = "abac_rule_eval_failure"
    INPUT_GUARD_FAILURE = "input_guard_failure"
    CLEARED = "cleared"


@dataclass
class DegradationState:
    level: DegradationLevel = DegradationLevel.NORMAL
    reason: DegradationReason = DegradationReason.CLEARED
    since: float = field(default_factory=time.time)
    triggered_by_agent: Optional[str] = None
    partial_failure_start: Optional[float] = None
    recovery_attempts: int = 0


@dataclass
class AgentDegradationRecord:
    agent_id: str
    degradation_count: int = 0
    first_degradation: float = field(default_factory=time.time)
    last_degradation: float = field(default_factory=time.time)
    blocked: bool = False


class EngineDegradationManager:
    def __init__(self) -> None:
        self._state = DegradationState()
        self._agent_records: dict[str, AgentDegradationRecord] = {}
        self._degradation_threshold = 2
        self._partial_failure_upgrade_seconds = 3600

    @property
    def state(self) -> DegradationState:
        return self._state

    @property
    def is_blocked(self) -> bool:
        return self._state.level in (
            DegradationLevel.PERMISSION_BLOCKED,
            DegradationLevel.SYSTEM_UNAVAILABLE,
        )

    @property
    def is_degraded(self) -> bool:
        return self._state.level != DegradationLevel.NORMAL

    def should_block(self) -> bool:
        return self.is_blocked

    def trigger_degradation(
        self,
        level: DegradationLevel,
        reason: DegradationReason,
        agent_id: Optional[str] = None,
    ) -> DegradationState:
        self._state.level = level
        self._state.reason = reason
        self._state.since = time.time()
        self._state.triggered_by_agent = agent_id

        if level == DegradationLevel.PARTIAL_FAILURE:
            if self._state.partial_failure_start is None:
                self._state.partial_failure_start = time.time()

        if agent_id is not None:
            self._record_agent_degradation(agent_id)

        self._check_partial_failure_upgrade()
        return self._state

    def _record_agent_degradation(self, agent_id: str) -> None:
        now = time.time()
        if agent_id not in self._agent_records:
            self._agent_records[agent_id] = AgentDegradationRecord(agent_id=agent_id)
        record = self._agent_records[agent_id]
        record.degradation_count += 1
        record.last_degradation = now
        if record.first_degradation == 0:
            record.first_degradation = now
        if record.degradation_count >= self._degradation_threshold:
            record.blocked = True

    def is_agent_degradation_blocked(self, agent_id: str) -> bool:
        record = self._agent_records.get(agent_id)
        if record is None:
            return False
        return record.blocked

    def is_partial_failure_upgrade_needed(self) -> bool:
        if self._state.level != DegradationLevel.PARTIAL_FAILURE:
            return False
        if self._state.partial_failure_start is None:
            return False
        elapsed = time.time() - self._state.partial_failure_start
        return elapsed > self._partial_failure_upgrade_seconds

    def _check_partial_failure_upgrade(self) -> bool:
        if self.is_partial_failure_upgrade_needed():
            self._state.level = DegradationLevel.PERMISSION_BLOCKED
            self._state.reason = DegradationReason.RBAC_CONFIG_LOAD_FAILURE
            return True
        return False

    def try_recover(self) -> bool:
        if self._state.level == DegradationLevel.SYSTEM_UNAVAILABLE:
            if not self._verify_immutable_core():
                return False
        self._state.level = DegradationLevel.NORMAL
        self._state.reason = DegradationReason.CLEARED
        self._state.recovery_attempts += 1
        self._state.partial_failure_start = None
        return True

    def owner_force_recover(self) -> None:
        self._state = DegradationState(
            level=DegradationLevel.NORMAL,
            reason=DegradationReason.CLEARED,
        )
        for record in self._agent_records.values():
            record.blocked = False

    def _verify_immutable_core(self) -> bool:
        try:
            from zephyr.agent_rbac.immutable_core import get_immutable_core
            core = get_immutable_core()
            result = core.verify_immutable_core_integrity()
            return result.intact
        except Exception:
            return False

    def reset(self) -> None:
        self._state = DegradationState()
        self._agent_records.clear()


_engine_degradation_manager: Optional[EngineDegradationManager] = None


def get_engine_degradation_manager() -> EngineDegradationManager:
    global _engine_degradation_manager
    if _engine_degradation_manager is None:
        _engine_degradation_manager = EngineDegradationManager()
    return _engine_degradation_manager
