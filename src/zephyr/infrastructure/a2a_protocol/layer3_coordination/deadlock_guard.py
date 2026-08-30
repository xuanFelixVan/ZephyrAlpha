# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.deadlock_guard
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
P2: 死锁守卫

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: deadlock_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① DeadlockGuard
#   name_en: DeadlockGuard
#   intro: class DeadlockGuard 源码 L49-L74
#   desc: 公共方法（定义序）: locks, try_acquire, release；源码 L49-L74
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DeadlockGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class DeadlockGuard:
    def __init__(self):
        self._locks: dict = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def locks(self) -> dict:
        """只读：locks（Stage 4 公共化）。"""
        return self._locks

    @locks.setter
    def locks(self, value):
        """写入：locks（Stage 4 公共化）。"""
        self._locks = value

    def try_acquire(self, resource: str, holder: str) -> bool:
        if resource in self._locks:
            return False
        self._locks[resource] = holder
        return True

    def release(self, resource: str, holder: str) -> bool:
        if self._locks.get(resource) == holder:
            del self._locks[resource]
            return True
        return False
