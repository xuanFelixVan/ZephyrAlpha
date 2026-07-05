# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.ai_guards.config_safety_guard
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_config_safety_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""config_safety_guard.py — 配置自毁防护 (B16, DD90, TASK-017)"""

from dataclasses import dataclass


@dataclass
class ConfigGuardResult:
    key: str
    value: float
    min_val: float
    max_val: float
    valid: bool
    rejected: bool = False


class ConfigSafetyGuard:
    """Config key domain[min,max] Contract-YAML driven; 超界拒绝+告警 (DD90)."""

    _DOMAINS: dict[str, tuple[float, float]] = {
        "threshold_pct": (0.5, 0.99),
        "top_k": (1, 20),
        "max_age_s": (60, 7200),
    }

    def validate(self, key: str, value: float) -> ConfigGuardResult:
        domain = self._DOMAINS.get(key, (0.0, float("inf")))
        valid = domain[0] <= value <= domain[1]
        return ConfigGuardResult(
            key=key, value=value, min_val=domain[0], max_val=domain[1], valid=valid, rejected=not valid
        )
