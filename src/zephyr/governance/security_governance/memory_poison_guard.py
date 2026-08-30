# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.memory_poison_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 记忆投毒检测不可禁用;存储前检测必须执行
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Memory Poison Guard — v0.9.0 记忆投毒防护: Memory写入内容审计+恶意注入检测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: memory_poison_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① MemoryPoisonGuard
#   name_en: MemoryPoisonGuard
#   intro: class MemoryPoisonGuard 源码 L51-L76
#   desc: 公共方法（定义序）: trusted_agents, register_trusted, validate_write；源码 L51-L76
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: MemoryPoisonGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class MemoryPoisonGuard:
    def __init__(self):
        self._trusted_agents: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def trusted_agents(self) -> set[str]:
        """只读：trusted_agents（Stage 4 公共化）。"""
        return self._trusted_agents

    @trusted_agents.setter
    def trusted_agents(self, value):
        """写入：trusted_agents（Stage 4 公共化）。"""
        self._trusted_agents = value

    def register_trusted(self, agent_id: str):
        self._trusted_agents.add(agent_id)

    def validate_write(self, agent_id: str, memory_content: str) -> tuple[bool, str]:
        if agent_id not in self._trusted_agents:
            return False, f"Agent {agent_id} not trusted for memory write"
        suspicious = ["ignore_previous", "forget_rules", "new_identity", "system_prompt:"]
        for s in suspicious:
            if s in memory_content.lower():
                return False, f"Suspicious content: {s}"
        return True, "OK"
