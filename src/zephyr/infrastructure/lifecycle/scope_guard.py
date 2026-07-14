# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.lifecycle.scope_guard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_scope_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Scope Guard — 范围蔓延检测与阻断。

依据：
    蓝图 MOD-TASK_SYSTEM §6.11.3 + v0.6.0
    任务卡 TASK-INF-0118
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class ScopeDrift:
    task_id: str
    expected_touch: list[str]
    actual_touch: list[str]
    extra_touch: list[str]
    severity: str
    timestamp_utc: str


@dataclass
class ScopeGuardConfig:
    max_extra_touch: int = 3
    auto_block_on_critical: bool = True
    warn_on_extra: bool = True


class ScopeGuard:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._config = ScopeGuardConfig()
        self._drift_log: list[ScopeDrift] = []
        self._blocked_tasks: set[str] = set()

    def validate_scope(self, task_card: dict[str, Any], actual_touched: list[str]) -> ScopeDrift | None:
        task_id = task_card.get("task_id", "")
        expected = set(task_card.get("allowed_touch", []))
        upstream = {f if isinstance(f, str) else f.get("file_path", "") for f in task_card.get("upstream_files", [])}
        downstream = {o.get("path", "") for o in task_card.get("downstream_outputs", [])}

        expected = expected | upstream | downstream | {""}
        actual_set = set(actual_touched)

        extra = actual_set - expected

        if not extra:
            return None

        if len(extra) > self._config.max_extra_touch:
            severity = "CRITICAL"
        elif len(extra) > 1:
            severity = "HIGH"
        else:
            severity = "LOW"

        drift = ScopeDrift(
            task_id=task_id,
            expected_touch=sorted(expected),
            actual_touch=actual_touched,
            extra_touch=sorted(extra),
            severity=severity,
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        self._drift_log.append(drift)

        if severity == "CRITICAL" and self._config.auto_block_on_critical:
            self._blocked_tasks.add(task_id)

        return drift

    def is_blocked(self, task_id: str) -> bool:
        return task_id in self._blocked_tasks

    def unblock(self, task_id: str) -> None:
        self._blocked_tasks.discard(task_id)

    def get_drift_history(self, task_id: str = "") -> list[ScopeDrift]:
        if task_id:
            return [d for d in self._drift_log if d.task_id == task_id]
        return list(self._drift_log)
