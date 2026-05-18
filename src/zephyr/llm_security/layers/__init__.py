# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §
"""LSG 九层防御层实现包（L0-L8）。

每层对应 blueprint.md §3 一条防御策略，均实现 LLMSecurityProtocol。

L0 — 供应链安全：模型验证 / 依赖扫描 / MCP验证 / Prompt模板审计
L1 — 输入防护层：直接注入 + 间接注入 + 越狱检测 + 编码逃逸防御
L2 — Prompt保护层：四段式模板 / 防泄露 / 话题边界控制
L3 — 输出安全层：Schema验证 / 代码沙箱 / PII脱敏 / 幻觉检测
L4 — Agent安全层：权限最小化 / HITL审批 / 工具参数注入防护
L5 — 资源保护层：Token预算 / 速率限制 / 成本熔断
L6 — 可观测性层：安全日志 / 异常告警 / 仪表板
L7 — 持续验证层：自动Red Team / 安全回归 / 防御度量
L8 — 多Agent安全层：跨Agent权限继承 / 信任链验证
"""

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "l0_supply_chain": ("SupplyChainGuard",),
    "l1_input": ("InputDefenseLayer",),
    "l2_prompt_protection": ("PromptProtectionLayer",),
    "l2a_process_sandbox": ("ProcessSandboxLayer",),
    "l3_output": ("OutputSecurityLayer",),
    "l4_agent": ("AgentSecurityLayer",),
    "l5_resource_protection": ("ResourceProtectionLayer",),
    "l6_observability": ("ObservabilityLayer",),
    "l8_multi_agent": ("MultiAgentSecurityLayer",),
}

__all__ = [
    'l0_supply_chain', 'l1_input', 'l2_prompt_protection', 'l2a_process_sandbox',
    'l3_output', 'l4_agent', 'l5_resource_protection', 'l6_observability', 'l8_multi_agent',
    'SupplyChainGuard', 'InputDefenseLayer', 'PromptProtectionLayer', 'ProcessSandboxLayer',
    'OutputSecurityLayer', 'AgentSecurityLayer', 'ResourceProtectionLayer',
    'ObservabilityLayer', 'MultiAgentSecurityLayer',
]


def __getattr__(name: str):
    for mod_name, symbols in _LAZY_MODULES.items():
        if name in symbols or name == mod_name:
            mod = __import__(f"zephyr.llm_security.layers.{mod_name}", fromlist=[name])
            try:
                return getattr(mod, name)
            except AttributeError:
                pass
    raise AttributeError(f"module 'zephyr.llm_security.layers' has no attribute '{name}'")
