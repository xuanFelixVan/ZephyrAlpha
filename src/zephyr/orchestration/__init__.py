# [A_module] module_id=MOD-ORC_proxy | layer=package | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.orchestration
# [INVARIANTS] 代理包——所有子模块重定向到物理位置；不持有业务逻辑
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] 24个文件通过 import_module("zephyr.orchestration.*") 访问
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if proxy target missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.orchestration — 代理包

历史背景：D-ORCHESTRATION 域被裁定为"AI生成器膨胀产物"（architecture_upgrade_discussion.md D78），
其子模块物理分散到 autonomy_core/、trading/、integration/ 三个包。
但 24 个文件仍通过 import_module("zephyr.orchestration.*") 访问这些子模块。
本代理包提供导入兼容，将所有访问重定向到正确的物理位置。

创建依据：OPS-2026062101（zephyr.orchestration 断裂点修复）
先例：data/persistence/circuit_breaker_types.py（单文件代理）
"""

# 子模块物理映射表（供诊断用）
_PROXY_MAP = {
    "context_management": "zephyr.autonomy_core",
    "agent_lifecycle": "zephyr.ops.actors.agent_lifecycle",
    "agent_communication": "zephyr.autonomy_core.agent_communication",
    "runtime_core": "zephyr.trading",
    "pipeline_routing": "zephyr.integration",
}

__all__ = ["context_management", "agent_lifecycle", "agent_communication", "runtime_core", "pipeline_routing"]
