# [A_module] module_id=MOD-SHR_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
"""Configuration loader for Zephyr Alpha."""

from zephyr.shared.config.loader import (
    ConfigLoadError,
    load_yaml_config,
    load_yaml_config_validated,
)
from zephyr.shared.config import loader

__all__ = [
    "load_yaml_config",
    "load_yaml_config_validated",
    "ConfigLoadError",
    "loader",
]
