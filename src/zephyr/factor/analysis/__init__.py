# [BLUEPRINT] MOD-L02-ANA | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA
# [MODULE] zephyr.factor.analysis
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation
# [STARTUP] imported
# [MATURITY] production
# [TTL] permanent
"""D_FACTOR analysis 子包——因子分析与评估工具链。

提供 IC/IR 批量计算、IC 衰减分析、相关性分析、分层回测、多因子合成等工具。
所有策略参数从 _config.yaml 读取，不硬编码。
"""
from __future__ import annotations

from pathlib import Path

import yaml

__all__ = ["load_analysis_config"]

_CONFIG_PATH = Path(__file__).parent / "_config.yaml"


def load_analysis_config() -> dict:
    """加载 analysis 模块策略参数配置。"""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
