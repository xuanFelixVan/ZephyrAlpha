"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: disk_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① DiskGuard
#   name_en: DiskGuard
#   intro: class DiskGuard 源码 L55-L63
#   desc: 公共方法（定义序）: check, should_enter_readonly；源码 L55-L63
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DiskGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.fault_tolerance.disk_guard
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""磁盘空间耗尽防护（CT-DISK-GUARD）——剩余空间<5%->告警+只读模式。"""

DISK_THRESHOLD_PCT: Final[float] = 5.0


class DiskGuard:
    def check(self, free_gb: float, total_gb: float) -> tuple[bool, str]:
        pct = (free_gb / total_gb) * 100 if total_gb > 0 else 0
        if pct < DISK_THRESHOLD_PCT:
            return False, f"磁盘剩余 {pct:.1f}% < {DISK_THRESHOLD_PCT}%"
        return True, "OK"

    def should_enter_readonly(self, free_gb: float, total_gb: float) -> bool:
        return not self.check(free_gb, total_gb)[0]
