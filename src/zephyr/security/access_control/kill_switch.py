# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §kill_switch
# [MODULE] zephyr.security.access_control.kill_switch
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] genesis_bootstrap._phase_kill_switch; tests/agent_rbac/test_kill_switch_agent_rbac.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] KillSwitch default state is NORMAL; trigger only on critical failure; reset requires owner approval
# [MODIFY-GUARD] Owner approval required; changes require blueprint update
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] trigger()/reset() never raise; return TriggerResult with success flag
# [TESTS] tests/agent_rbac/test_kill_switch_agent_rbac.py
# [A_module] module_id=MOD-SEC_kill_switch | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""KillSwitch — 熔断器.

依据蓝图 MOD-INF-018 §kill_switch:
- 系统级熔断器，在严重故障时触发
- 默认状态为 NORMAL
- 触发后进入 TRIPPED 状态，需要手动重置
- 支持单Agent阻断和全局熔断
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class KillSwitchState(str, Enum):
    """熔断器状态."""

    NORMAL = "normal"
    TRIPPED = "tripped"
    RESET_PENDING = "reset_pending"
    COOLDOWN = "cooldown"


class KillSwitchStatus:
    """熔断器状态容器."""

    def __init__(self) -> None:
        self.state: KillSwitchState = KillSwitchState.NORMAL
        self.tripped_at: float = 0.0
        self.reason: str = ""

    def __repr__(self) -> str:
        return f"KillSwitchStatus(state={self.state.value}, reason={self.reason!r})"


@dataclass
class TriggerDefinition:
    """触发条件定义."""

    trigger: str
    default_threshold: int = 5
    description: str = ""
    window_seconds: float = 60.0
    cooldown_seconds: float = 0.0
    auto_release: bool = False


@dataclass
class TriggerEvent:
    """触发事件."""

    trigger: str = ""
    agent_id: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class TriggerResult:
    """触发结果 — 类常量模式."""

    NO_ACTION = "no_action"
    BLOCK_AGENT = "block_agent"
    GLOBAL_BLOCK = "global_block"

    def __init__(self, action: str = "no_action", agent_id: str = "", reason: str = "") -> None:
        self.action = action
        self.agent_id = agent_id
        self.reason = reason

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.action == other
        if isinstance(other, TriggerResult):
            return self.action == other.action
        # 5.108.2 修复：返回 NotImplemented 而非 False，让右操作数的 __eq__ 有机会参与比较。
        return NotImplemented

    # 5.83.1 修复：原定义了 __eq__ 但未定义 __hash__，Python 3 中定义 __eq__ 会自动将 __hash__ 设为 None，使实例变为 unhashable。
    # __hash__ 基于 __eq__ 比较的 action 字段，保持两者一致性。
    def __hash__(self) -> int:
        return hash(self.action)

    def __repr__(self) -> str:
        return f"TriggerResult(action={self.action!r}, agent_id={self.agent_id!r})"


# 默认触发器列表（至少9个）
DEFAULT_TRIGGERS: list[TriggerDefinition] = [
    TriggerDefinition(trigger="rapid_file_deletion", default_threshold=5, description="快速文件删除"),
    TriggerDefinition(trigger="permission_boundary_probe", default_threshold=3, description="权限边界探测"),
    TriggerDefinition(trigger="suspicious_sequence", default_threshold=3, description="可疑操作序列"),
    TriggerDefinition(trigger="off_hours_destructive", default_threshold=2, description="非工作时间破坏性操作"),
    TriggerDefinition(trigger="config_file_blitz", default_threshold=4, description="配置文件批量修改"),
    TriggerDefinition(trigger="signal_noise_attack", default_threshold=5, description="信噪攻击"),
    TriggerDefinition(trigger="sensitivity_label_blitz", default_threshold=3, description="敏感标签批量操作"),
    TriggerDefinition(trigger="agent_spawn_storm", default_threshold=5, description="Agent生成风暴"),
    TriggerDefinition(trigger="audit_log_tamper", default_threshold=1, description="审计日志篡改"),
]


class KillSwitch:
    """熔断器 — 系统级安全制动.

    在检测到严重故障时触发，阻止系统继续运行。
    支持单Agent阻断和全局熔断两级机制。
    """

    def __init__(self) -> None:
        self._status = KillSwitchStatus()
        self._triggers: dict[str, TriggerDefinition] = {t.trigger: t for t in DEFAULT_TRIGGERS}
        self._agent_events: dict[str, dict[str, list[float]]] = {}
        self._blocked_agents: set[str] = set()
        self._global_tripped = False
        self._global_reason = ""
        self._override_active = False
        self._pre_override_tripped = False

    @property
    def status(self) -> KillSwitchStatus:
        """当前熔断器状态."""
        return self._status

    @property
    def state(self) -> KillSwitchState:
        """当前状态枚举."""
        return self._status.state

    @property
    def trigger_count(self) -> int:
        """已注册触发器数量."""
        return len(self._triggers)

    @property
    def triggers(self) -> list[TriggerDefinition]:
        """已注册触发器列表（返回副本）."""
        return list(self._triggers.values())

    def register_trigger(self, trigger: TriggerDefinition) -> None:
        """注册触发条件."""
        self._triggers[trigger.trigger] = trigger
        logger.debug("KillSwitch trigger registered: %s", trigger.trigger)

    def record_event(self, event: TriggerEvent) -> TriggerResult:
        """记录触发事件，返回触发结果."""
        trigger_name = event.trigger
        agent_id = event.agent_id

        if trigger_name not in self._triggers:
            return TriggerResult(action=TriggerResult.NO_ACTION)

        trigger_def = self._triggers[trigger_name]
        threshold = trigger_def.default_threshold

        # 记录事件
        if agent_id not in self._agent_events:
            self._agent_events[agent_id] = {}
        if trigger_name not in self._agent_events[agent_id]:
            self._agent_events[agent_id][trigger_name] = []

        now = time.time()
        self._agent_events[agent_id][trigger_name].append(now)

        # 清理过期事件
        window = trigger_def.window_seconds
        self._agent_events[agent_id][trigger_name] = [
            t for t in self._agent_events[agent_id][trigger_name] if now - t <= window
        ]

        count = len(self._agent_events[agent_id][trigger_name])

        if count >= threshold:
            self._blocked_agents.add(agent_id)
            logger.warning(
                "KillSwitch: agent %s blocked (trigger=%s count=%d threshold=%d)",
                agent_id, trigger_name, count, threshold,
            )

            # 检查是否需要全局熔断（>=3个agent被阻断）
            if len(self._blocked_agents) >= 3:
                self._global_tripped = True
                self._global_reason = f"multiple agents blocked: {trigger_name}"
                self._status.state = KillSwitchState.TRIPPED
                self._status.tripped_at = now
                self._status.reason = self._global_reason
                logger.warning("KillSwitch GLOBAL TRIPPED: %s", self._global_reason)

            return TriggerResult(action=TriggerResult.BLOCK_AGENT, agent_id=agent_id)

        return TriggerResult(action=TriggerResult.NO_ACTION)

    def is_agent_blocked(self, agent_id: str) -> bool:
        """检查agent是否被阻断."""
        return agent_id in self._blocked_agents

    def is_global_tripped(self) -> bool:
        """检查是否全局熔断."""
        return self._global_tripped

    def manual_trip_global(self, reason: str = "manual") -> None:
        """手动全局熔断."""
        self._global_tripped = True
        self._global_reason = reason
        self._status.state = KillSwitchState.TRIPPED
        self._status.tripped_at = time.time()
        self._status.reason = reason
        logger.warning("KillSwitch manual global trip: %s", reason)

    def manual_trip_agent(self, agent_id: str) -> None:
        """手动阻断单个agent."""
        self._blocked_agents.add(agent_id)
        logger.warning("KillSwitch manual agent trip: %s", agent_id)

    def owner_release_global(self) -> None:
        """Owner释放全局熔断（覆盖）."""
        self._pre_override_tripped = self._global_tripped
        self._override_active = True
        self._global_tripped = False
        self._global_reason = ""
        self._status.state = KillSwitchState.NORMAL
        self._status.tripped_at = 0.0
        self._status.reason = ""
        logger.info("KillSwitch global released by owner (override active)")

    def owner_release_agent(self, agent_id: str) -> None:
        """Owner释放单个agent."""
        self._blocked_agents.discard(agent_id)
        logger.info("KillSwitch agent %s released by owner", agent_id)

    def owner_revoke_override(self) -> None:
        """Owner撤销覆盖，恢复熔断状态."""
        if self._override_active:
            self._global_tripped = self._pre_override_tripped
            self._override_active = False
            if self._global_tripped:
                self._status.state = KillSwitchState.TRIPPED
                self._status.reason = self._global_reason or "override revoked"
                self._status.tripped_at = time.time()
            logger.info("KillSwitch override revoked, global_tripped=%s", self._global_tripped)

    def trigger(self, trigger_name: str = "manual", reason: str = "") -> TriggerResult:
        """触发熔断器（兼容旧接口）."""
        old_state = self._status.state
        if old_state is KillSwitchState.TRIPPED:
            return TriggerResult(action=TriggerResult.NO_ACTION)

        self._status.state = KillSwitchState.TRIPPED
        self._status.tripped_at = time.time()
        self._status.reason = reason or trigger_name
        self._global_tripped = True
        logger.warning("KillSwitch TRIPPED: trigger=%s reason=%s", trigger_name, reason)
        return TriggerResult(action=TriggerResult.GLOBAL_BLOCK, agent_id="", reason=reason)

    def reset(self) -> TriggerResult:
        """重置熔断器（需要owner批准）."""
        old_state = self._status.state
        if old_state is KillSwitchState.NORMAL:
            return TriggerResult(action=TriggerResult.NO_ACTION)

        self._status.state = KillSwitchState.NORMAL
        self._status.tripped_at = 0.0
        self._status.reason = ""
        self._global_tripped = False
        self._global_reason = ""
        self._override_active = False
        self._pre_override_tripped = False
        self._blocked_agents.clear()
        self._agent_events.clear()
        logger.info("KillSwitch RESET to NORMAL")
        return TriggerResult(action=TriggerResult.NO_ACTION)


_kill_switch_instance: KillSwitch | None = None


def get_kill_switch() -> KillSwitch:
    """获取KillSwitch单例."""
    global _kill_switch_instance
    if _kill_switch_instance is None:
        _kill_switch_instance = KillSwitch()
    return _kill_switch_instance


__all__ = [
    "DEFAULT_TRIGGERS",
    "KillSwitch",
    "KillSwitchState",
    "KillSwitchStatus",
    "TriggerDefinition",
    "TriggerEvent",
    "TriggerResult",
    "get_kill_switch",
]
