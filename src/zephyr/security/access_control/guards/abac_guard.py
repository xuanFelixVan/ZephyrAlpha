# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.abac_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] L0_INTERN never allowed modify:blueprint; temporal classification always returns valid category
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() never raises; returns tuple[bool, str]; classify_temporal() never raises
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_abac_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ABACGuard — 基于属性的权限守卫.

依据蓝图 MOD-INF-018 §3:
- 基于属性（成熟度、时间、敏感度）判断权限
- L0_INTERN 不能修改蓝图
- 时间分类（正常/下班/周末/午餐高峰）
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from zephyr.security.access_control.identity import MATURITY_TLB_LIMITS, MaturityLevel
from zephyr.shared.utils.time_utils import now_utc


class TemporalCategory(str, Enum):
    """时间分类枚举."""

    NORMAL = "NORMAL"
    OFF_HOURS = "OFF_HOURS"
    LUNCH_PEAK = "LUNCH_PEAK"
    WEEKEND = "WEEKEND"


class SensitivityLabel(str, Enum):
    """敏感度标签枚举."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    HIGH = "HIGH"
    RESTRICTED = "RESTRICTED"


MATURITY_OPERATION_MAP: dict[MaturityLevel, list[str]] = {
    MaturityLevel.L0_INTERN: ["read:docs", "read:src"],
    MaturityLevel.L1_JUNIOR: ["read:docs", "read:src", "write:tests"],
    MaturityLevel.L2_REGULAR: [
        "read:docs", "read:src", "write:src", "write:tests", "execute:scripts",
    ],
    MaturityLevel.L3_SENIOR: [
        "read:docs", "read:src", "write:src", "write:tests",
        "execute:scripts", "modify:blueprint",
    ],
    MaturityLevel.L4_PRINCIPAL: [
        "read:docs", "read:src", "write:src", "write:tests",
        "execute:scripts", "modify:blueprint", "admin:override",
    ],
}

SENSITIVITY_MIN_MATURITY: dict[SensitivityLabel, MaturityLevel] = {
    SensitivityLabel.PUBLIC: MaturityLevel.L0_INTERN,
    SensitivityLabel.INTERNAL: MaturityLevel.L1_JUNIOR,
    SensitivityLabel.CONFIDENTIAL: MaturityLevel.L2_REGULAR,
    SensitivityLabel.HIGH: MaturityLevel.L3_SENIOR,
    SensitivityLabel.RESTRICTED: MaturityLevel.L4_PRINCIPAL,
}

_SENSITIVITY_KEYWORDS: list[tuple[str, SensitivityLabel]] = [
    ("top secret", SensitivityLabel.RESTRICTED),
    ("password", SensitivityLabel.HIGH),
    ("secret", SensitivityLabel.HIGH),
    ("key", SensitivityLabel.CONFIDENTIAL),
    ("internal", SensitivityLabel.INTERNAL),
]

_BLITZ_THRESHOLD = 5
_BLITZ_WINDOW_SECONDS = 60.0


@dataclass
class ABACContext:
    """ABAC 上下文.

    Attributes:
        operation: 操作名称
        temporal: 时间分类
        intent: 操作意图（如 maintenance, deployment, audit）
        sensitivity: 敏感度标签
    """

    operation: str = ""
    temporal: TemporalCategory = TemporalCategory.NORMAL
    intent: str = "unknown"
    sensitivity: SensitivityLabel = SensitivityLabel.INTERNAL


@dataclass
class TLBRecord:
    """TLB（Translation Lookaside Buffer）记录.

    Attributes:
        agent_id: agent ID
        counter: 当前计数
        limit: 上限
    """

    agent_id: str = ""
    counter: int = 0
    limit: int = 100


class ABACGuard:
    """基于属性的权限守卫.

    根据属性（成熟度、时间、敏感度）判断权限。
    """

    def __init__(self) -> None:
        self._tlb: dict[str, TLBRecord] = {}
        self._sensitivity_changes: list[float] = []

    @staticmethod
    def classify_temporal(timestamp: float | None = None) -> TemporalCategory:
        """根据时间戳分类.

        Args:
            timestamp: Unix 时间戳（可选，默认当前时间）

        Returns:
            TemporalCategory: 时间分类
        """
        if timestamp is None:
            now = now_utc()
        else:
            now = datetime.fromtimestamp(timestamp)
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        if weekday >= 5:
            return TemporalCategory.WEEKEND
        if hour < 8 or hour >= 18:
            return TemporalCategory.OFF_HOURS
        if 12 <= hour < 13:
            return TemporalCategory.LUNCH_PEAK
        return TemporalCategory.NORMAL

    @staticmethod
    def detect_sensitivity_from_content(content: str) -> SensitivityLabel:
        """根据内容检测敏感度.

        Args:
            content: 内容文本

        Returns:
            SensitivityLabel: 检测到的敏感度标签
        """
        if not content:
            return SensitivityLabel.PUBLIC
        content_lower = content.lower()
        for keyword, label in _SENSITIVITY_KEYWORDS:
            if keyword in content_lower:
                return label
        return SensitivityLabel.PUBLIC

    def record_sensitivity_label_change(self, label: str, timestamp: float | None = None) -> None:
        """记录敏感度标签变更.

        Args:
            label: 变更的标签
            timestamp: 变更时间戳（可选，默认当前时间）
        """
        ts = timestamp if timestamp is not None else time.time()
        self._sensitivity_changes.append(ts)

    def is_sensitivity_label_blitz(self) -> bool:
        """检测是否发生敏感度标签变更风暴.

        Returns:
            bool: 如果在时间窗口内变更次数 >= 阈值则返回 True
        """
        now = time.time()
        recent = [ts for ts in self._sensitivity_changes if now - ts <= _BLITZ_WINDOW_SECONDS]
        return len(recent) >= _BLITZ_THRESHOLD

    def reset_tlb(self, agent_id: str) -> None:
        """重置指定 agent 的 TLB 计数.

        Args:
            agent_id: agent ID
        """
        if agent_id in self._tlb:
            self._tlb[agent_id].counter = 0

    def reset_all(self) -> None:
        """重置所有 TLB 记录和敏感度变更记录."""
        self._tlb.clear()
        self._sensitivity_changes.clear()

    def _is_destructive(self, operation: str) -> bool:
        """判断操作是否为破坏性操作."""
        return (
            operation.startswith("delete:")
            or operation.startswith("modify:")
            or operation.startswith("write:")
            or operation.startswith("execute:")
        )

    def check(self, agent: Any, ctx: ABACContext) -> tuple[bool, str]:
        """检查操作权限.

        Args:
            agent: AgentIdentity 实例
            ctx: ABAC 上下文

        Returns:
            tuple[bool, str]: (是否允许, 原因)
        """
        operation = getattr(ctx, "operation", "")
        maturity = getattr(agent, "maturity", None)
        agent_id = getattr(agent, "session_id", "")

        # TLB 检查
        if agent_id:
            if agent_id in self._tlb:
                record = self._tlb[agent_id]
            else:
                limit = MATURITY_TLB_LIMITS.get(
                    maturity.value if maturity else "L0_INTERN", 100
                )
                record = TLBRecord(agent_id=agent_id, counter=0, limit=limit)
                self._tlb[agent_id] = record
            record.counter += 1
            if record.counter > record.limit:
                return (False, f"TLB limit exceeded for {agent_id} (limit={record.limit})")

        # 成熟度检查 — L0_INTERN 只能读
        if maturity is MaturityLevel.L0_INTERN:
            if not operation.startswith("read:"):
                return (False, f"Maturity L0_INTERN cannot perform: {operation}")

        # 敏感度检查
        sensitivity = getattr(ctx, "sensitivity", SensitivityLabel.INTERNAL)
        if sensitivity in SENSITIVITY_MIN_MATURITY:
            required = SENSITIVITY_MIN_MATURITY[sensitivity]
            levels = list(MaturityLevel)
            if maturity and levels.index(maturity) < levels.index(required):
                return (
                    False,
                    f"Sensitivity {sensitivity.value} requires maturity {required.value}",
                )

        # 时间检查
        temporal = getattr(ctx, "temporal", TemporalCategory.NORMAL)
        if temporal in (TemporalCategory.OFF_HOURS, TemporalCategory.WEEKEND):
            if maturity is MaturityLevel.L0_INTERN:
                if temporal is TemporalCategory.WEEKEND:
                    return (False, f"Weekend blocked for {maturity.value}")
                return (False, f"Off-hours blocked for {maturity.value}")
            if maturity in (MaturityLevel.L1_JUNIOR, MaturityLevel.L2_REGULAR):
                if operation.startswith("delete:") or operation.startswith("modify:"):
                    return (
                        False,
                        f"Destructive operation blocked in off-hours for {maturity.value}",
                    )
                if maturity is MaturityLevel.L1_JUNIOR and self._is_destructive(operation):
                    return (
                        False,
                        f"Destructive operation blocked in off-hours for {maturity.value}",
                    )
        elif temporal is TemporalCategory.LUNCH_PEAK:
            if maturity is MaturityLevel.L1_JUNIOR:
                if operation.startswith("batch:") or operation.startswith("execute:"):
                    return (
                        False,
                        f"Heavy operation throttled during lunch peak for {maturity.value}",
                    )

        # 默认允许
        return (True, "allowed by ABAC")


__all__ = [
    "MATURITY_OPERATION_MAP",
    "SENSITIVITY_MIN_MATURITY",
    "ABACContext",
    "ABACGuard",
    "SensitivityLabel",
    "TLBRecord",
    "TemporalCategory",
]
