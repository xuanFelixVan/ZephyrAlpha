"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: path_index.py
# 层: 算法
# - id: A1
#   name_zh: ① PathIndex
#   name_en: PathIndex
#   intro: class PathIndex 源码 L55-L60
#   desc: 公共方法（定义序）: lookup, register；源码 L55-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PathIndex
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.path_index
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

"""文件路径索引（Path Index）——Module->__init__.py->蓝图->任务卡->配置的完整映射。"""

PATH_INDEX: Final[dict[str, list[str]]] = {}


class PathIndex:
    def lookup(self, module: str) -> list[str]:
        return PATH_INDEX.get(module, [])

    def register(self, module: str, paths: list[str]) -> None:
        PATH_INDEX[module] = paths
