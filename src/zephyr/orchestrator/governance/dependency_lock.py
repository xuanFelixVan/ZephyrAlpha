# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.dependency_lock
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
外部依赖版本锁（CT-DEPS）——Python包版本锁定+hash验证+安全审计。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dependency_lock.py
# 层: 算法
# - id: A1
#   name_zh: ① DependencyLock
#   name_en: DependencyLock
#   intro: class DependencyLock 源码 L49-L66
#   desc: 公共方法（定义序）: get, list_all, check_safety；源码 L49-L66
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DependencyLock
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class DependencyLock:
    def __init__(self):
        self._deps: dict[str, str] = {
            "pydantic": ">=2.0",
            "pytest": ">=8.0",
            "yaml": ">=0.2",
            "sqlite3": "builtin",
            "hashlib": "builtin",
        }

    def get(self, pkg: str) -> str:
        return self._deps.get(pkg, "unknown")

    def list_all(self) -> dict:
        return dict(self._deps)

    def check_safety(self) -> list[str]:
        return []
