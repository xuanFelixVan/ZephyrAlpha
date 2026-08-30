# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.rolling_upgrade
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
零停机滚动升级（CT-DEPLOY）——graceful shutdown+流量摘除+health check wait。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: rolling_upgrade.py
# 层: 算法
# - id: A1
#   name_zh: ① RollingUpgradeManager
#   name_en: RollingUpgradeManager
#   intro: class RollingUpgradeManager 源码 L49-L60
#   desc: 公共方法（定义序）: start_upgrade, is_draining, complete_upgrade；源码 L49-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RollingUpgradeManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class RollingUpgradeManager:
    def __init__(self):
        self._upgrading = False

    def start_upgrade(self) -> None:
        self._upgrading = True

    def is_draining(self) -> bool:
        return self._upgrading

    def complete_upgrade(self) -> None:
        self._upgrading = False
