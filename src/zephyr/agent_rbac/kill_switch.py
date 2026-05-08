"""
L0 Kill Switch — 全局熔断机制

MOD-INF-018 §2.2  D-018-05

对标 K8s Circuit Breaker + 交易系统熔断 + CSA ATF Incident Response。
全局熔断：当 Agent 行为触发危险阈值时自动熔断 Agent 操作。

触发机制：
  - >= 13 种自动触发器
  - 熔断源隔离策略：单 Agent 触发仅阻断该 Agent
  - 多 Agent (>=2) 同时触发才全局熔断
  - 支持手动熔断/解除

设计原则：
  - 最先执行（L0 级别检查）
  - 不可覆盖、不可绕过
  - cooldown 机制防止过度阻断
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class KillSwitchState(Enum):
    NORMAL = "normal"
    SINGLE_AGENT_TRIPPED = "single_agent_tripped"
    GLOBAL_TRIPPED = "global_tripped"
    COOLDOWN = "cooldown"


class TriggerResult(Enum):
    NO_ACTION = "no_action"
    WARNING = "warning"
    BLOCK_AGENT = "block_agent"
    GLOBAL_BLOCK = "global_block"


@dataclass
class TriggerDefinition:
    trigger: str
    description: str
    default_threshold: int
    window_seconds: float
    cooldown_seconds: float
    auto_release: bool


@dataclass
class TriggerEvent:
    trigger: str
    agent_id: str
    timestamp: float = field(default_factory=time.time)
    context: dict = field(default_factory=dict)


@dataclass
class KillSwitchStatus:
    state: KillSwitchState = KillSwitchState.NORMAL
    tripped_triggers: list[str] = field(default_factory=list)
    tripped_agents: set[str] = field(default_factory=set)
    tripped_at: float = 0.0
    cooldown_until: float = 0.0
    global_tripped: bool = False
    owner_override: bool = False


DEFAULT_TRIGGERS: list[TriggerDefinition] = [
    TriggerDefinition(
        trigger="rapid_file_deletion",
        description="Agent deletes >= threshold non-temporary files in window",
        default_threshold=3,
        window_seconds=5.0,
        cooldown_seconds=30.0,
        auto_release=True,
    ),
    TriggerDefinition(
        trigger="permission_boundary_probe",
        description="Agent triggers >= threshold BLOCKED decisions in window",
        default_threshold=5,
        window_seconds=120.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="suspicious_sequence",
        description="Sequence Guard triggers >= threshold alerts in window",
        default_threshold=2,
        window_seconds=60.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="off_hours_destructive",
        description="Destructive operations during off-hours (22:00-06:00)",
        default_threshold=1,
        window_seconds=28800.0,
        cooldown_seconds=3600.0,
        auto_release=True,
    ),
    TriggerDefinition(
        trigger="config_file_blitz",
        description="Agent modifies >= threshold YAML files in window",
        default_threshold=10,
        window_seconds=60.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="signal_noise_attack",
        description="Alert density > P99 baseline * 10 in window",
        default_threshold=10,
        window_seconds=300.0,
        cooldown_seconds=600.0,
        auto_release=True,
    ),
    TriggerDefinition(
        trigger="sensitivity_label_blitz",
        description="Agent modifies >= threshold sensitivity labels in window",
        default_threshold=5,
        window_seconds=60.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="agent_spawn_storm",
        description="Parent agent creates >= threshold child agents in window",
        default_threshold=3,
        window_seconds=300.0,
        cooldown_seconds=600.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="unauthorized_protected_write",
        description="Agent attempts writing to L0 protected paths",
        default_threshold=1,
        window_seconds=10.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="multi_session_anomaly",
        description="Anomalous cross-session correlation detected",
        default_threshold=2,
        window_seconds=3600.0,
        cooldown_seconds=1800.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="rollback_storm",
        description=">= threshold rollbacks triggered in short window",
        default_threshold=3,
        window_seconds=60.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="clock_tampering",
        description="System clock or log timestamp anomalies detected",
        default_threshold=1,
        window_seconds=30.0,
        cooldown_seconds=600.0,
        auto_release=False,
    ),
    TriggerDefinition(
        trigger="credential_scan_blast",
        description="Credential/key scanning storms — rapid credential detection",
        default_threshold=5,
        window_seconds=60.0,
        cooldown_seconds=300.0,
        auto_release=False,
    ),
]


class KillSwitch:
    """L0 全局熔断器"""

    def __init__(self, triggers: Optional[list[TriggerDefinition]] = None) -> None:
        self._triggers = triggers or [TriggerDefinition(**td.__dict__) for td in DEFAULT_TRIGGERS]
        self._status = KillSwitchStatus()
        self._event_log: list[TriggerEvent] = []
        self._per_agent_counters: dict[str, dict[str, list[float]]] = {}
        self._pre_override_state: Optional[KillSwitchStatus] = None

    @property
    def triggers(self) -> list[TriggerDefinition]:
        return list(self._triggers)

    @property
    def status(self) -> KillSwitchStatus:
        return self._status

    @property
    def trigger_count(self) -> int:
        return len(self._triggers)

    def is_global_tripped(self) -> bool:
        if self._status.owner_override:
            return False
        if self._status.state == KillSwitchState.GLOBAL_TRIPPED:
            if self._status.cooldown_until > 0 and time.time() >= self._status.cooldown_until:
                self._try_auto_release()
                return self._status.state == KillSwitchState.GLOBAL_TRIPPED
            return True
        return False

    def is_agent_blocked(self, agent_id: str) -> bool:
        if self.is_global_tripped():
            return True
        if self._status.owner_override:
            return False
        return agent_id in self._status.tripped_agents

    def record_event(self, event: TriggerEvent) -> TriggerResult:
        self._event_log.append(event)
        self._cleanup_old_events()

        trigger_def = self._find_trigger(event.trigger)
        if trigger_def is None:
            return TriggerResult.NO_ACTION

        agent_counter = self._per_agent_counters.setdefault(event.agent_id, {})
        trigger_times = agent_counter.setdefault(event.trigger, [])
        trigger_times.append(event.timestamp)

        recent = [t for t in trigger_times if event.timestamp - t <= trigger_def.window_seconds]
        agent_counter[event.trigger] = recent

        if len(recent) >= trigger_def.default_threshold:
            return self._apply_trigger(trigger_def, event)

        return TriggerResult.WARNING

    def manual_trip_global(self, reason: str = "") -> None:
        self._status.state = KillSwitchState.GLOBAL_TRIPPED
        self._status.global_tripped = True
        self._status.tripped_at = time.time()
        self._status.tripped_triggers.append(f"manual:{reason}" if reason else "manual")
        self._status.owner_override = False

    def manual_trip_agent(self, agent_id: str) -> None:
        self._status.tripped_agents.add(agent_id)
        self._status.tripped_triggers.append(f"manual:agent:{agent_id}")

    def owner_release_global(self) -> None:
        self._pre_override_state = KillSwitchStatus(
            state=self._status.state,
            tripped_triggers=list(self._status.tripped_triggers),
            tripped_agents=set(self._status.tripped_agents),
            tripped_at=self._status.tripped_at,
            cooldown_until=self._status.cooldown_until,
            global_tripped=self._status.global_tripped,
            owner_override=False,
        )
        self._status.state = KillSwitchState.NORMAL
        self._status.global_tripped = False
        self._status.cooldown_until = 0.0
        self._status.owner_override = True

    def owner_release_agent(self, agent_id: str) -> None:
        self._status.tripped_agents.discard(agent_id)

    def owner_revoke_override(self) -> None:
        if self._pre_override_state is not None:
            self._status = self._pre_override_state
            self._pre_override_state = None
        self._status.owner_override = False

    def reset(self) -> None:
        self._status = KillSwitchStatus()
        self._event_log.clear()
        self._per_agent_counters.clear()
        self._pre_override_state = None

    def _find_trigger(self, trigger_name: str) -> Optional[TriggerDefinition]:
        for td in self._triggers:
            if td.trigger == trigger_name:
                return td
        return None

    def _apply_trigger(self, trigger_def: TriggerDefinition, event: TriggerEvent) -> TriggerResult:
        self._status.tripped_triggers.append(trigger_def.trigger)

        other_agents = [
            e.agent_id for e in self._event_log
            if e.trigger == trigger_def.trigger and e.agent_id != event.agent_id
            and time.time() - e.timestamp <= trigger_def.window_seconds * 2
        ]

        if len(set(other_agents)) >= 2:
            self._status.state = KillSwitchState.GLOBAL_TRIPPED
            self._status.global_tripped = True
            self._status.tripped_at = time.time()
            if trigger_def.auto_release:
                self._status.cooldown_until = time.time() + trigger_def.cooldown_seconds
            return TriggerResult.GLOBAL_BLOCK

        self._status.tripped_agents.add(event.agent_id)
        if self._status.state != KillSwitchState.GLOBAL_TRIPPED:
            self._status.state = KillSwitchState.SINGLE_AGENT_TRIPPED
        return TriggerResult.BLOCK_AGENT

    def _try_auto_release(self) -> None:
        if self._status.cooldown_until > 0 and time.time() >= self._status.cooldown_until:
            self._status.state = KillSwitchState.NORMAL
            self._status.global_tripped = False
            self._status.cooldown_until = 0.0

    def _cleanup_old_events(self) -> None:
        cutoff = time.time() - 7200
        self._event_log = [e for e in self._event_log if e.timestamp > cutoff]


_kill_switch_instance: Optional[KillSwitch] = None


def get_kill_switch() -> KillSwitch:
    global _kill_switch_instance
    if _kill_switch_instance is None:
        _kill_switch_instance = KillSwitch()
    return _kill_switch_instance
