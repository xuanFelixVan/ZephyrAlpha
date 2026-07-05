# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §engine_degradation
# [MODULE] zephyr.security.access_control.engine_degradation
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] genesis_bootstrap._phase_engine_degradation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] default level is NORMAL; degradation only escalates; recovery requires explicit action
# [MODIFY-GUARD] Owner approval required; changes require blueprint update
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] trigger_degradation()/recover() never raise; return dict with success flag
# [TESTS] tests/agent_rbac/test_rbac_auto_lifecycle.py
# [A_module] module_id=MOD-SEC_engine_degradation | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""EngineDegradation — 引擎降级管理.

依据蓝图 MOD-INF-018 §engine_degradation:
- 管理引擎降级级别
- 在资源不足或故障时降级运行
- 支持升级和恢复
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

_AGENT_BLOCK_THRESHOLD = 2
_PARTIAL_FAILURE_UPGRADE_SECONDS = 3600.0


class DegradationLevel(str, Enum):
    """降级级别."""

    NORMAL = "normal"
    PARTIAL_FAILURE = "partial_failure"
    DEGRADED = "degraded"
    SEVERELY_DEGRADED = "severely_degraded"
    PERMISSION_BLOCKED = "permission_blocked"
    SYSTEM_UNAVAILABLE = "system_unavailable"


class DegradationReason(str, Enum):
    """降级原因."""

    NONE = "none"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"
    RATE_LIMIT = "rate_limit"
    MANUAL = "manual"
    IMMUTABLE_CORE_FAULT = "immutable_core_fault"
    RBAC_CONFIG_LOAD_FAILURE = "rbac_config_load_failure"
    ABAC_RULE_EVAL_FAILURE = "abac_rule_eval_failure"
    INPUT_GUARD_FAILURE = "input_guard_failure"


_BLOCKED_LEVELS = frozenset({
    DegradationLevel.SYSTEM_UNAVAILABLE,
    DegradationLevel.PERMISSION_BLOCKED,
})


@dataclass
class DegradationState:
    """降级状态.

    Attributes:
        level: 当前降级级别
        reason: 降级原因
        escalated_at: 升级时间戳
        message: 详细信息
        partial_failure_start: 部分失败开始时间
        triggered_by_agent: 触发降级的 agent ID
    """

    level: DegradationLevel = DegradationLevel.NORMAL
    reason: DegradationReason = DegradationReason.NONE
    escalated_at: float = 0.0
    message: str = ""
    partial_failure_start: float | None = None
    triggered_by_agent: str | None = None

    def __repr__(self) -> str:
        return (
            f"DegradationState(level={self.level.value}, "
            f"reason={self.reason.value}, message={self.message!r})"
        )


@dataclass
class AgentDegradationRecord:
    """Agent降级记录."""

    agent_id: str
    level: DegradationLevel = DegradationLevel.NORMAL
    reason: DegradationReason = DegradationReason.NONE
    timestamp: float = 0.0
    count: int = 0


class EngineDegradationManager:
    """引擎降级管理器 — 管理系统降级状态.

    在资源不足或故障时降级运行，支持升级和恢复。
    """

    _singleton_instance: EngineDegradationManager | None = None

    def __init__(self) -> None:
        self._state = DegradationState()
        self._agent_records: dict[str, AgentDegradationRecord] = {}

    @property
    def state(self) -> DegradationState:
        """当前降级状态."""
        return self._state

    @property
    def current_level(self) -> DegradationLevel:
        """当前降级级别."""
        return self._state.level

    @property
    def current_reason(self) -> DegradationReason:
        """当前降级原因."""
        return self._state.reason

    @property
    def is_blocked(self) -> bool:
        """是否被阻断（SYSTEM_UNAVAILABLE 或 PERMISSION_BLOCKED）."""
        return self._state.level in _BLOCKED_LEVELS

    @property
    def is_degraded(self) -> bool:
        """是否处于降级状态（级别 != NORMAL）."""
        return self._state.level != DegradationLevel.NORMAL

    def should_block(self) -> bool:
        """是否应该阻断操作."""
        return self.is_blocked

    def trigger_degradation(
        self,
        level: DegradationLevel,
        reason: DegradationReason = DegradationReason.MANUAL,
        message: str = "",
        agent_id: str | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        """触发降级.

        Args:
            level: 目标降级级别
            reason: 降级原因
            message: 详细信息
            agent_id: 触发降级的 agent ID（可选）
            source: 降级来源（可选）

        Returns:
            dict 包含 success 标志
        """
        old_level = self._state.level
        self._state.level = level
        self._state.reason = reason
        self._state.escalated_at = time.time()
        self._state.message = message

        if level == DegradationLevel.PARTIAL_FAILURE:
            if self._state.partial_failure_start is None:
                self._state.partial_failure_start = time.time()

        if agent_id:
            self._state.triggered_by_agent = agent_id
            record = self._agent_records.get(agent_id)
            if record is None:
                record = AgentDegradationRecord(
                    agent_id=agent_id,
                    level=level,
                    reason=reason,
                    timestamp=time.time(),
                    count=1,
                )
                self._agent_records[agent_id] = record
            else:
                record.count += 1
                record.level = level
                record.reason = reason
                record.timestamp = time.time()

        logger.warning(
            "EngineDegradation TRIGGERED: %s -> %s (reason=%s, agent=%s)",
            old_level.value,
            level.value,
            reason.value,
            agent_id or "N/A",
        )
        return {
            "success": True,
            "old_level": old_level.value,
            "new_level": level.value,
            "reason": reason.value,
        }

    def escalate(
        self,
        level: DegradationLevel,
        reason: DegradationReason = DegradationReason.MANUAL,
        message: str = "",
    ) -> dict[str, Any]:
        """升级降级级别（兼容旧接口）.

        Args:
            level: 目标降级级别
            reason: 降级原因
            message: 详细信息

        Returns:
            dict 包含 success 标志
        """
        return self.trigger_degradation(level, reason, message)

    def is_agent_degradation_blocked(self, agent_id: str) -> bool:
        """检查 agent 是否因多次触发降级而被阻断.

        Args:
            agent_id: agent ID

        Returns:
            bool: 如果 agent 触发次数 >= 阈值则返回 True
        """
        record = self._agent_records.get(agent_id)
        if record is None:
            return False
        return record.count >= _AGENT_BLOCK_THRESHOLD

    def is_blocked_for_agent(self, agent_id: str) -> bool:
        """检查 agent 是否被阻断（兼容别名）."""
        return self.is_agent_degradation_blocked(agent_id)

    def is_partial_failure_upgrade_needed(self) -> bool:
        """检查部分失败是否需要升级到 P0.

        Returns:
            bool: 如果部分失败持续时间 > 3600 秒则返回 True
        """
        if self._state.level != DegradationLevel.PARTIAL_FAILURE:
            return False
        if self._state.partial_failure_start is None:
            return False
        elapsed = time.time() - self._state.partial_failure_start
        return elapsed > _PARTIAL_FAILURE_UPGRADE_SECONDS

    def owner_force_recover(self) -> dict[str, Any]:
        """Owner 强制恢复到正常级别.

        Returns:
            dict 包含 success 标志
        """
        return self._recover_internal("owner_force_recover")

    def try_recover(self) -> bool:
        """尝试恢复（无需核心验证）.

        Returns:
            bool: 恢复成功返回 True
        """
        self._recover_internal("try_recover")
        return True

    def recover(self, message: str = "") -> dict[str, Any]:
        """恢复到正常级别.

        Args:
            message: 恢复信息

        Returns:
            dict 包含 success 标志
        """
        return self._recover_internal(message or "recover")

    def _recover_internal(self, source: str) -> dict[str, Any]:
        """内部恢复实现."""
        old_level = self._state.level
        self._state.level = DegradationLevel.NORMAL
        self._state.reason = DegradationReason.NONE
        self._state.escalated_at = 0.0
        self._state.message = f"recovered via {source}"
        self._state.partial_failure_start = None
        self._state.triggered_by_agent = None
        logger.info(
            "EngineDegradation RECOVERED: %s -> NORMAL (source=%s)",
            old_level.value,
            source,
        )
        return {
            "success": True,
            "old_level": old_level.value,
            "new_level": DegradationLevel.NORMAL.value,
        }

    def reset(self) -> None:
        """重置所有状态和 agent 记录."""
        self._state = DegradationState()
        self._agent_records.clear()

    def get_agent_degradation(self, agent_id: str) -> AgentDegradationRecord | None:
        """获取Agent降级记录."""
        return self._agent_records.get(agent_id)

    def set_agent_degradation(
        self,
        agent_id: str,
        level: DegradationLevel,
        reason: DegradationReason = DegradationReason.MANUAL,
    ) -> AgentDegradationRecord:
        """设置Agent降级级别."""
        record = AgentDegradationRecord(
            agent_id=agent_id,
            level=level,
            reason=reason,
            timestamp=time.time(),
        )
        self._agent_records[agent_id] = record
        return record


_engine_degradation_instance: EngineDegradationManager | None = None


def get_engine_degradation_manager() -> EngineDegradationManager:
    """获取EngineDegradationManager单例."""
    global _engine_degradation_instance
    if _engine_degradation_instance is None:
        _engine_degradation_instance = EngineDegradationManager()
    return _engine_degradation_instance


__all__ = [
    "AgentDegradationRecord",
    "DegradationLevel",
    "DegradationReason",
    "DegradationState",
    "EngineDegradationManager",
    "get_engine_degradation_manager",
]
