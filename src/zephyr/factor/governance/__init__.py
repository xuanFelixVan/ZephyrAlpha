# [BLUEPRINT] MOD-L02-GOV | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV
# [MODULE] zephyr.factor.governance
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.lifecycle.state_machine; zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [STARTUP] imported
# [MATURITY] production
# [TTL] permanent
"""D_FACTOR governance 子包——因子生命周期治理工具链。

提供因子生命周期状态机、ABS001 上线门禁、灰度发布、六步流程编排、治理引擎。
所有治理参数从 _config.yaml 读取，不硬编码。
"""
from __future__ import annotations

from pathlib import Path

import yaml

__all__ = ["load_governance_config"]

_CONFIG_PATH = Path(__file__).parent / "_config.yaml"


def load_governance_config() -> dict:
    """加载 governance 模块参数配置。"""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
