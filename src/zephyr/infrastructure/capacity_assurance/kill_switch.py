# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.kill_switch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS] zephyr.autonomy_core.context.context_pipeline_auto
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] err_count>threshold -> fuse off; needs manual reset (DD110)
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FuseState
# [TESTS] tests/context/test_context_pipeline_auto.py
# [A_module] module_id=MOD-INF-001_kill_switch | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/kill_switch.py 迁移至
#   infrastructure/capacity_assurance/kill_switch.py（blueprint actual_disk_path 真源）。
#   原始 autonomy_core/kill_switch.py 的 SRC-0041 注释提到 shared/kill_switch.py 为
#   统一 SSoT 导出，但该文件当前不存在；本文件保留独立实现，待 future review 决定是否合并。
"""kill_switch.py -- safety circuit breaker (DD110, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FuseState:
    on: bool
    trigger_reason: str
    manual_reset_needed: bool


# class-name-alias: capacity-assurance per-session error-count fuse (DD110); name shadows canonical zephyr.security.access_control.kill_switch.KillSwitch (MOD-SEC_kill_switch) but semantics differ (err threshold vs system-level breaker). Distinct domain (D_INFRA_RUNTIME) — not a re-export.
class KillSwitch:
    """per-session err>threshold -> fuse off. needs manual reset (DD110)."""

    def __init__(self, threshold: int = 5) -> None:
        self._threshold = threshold
        self._error_count = 0
        self._fuse_on = False

    def record_error(self, reason: str = "") -> FuseState:
        self._error_count += 1
        if self._error_count >= self._threshold:
            self._fuse_on = True
        return FuseState(on=self._fuse_on, trigger_reason=reason, manual_reset_needed=True)

    def reset(self) -> None:
        self._error_count = 0
        self._fuse_on = False
