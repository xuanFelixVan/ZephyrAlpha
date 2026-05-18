# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §
"""
AutoRuntime Core — 三层运行时运营中心（系统大脑）
==================================================
蓝图: ARC-0001 / spec.md v5.0.0

终极目标: 接入项目里的所有模块、系统、脚本，能灵活运用所有东西。
衡量标准: 孤儿率 = 未接入模块数 / 总模块数 → 目标 = 0%
"""

from __future__ import annotations

__all__ = [
    'AutoRuntimeCore',
    'action_dispatcher',
    'ai_audit_logger',
    'auto_integrator',
    'auto_runtime_core',
    'auto_task_generator',
    'boot_cron_jobs',
    'boot_hooks',
    'capability_card',
    'capability_registry',
    'capability_sync',
    'circadian_scheduler',
    'dream_cycle',
    'feedback_loop',
    'finalizer',
    'health_monitor',
    'integration_registry',
    'lifecycle_manager',
    'module_onboarding_scanner',
    'night_shift_queue',
    'orphan_detector',
    'resource_optimization',
    'runtime_config',
    'status_dashboard',
    'stop_gate',
    'task_gate',
    'windows_service',
    'work_dag',
    'work_orchestrator',
]