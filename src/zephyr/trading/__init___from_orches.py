# [A_module] module_id=MOD-ORC_runtime_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md
# [MODULE] zephyr.trading
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""
AutoRuntime Core — 三层运行时运营中心（系统大脑）
==================================================
蓝图: ARC-0001 / spec.md v5.0.0

终极目标: 接入项目里的所有模块、系统、脚本，能灵活运用所有东西。
衡量标准: 孤儿率 = 未接入模块数 / 总模块数 → 目标 = 0%
"""

from __future__ import annotations

_SUBMODULES = [
    "action_dispatcher",
    "ai_audit_logger",
    "auto_dispatcher",
    "auto_integrator",
    "auto_runtime_core",
    "auto_task_generator",
    "boot_cron_jobs",
    "boot_hooks",
    "capability_card",
    "capability_registry",
    "capability_sync",
    "circadian_scheduler",
    "dream_cycle",
    "feedback-loop",
    "finalizer",
    "gpu_monitor",
    "health-monitor",
    "ide_health_daemon",
    "integration_registry",
    "lifecycle_manager",
    "module_onboarding_scanner",
    "night_shift_queue",
    "orphan_detector",
    "ports",
    "resource_optimization",
    "runtime_config",
    "speed_baseline_checker",
    "status_dashboard",
    "staging_area",
    "stop_gate",
    "task_gate",
    "windows_service",
    "work_dag",
    "work_orchestrator",
    "zombie_scanner",
    "__main__",
    "admission_controller",
    "autopilot",
    "conductor",
    "gpu_consensus_scheduler",
    "protection_index",
    "session_lifecycle",
    "verdict_engine",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.trading.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AutoRuntimeCore",
    "__main__",
    "action_dispatcher",
    "admission_controller",
    "ai_audit_logger",
    "auto_dispatcher",
    "auto_integrator",
    "auto_runtime_core",
    "auto_task_generator",
    "autopilot",
    "boot_cron_jobs",
    "boot_hooks",
    "capability_card",
    "capability_registry",
    "capability_sync",
    "circadian_scheduler",
    "conductor",
    "dream_cycle",
    "feedback_loop",
    "finalizer",
    "gpu_consensus_scheduler",
    "gpu_monitor",
    "health_monitor",
    "ide_health_daemon",
    "integration_registry",
    "lifecycle_manager",
    "module_onboarding_scanner",
    "night_shift_queue",
    "orphan_detector",
    "ports",
    "protection_index",
    "resource_optimization",
    "runtime_config",
    "session_lifecycle",
    "speed_baseline_checker",
    "staging_area",
    "status_dashboard",
    "stop_gate",
    "task_gate",
    "verdict_engine",
    "windows_service",
    "work_dag",
    "work_orchestrator",
    "zombie_scanner",
]
