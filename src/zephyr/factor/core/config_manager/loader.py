# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-CFG
# [MODULE] zephyr.factor.core.config_manager.loader
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng; zephyr.factor.core.batch_output; zephyr.factor.core.backpressure
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配置真源为 core/_config.yaml；改后重启进程即生效
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] yaml 不存在->返回空 dict（开发友好）；子节缺失->返回 {}
# [TESTS] tests/factor/test_config_manager.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core config_manager 加载器——加载 core/_config.yaml 策略参数。

借鉴 analysis/__init__.py:load_analysis_config() 模式。提供：
- load_core_config(): 加载完整配置 dict
- get_section(name): 取子节（如 "backpressure"），缺失返回 {}
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

log = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "_config.yaml"


def load_core_config() -> dict[str, Any]:
    """加载 core/_config.yaml 完整配置。

    Returns:
        配置 dict。文件不存在或为空时返回 {}（开发友好，不抛异常）。
    """
    if not _CONFIG_PATH.exists():
        log.warning("config_manager: 配置文件不存在 %s，返回空 dict", _CONFIG_PATH)
        return {}
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_section(name: str) -> dict[str, Any]:
    """取配置子节。

    Args:
        name: 子节名（如 "backpressure" / "batch_output" / "dag_manager" / "dist_feature_eng"）

    Returns:
        子节 dict。子节缺失或非 dict 时返回 {}。
    """
    config = load_core_config()
    section = config.get(name)
    if not isinstance(section, dict):
        return {}
    return section
