# [A_module] module_id=MOD-GOV-agent_spec | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [TTL] permanent
"""
Agent Spec — MOD-INF-019

Agent 规范约束定义：参数类型、行为签名、契约检查。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final, AgentCapability, SpecRegistry
#   code: __init__.py import L36
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final, AgentCapability, SpecRegistry（共 3 符号）
#   desc: __init__ import L36；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: Final, AgentCapability, SpecRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

from zephyr.governance.agent_spec.registry import AgentCapability, SpecRegistry

__all__: Final = ["AgentCapability", "SpecRegistry", "registry", "a2a_failure", "rbac_bridge"]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-019"
