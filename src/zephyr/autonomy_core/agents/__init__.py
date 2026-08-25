# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.0/§4-Phase0
# [MODULE] zephyr.autonomy_core.agents
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 包级零 eager 子模块加载；四类入口均为手动触发薄入口（14号文 §3.0 role façade），非常驻进程/无消息总线/无调度器（61号文 §4.1 裁定边界）
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 Phase 0 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无（纯包入口，无导入副作用）
# [TESTS] tests/autonomy/test_execution_layer_agent_entries.py
# [A_module] module_id=MOD-EXE-AGENTS | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AI 执行层四类 Agent 薄入口包（14号文 §3.0 role façade，§4 Phase 0 手动形态）.

四类角色入口（治理/业务/算法/自我迭代）只做"职责边界声明 + 能力包组装 +
工单/产出落盘"，内部零新业务逻辑；物理上不新建进程、不建消息总线、
不建调度器。产出 100% 落盘（.runtime/agent_runs/）且标 human_gated。
"""

from __future__ import annotations

__all__ = [
    "algorithm_agent_entry",
    "business_agent_entry",
    "governance_agent_entry",
    "risk_manager_agent",
    "self_iteration_agent_entry",
]
