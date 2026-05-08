"""
L2 ABAC Guard — 五维属性权限 (Intent / Maturity / Temporal / Sensitivity / TLB)

MOD-INF-018 §2.5  D-018-07

五维判定：意图感知(intent) + Agent成熟度(maturity) + 时间窗口(temporal) + 资源敏感性(sensitivity) + TLB限流(tlb)
从"谁"升级到"什么上下文"——不再仅凭身份判定，而是五维上下文综合裁决。

off_hours 自动降级 + sensitivity_label_blitz 熔断 + per-Agent TLB。
"""

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from typing import Optional

from zephyr.agent_rbac.identity import AgentIdentity, MaturityLevel, MATURITY_TLB_LIMITS


def _maturity_value(agent: AgentIdentity) -> str:
    m = agent.maturity
    if isinstance(m, MaturityLevel):
        return m.value
    return m


def _maturity_enum(agent: AgentIdentity) -> MaturityLevel:
    m = agent.maturity
    if isinstance(m, MaturityLevel):
        return m
    return MaturityLevel(m)


class TemporalCategory(str, Enum):
    NORMAL = "normal"
    OFF_HOURS = "off_hours"
    LUNCH_PEAK = "lunch_peak"
    WEEKEND = "weekend"


class SensitivityLabel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    HIGH = "high"
    RESTRICTED = "restricted"


SENSITIVITY_MIN_MATURITY: dict[SensitivityLabel, MaturityLevel] = {
    SensitivityLabel.PUBLIC: MaturityLevel.L0_INTERN,
    SensitivityLabel.INTERNAL: MaturityLevel.L1_JUNIOR,
    SensitivityLabel.CONFIDENTIAL: MaturityLevel.L2_REGULAR,
    SensitivityLabel.HIGH: MaturityLevel.L3_SENIOR,
    SensitivityLabel.RESTRICTED: MaturityLevel.L4_PRINCIPAL,
}

MATURITY_OPERATION_MAP: dict[MaturityLevel, list[str]] = {
    MaturityLevel.L0_INTERN: ["read"],
    MaturityLevel.L1_JUNIOR: ["read", "write:tests", "execute:tests"],
    MaturityLevel.L2_REGULAR: ["read", "write", "execute"],
    MaturityLevel.L3_SENIOR: ["read", "write", "execute", "modify:config"],
    MaturityLevel.L4_PRINCIPAL: ["*"],
}


@dataclass
class ABACContext:
    intent: str = "unknown"
    temporal: TemporalCategory = TemporalCategory.NORMAL
    sensitivity: SensitivityLabel = SensitivityLabel.INTERNAL
    operation: str = ""


@dataclass
class TLBRecord:
    agent_id: str
    counter: int = 0
    window_start: float = field(default_factory=time.time)
    limit: int = 100


class ABACGuard:
    def __init__(self) -> None:
        self._tlb_records: dict[str, TLBRecord] = {}
        self._sensitivity_label_changes: list[tuple[str, float]] = []
        self._sensitivity_blitz_threshold = 5
        self._sensitivity_blitz_window = 60

    def check(self, agent: AgentIdentity, context: ABACContext) -> tuple[bool, str]:
        temporal_block = self._check_temporal(agent, context)
        if temporal_block:
            return False, temporal_block

        maturity_block = self._check_maturity(agent, context.operation)
        if maturity_block:
            return False, maturity_block

        sensitivity_block = self._check_sensitivity(agent, context.sensitivity)
        if sensitivity_block:
            return False, sensitivity_block

        tlb_ok, tlb_msg = self._check_tlb(agent)
        if not tlb_ok:
            return False, tlb_msg

        return True, "ABAC pass: all 5 dimensions OK"

    def _check_temporal(self, agent: AgentIdentity, context: ABACContext) -> Optional[str]:
        if context.temporal == TemporalCategory.WEEKEND:
            if _maturity_enum(agent) == MaturityLevel.L0_INTERN:
                return f"Weekend execution blocked for L0_INTERN agent {agent.session_id}"
            return None

        if context.temporal == TemporalCategory.OFF_HOURS:
            if _maturity_enum(agent) == MaturityLevel.L0_INTERN:
                return f"Off-hours execution blocked for L0_INTERN agent {agent.session_id}"
            if _maturity_enum(agent) in (MaturityLevel.L1_JUNIOR, MaturityLevel.L2_REGULAR):
                destructive_ops = ["delete:", "rm ", "remove:", "format:"]
                for pattern in destructive_ops:
                    if pattern in context.operation:
                        return f"Destructive operation '{context.operation}' blocked during off-hours"

        if context.temporal == TemporalCategory.LUNCH_PEAK:
            if _maturity_enum(agent) in (MaturityLevel.L0_INTERN, MaturityLevel.L1_JUNIOR):
                heavy_ops = ["batch:", "migrate:", "deploy:", "publish:"]
                for pattern in heavy_ops:
                    if pattern in context.operation:
                        return f"Heavy operation '{context.operation}' throttled during lunch peak"

        return None

    def _check_maturity(self, agent: AgentIdentity, operation: str) -> Optional[str]:
        allowed = MATURITY_OPERATION_MAP.get(_maturity_enum(agent), ["read"])
        if "*" in allowed:
            return None
        op_category = operation.split(":")[0] if ":" in operation else operation
        for a in allowed:
            if a == op_category or (":" in a and operation.startswith(a.split(":")[0])):
                return None
        return f"Maturity level {_maturity_value(agent)} not authorized for '{operation}'"

    def _check_sensitivity(self, agent: AgentIdentity, sensitivity: SensitivityLabel) -> Optional[str]:
        min_maturity = SENSITIVITY_MIN_MATURITY.get(sensitivity, MaturityLevel.L4_PRINCIPAL)
        levels = list(MaturityLevel)
        agent_maturity = _maturity_enum(agent)
        agent_idx = levels.index(agent_maturity) if agent_maturity in levels else 0
        min_idx = levels.index(min_maturity) if min_maturity in levels else len(levels) - 1
        if agent_idx < min_idx:
            return f"Sensitivity '{sensitivity.value}' requires {min_maturity.value}, agent is {_maturity_value(agent)}"
        return None

    def _check_tlb(self, agent: AgentIdentity) -> tuple[bool, str]:
        limit = agent.get_tlb_limit()
        if agent.session_id not in self._tlb_records:
            self._tlb_records[agent.session_id] = TLBRecord(
                agent_id=agent.session_id,
                limit=limit,
            )
        record = self._tlb_records[agent.session_id]
        now = time.time()
        if now - record.window_start > 60:
            record.counter = 0
            record.window_start = now
        record.counter += 1
        if record.counter > record.limit:
            return False, f"TLB limit exceeded: {record.counter}/{record.limit}"
        return True, "TLB OK"

    def record_sensitivity_label_change(self, label: str, timestamp: Optional[float] = None) -> int:
        ts = timestamp or time.time()
        self._sensitivity_label_changes.append((label, ts))
        cutoff = ts - self._sensitivity_blitz_window
        self._sensitivity_label_changes = [
            (l, t) for l, t in self._sensitivity_label_changes if t > cutoff
        ]
        return len(self._sensitivity_label_changes)

    def is_sensitivity_label_blitz(self) -> bool:
        return len(self._sensitivity_label_changes) >= self._sensitivity_blitz_threshold

    def reset_tlb(self, agent_id: str) -> None:
        self._tlb_records.pop(agent_id, None)

    def reset_all(self) -> None:
        self._tlb_records.clear()
        self._sensitivity_label_changes.clear()

    @staticmethod
    def classify_temporal(timestamp: Optional[float] = None) -> TemporalCategory:
        ts = timestamp or time.time()
        tm = time.localtime(ts)
        hour = tm.tm_hour
        wday = tm.tm_wday
        if wday in (5, 6):
            return TemporalCategory.WEEKEND
        if hour < 8 or hour >= 22:
            return TemporalCategory.OFF_HOURS
        if 12 <= hour < 14:
            return TemporalCategory.LUNCH_PEAK
        return TemporalCategory.NORMAL

    @staticmethod
    def detect_sensitivity_from_content(content: str) -> SensitivityLabel:
        patterns = {
            SensitivityLabel.RESTRICTED: [r"(?i)top.secret", r"(?i)need.to.know"],
            SensitivityLabel.HIGH: [r"(?i)password", r"(?i)secret.key", r"(?i)private.key"],
            SensitivityLabel.CONFIDENTIAL: [r"(?i)api.key", r"(?i)token", r"(?i)credential"],
            SensitivityLabel.INTERNAL: [r"(?i)internal", r"(?i)draft"],
        }
        for label, patterns_list in patterns.items():
            for pat in patterns_list:
                if re.search(pat, content):
                    return label
        return SensitivityLabel.PUBLIC
