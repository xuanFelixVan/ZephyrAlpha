# [BLUEPRINT] MOD-L02_GOV | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV
# [MODULE] zephyr.factor.governance
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.lifecycle.state_machine; zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [STARTUP] imported
# [MATURITY] production
# [A_module] module_id=MOD-L02_GOV | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_FACTOR governance 子包——因子生命周期治理工具链。

提供因子生命周期状态机、ABS001 上线门禁、灰度发布、六步流程编排、治理引擎。
所有治理参数从 _config.yaml 读取，不硬编码。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 治理参数配置文件 YAML
#   fields: abs001_gate / grayscale_rollout / lifecycle_state_machine / factor_pool 四段治理参数
#   code: governance/_config.yaml（__init__.py L22 _CONFIG_PATH）
# 层: 算法
# - id: A1
#   name_zh: ① 治理配置加载
#   name_en: load_governance_config
#   intro: 打开 governance/_config.yaml 用 yaml.safe_load 读成字典，空文件返回空dict
#   desc: open(_CONFIG_PATH, encoding=utf-8) → yaml.safe_load(f) or {}（__init__.py L25-28）
#   inputs: I1
#   outputs: 治理配置 dict
#   invariant: 所有治理参数从_config.yaml读取，不硬编码
# 层: 输出
# - id: O1
#   name_zh: 治理配置字典 dict
#   name_en: governance config dict
#   intro: 治理子包共享的参数真源，门禁阈值/灰度阶梯/池容量都从这里取
#   downstream: abs001_gate MOD-L02-014；grayscale_rollout MOD-L02-015；lifecycle_state_machine MOD-L02-013；factor_pool_manager MOD-L02-018
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
