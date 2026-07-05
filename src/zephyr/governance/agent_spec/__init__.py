# [A_module] module_id=MOD-GOV_agent_spec | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [TTL] permanent
"""
Agent Spec — MOD-INF-019

Agent 规范约束定义：参数类型、行为签名、契约检查。
"""

from zephyr.governance.agent_spec.registry import AgentCapability, SpecRegistry

__all__ = ["AgentCapability", "SpecRegistry", "registry", 'a2a_failure', 'rbac_bridge']

__version__ = "0.1.0"
__module_id__ = "MOD-INF-019"
