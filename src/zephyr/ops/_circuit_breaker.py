# [A_module] module_id=MOD-RES__circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.ops._circuit_breaker
# [DOMAIN] D-OPS
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.governance.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_escalation_engine_imports.py
from zephyr.ops.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)

_SUBMODULES = [
    "alternative_path_blocker",
    "autonomy_regressor",
    "bare_repo_scanner",
    "blueprint_bloat_monitor",
    "blueprint_reconciler",
    "bus_factor_defense",
    "clock_guard",
    "config_scanner",
    "construction_verifier",
    "data_pipeline_guard",
    "deadlock_detector",
    "decision_fatigue",
    "decision_fatigue_cli",
    "forensic_package",
    "gap_analyzer",
    "human_factors",
    "maintenance_window_adapter",
    "meta_confidence",
    "meta_observability",
    "model_version_detector",
    "persuasion_detector",
    "provider_failover",
    "silence_detector",
    "spof_checker",
]

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
]
