# [A_module] module_id=MOD-SHR_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.config
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""Configuration loader for Zephyr Alpha."""

from zephyr.infrastructure.config.shared.config import loader
from zephyr.infrastructure.config.shared.config.loader import (
    ConfigLoadError,
    load_yaml_config,
    load_yaml_config_validated,
)

__all__ = [
    "ConfigLoadError",
    "load_yaml_config",
    "load_yaml_config_validated",
    "loader",
]
