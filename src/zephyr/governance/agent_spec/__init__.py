# [A_module] module_id=MOD-GOV_agent_spec | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md | §
"""
Agent Spec — MOD-INF-019

Agent 规范约束定义：参数类型、行为签名、契约检查。
"""

from zephyr.governance.agent_spec.registry import AgentCapability, SpecRegistry

__all__ = ["AgentCapability", "SpecRegistry", "registry"]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-019"
