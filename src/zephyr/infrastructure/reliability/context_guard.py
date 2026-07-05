# [BLUEPRINT] SRC-134 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.reliability.context_guard
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
# [A_module] module_id=MOD-INF_context_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Context Guard — 上下文契约守卫。

依据：
    蓝图 MOD-TASK_SYSTEM §6.2.4 + v0.6.0
    任务卡 TASK-INF-0108 (Part 4/4)

功能：
    - 上下文白名单：只允许 upstream_files + downstream_outputs 中声明的文件
    - 超范围访问 → 告警 + 拒绝
    - forbidden_touch 强制执行
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AccessCheck:
    file_path: str
    allowed: bool
    reason: str
    is_allowed_touch: bool = False
    is_forbidden_touch: bool = False


@dataclass
class ContextGuardResult:
    all_allowed: bool
    checks: list[AccessCheck]
    blocked_files: list[str]
    warning_files: list[str]


class ContextGuard:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def validate_access(self, task_card: dict[str, Any], actual_touched: list[str]) -> ContextGuardResult:
        allowed_touch = set(task_card.get("allowed_touch", []))
        forbidden_touch = set(task_card.get("forbidden_touch", []))
        upstream = {f.get("file_path", "") for f in task_card.get("upstream_files", []) if isinstance(f, dict)}
        downstream = {o.get("path", "") for o in task_card.get("downstream_outputs", [])}

        all_allowed_set = allowed_touch | upstream | downstream | {"", "N/A"}

        checks: list[AccessCheck] = []
        blocked: list[str] = []
        warnings: list[str] = []

        for file_path in actual_touched:
            fp_norm = file_path.strip()

            if fp_norm in forbidden_touch:
                checks.append(
                    AccessCheck(
                        file_path=file_path,
                        allowed=False,
                        reason=f"FORBIDDEN: {file_path} is in forbidden_touch",
                        is_forbidden_touch=True,
                    )
                )
                blocked.append(file_path)
                continue

            if fp_norm in all_allowed_set:
                checks.append(
                    AccessCheck(
                        file_path=file_path,
                        allowed=True,
                        reason="Explicitly allowed (allowed_touch/upstream/downstream)",
                        is_allowed_touch=fp_norm in allowed_touch,
                    )
                )
            else:
                warnings.append(file_path)
                checks.append(
                    AccessCheck(
                        file_path=file_path,
                        allowed=False,
                        reason=f"WARNING: {file_path} not in allowed_touch/upstream/downstream",
                    )
                )

        return ContextGuardResult(
            all_allowed=len(blocked) == 0,
            checks=checks,
            blocked_files=blocked,
            warning_files=warnings,
        )

    def check_forbidden(self, actual_touched: list[str], forbidden_touch: list[str]) -> list[AccessCheck]:
        forbidden_set = set(forbidden_touch)
        checks: list[AccessCheck] = []

        for fp in actual_touched:
            if fp in forbidden_set:
                checks.append(
                    AccessCheck(
                        file_path=fp,
                        allowed=False,
                        reason=f"VIOLATION: {fp} is in forbidden_touch",
                        is_forbidden_touch=True,
                    )
                )

        return checks
