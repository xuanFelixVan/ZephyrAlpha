# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.auto_rollback_trigger
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
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
# [A_module] module_id=MOD-INF_auto_rollback_trigger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AutoRollbackTrigger — 自动回滚触发器。

依据: 蓝图 MOD-INF-021 §7 Phase 1.5 + §6.2 B15 + 决策 D-021-05

监听 auto_guard 后验结果 + 失败信号三分类:
    hard_failure  → 立即回滚
    soft_failure  → forward-fix 优先
    transient     → 重试 (不回滚)

三分类规则:
    Hard:   Drift Detector 检测 / CI FAIL / G6 secrets leak / DB corruption
    Soft:   G0-G3 格式/语法门禁失败 / lint 失败 / 缩进错误
    Transient: timeout / network / rate_limit / temp_file_lock
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FailureCategory(str, Enum):
    HARD = "hard_failure"
    SOFT = "soft_failure"
    TRANSIENT = "transient"


class ActionType(str, Enum):
    """5.96.2 修复：原 TriggerDecision 含 3 个布尔字段 (should_rollback/retry_allowed/
    forward_fix_allowed) 与 action 完全冗余，重构为枚举 + @property 派生，消除互斥动作的
    布尔组合不一致风险。"""

    ROLLBACK = "ROLLBACK_IMMEDIATE"
    FORWARD_FIX = "FORWARD_FIX_PREFERRED"
    UPGRADE_TO_SOFT = "UPGRADE_TO_SOFT"
    RETRY = "RETRY"

    @property
    def should_rollback(self) -> bool:
        return self is ActionType.ROLLBACK

    @property
    def retry_allowed(self) -> bool:
        return self in (ActionType.FORWARD_FIX, ActionType.RETRY)

    @property
    def forward_fix_allowed(self) -> bool:
        return self in (ActionType.FORWARD_FIX, ActionType.UPGRADE_TO_SOFT)


@dataclass
class AutoGuardResult:
    source: str
    gate_id: str
    task_id: str
    passed: bool
    error_message: str
    error_code: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerDecision:
    category: FailureCategory
    action: ActionType
    reason: str

    @property
    def should_rollback(self) -> bool:
        return self.action.should_rollback

    @property
    def retry_allowed(self) -> bool:
        return self.action.retry_allowed

    @property
    def forward_fix_allowed(self) -> bool:
        return self.action.forward_fix_allowed


HARD_SOURCES: set[str] = {
    "drift-detector",
    "CI",
    "G6_secrets",
    "db_integrity",
    "kill_switch",
}
SOFT_SOURCES: set[str] = {
    "G0",
    "G1",
    "G2",
    "G3",
    "lint",
    "style",
    "syntax",
}
TRANSIENT_SOURCES: set[str] = {
    "timeout",
    "network",
    "rate_limit",
    "temp_file_lock",
    "disk_quota",
}

HARD_PATTERNS: list[str] = [
    "corruption",
    "integrity check failed",
    "data loss",
    "secrets leak",
    "credentials exposed",
    "drift detected",
    "unauthorized access",
]
SOFT_PATTERNS: list[str] = [
    "indentation error",
    "syntax error",
    "missing docstring",
    "lint failed",
    "type error",
    "import error",
]
TRANSIENT_PATTERNS: list[str] = [
    "timeout",
    "connection refused",
    "rate limit",
    "too many requests",
    "temporary failure",
    "retry later",
]


class AutoRollbackTrigger:
    def __init__(self, max_retries: int = 3) -> None:
        self._max_retries = max_retries
        self._retry_counts: dict[str, int] = {}

    def classify(self, result: AutoGuardResult) -> TriggerDecision:
        category = self._classify_failure(result)
        return self._build_decision(category, result)

    def _classify_failure(self, result: AutoGuardResult) -> FailureCategory:
        if result.passed:
            return FailureCategory.SOFT

        source = result.source.lower()
        error_msg = result.error_message.lower()

        for src in HARD_SOURCES:
            if src.lower() in source:
                return FailureCategory.HARD

        for src in TRANSIENT_SOURCES:
            if src.lower() in source:
                return FailureCategory.TRANSIENT

        for src in SOFT_SOURCES:
            if src.lower() in source:
                return FailureCategory.SOFT

        for pattern in HARD_PATTERNS:
            if pattern.lower() in error_msg:
                return FailureCategory.HARD

        for pattern in SOFT_PATTERNS:
            if pattern.lower() in error_msg:
                return FailureCategory.SOFT

        for pattern in TRANSIENT_PATTERNS:
            if pattern.lower() in error_msg:
                return FailureCategory.TRANSIENT

        return FailureCategory.SOFT

    def _build_decision(self, category: FailureCategory, result: AutoGuardResult) -> TriggerDecision:
        if category is FailureCategory.HARD:
            return TriggerDecision(
                category=category,
                action=ActionType.ROLLBACK,
                reason=f"HARD failure from {result.source}: {result.error_message[:80]}",
            )
        elif category is FailureCategory.SOFT:
            return TriggerDecision(
                category=category,
                action=ActionType.FORWARD_FIX,
                reason=f"SOFT failure from {result.source}: {result.error_message[:80]}",
            )
        else:
            key = f"{result.task_id}:{result.gate_id}"
            self._retry_counts[key] = self._retry_counts.get(key, 0) + 1
            retries_left = self._max_retries - self._retry_counts[key]

            if retries_left <= 0:
                return TriggerDecision(
                    category=category,
                    action=ActionType.UPGRADE_TO_SOFT,
                    reason=f"TRANSIENT retries exhausted ({self._max_retries}) for {result.source}",
                )

            return TriggerDecision(
                category=category,
                action=ActionType.RETRY,
                reason=f"TRANSIENT from {result.source}: {retries_left} retries left",
            )

    def process_guard_result(self, result: AutoGuardResult) -> TriggerDecision:
        decision = self.classify(result)
        return decision

    @property
    def retry_counts(self) -> dict[str, int]:
        return dict(self._retry_counts)
