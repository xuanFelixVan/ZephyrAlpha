# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.fault_tolerance.canary_manager
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
金丝雀发布管理器（CT-CANARY）——权重分流+指标对比+自动回滚。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: canary_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① CanaryManager
#   name_en: CanaryManager
#   intro: class CanaryManager 源码 L49-L71
#   desc: 公共方法（定义序）: canary_weight, set_weight, should_rollback, promote；源码 L49-L71
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CanaryManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class CanaryManager:
    def __init__(self):
        self._canary_weight: float = 0.1

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def canary_weight(self) -> float:
        """只读：canary_weight（Stage 4 公共化）。"""
        return self._canary_weight

    @canary_weight.setter
    def canary_weight(self, value):
        """写入：canary_weight（Stage 4 公共化）。"""
        self._canary_weight = value

    def set_weight(self, weight: float) -> None:
        self._canary_weight = min(1.0, max(0.0, weight))

    def should_rollback(self, error_rate: float, baseline: float) -> bool:
        return error_rate > baseline * 2.0

    def promote(self) -> None:
        self._canary_weight = 1.0
