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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: analysis策略参数配置文件 _config.yaml
#   fields: layered_backtest/three_level_judgment/decay_monitor/factor_attribution/multifactor_synthesis/factor_optimization 六组参数
#   code: src/zephyr/factor/analysis/_config.yaml
# 层: 算法
# - id: A1
#   name_zh: ① 分析配置加载
#   name_en: load_analysis_config
#   intro: 读包内_config.yaml成字典，策略参数集中配置不硬编码
#   desc: open(_CONFIG_PATH) + yaml.safe_load，空文件返回 {}（L25-28）
#   inputs: I1
#   outputs: 配置字典 dict
# 层: 输出
# - id: O1
#   name_zh: 分析模块配置字典 dict
#   name_en: analysis config dict
#   intro: 供包内各分析模块读取阈值/频率/默认方法等策略参数
#   downstream: three_level_judgment MOD-L02-008；decay_monitor MOD-L02-009；factor_attribution MOD-L02-010；factor_optimization MOD-L02-012；layered_backtest（包内）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
