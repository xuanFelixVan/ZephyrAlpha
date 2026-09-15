# [BLUEPRINT] MOD-L02_ANA | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA
# [MODULE] zephyr.factor.analysis
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation
# [STARTUP] imported
# [MATURITY] production
# [A_module] module_id=MOD-L02_ANA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_FACTOR analysis 子包——因子分析与评估工具链。

提供 IC/IR 批量计算、IC 衰减分析、相关性分析、分层回测、多因子合成等工具。
所有策略参数从 _config.yaml 读取，不硬编码。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/analysis__init__.yaml
"""

from __future__ import annotations

from pathlib import Path

import yaml

# NOTE(P1W07-20260825): scaffold 注册器斜杠路径 bug（#ARCH-232 同型）已按可逆模式修复为点分路径
from zephyr.factor.analysis.bma_signal_weighter import BmaSignalWeighter

__all__ = ["load_analysis_config", "layered_backtest", "factor_optimization"]

_CONFIG_PATH = Path(__file__).parent / "_config.yaml"


def load_analysis_config() -> dict:
    """加载 analysis 模块策略参数配置。"""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


__all__.append("BmaSignalWeighter")
