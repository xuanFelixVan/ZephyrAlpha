from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.path_index
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_path_index | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""文件路径索引（Path Index）——Module->__init__.py->蓝图->任务卡->配置的完整映射。"""

PATH_INDEX: Final[dict[str, list[str]]] = {}


class PathIndex:
    def lookup(self, module: str) -> list[str]:
        return PATH_INDEX.get(module, [])

    def register(self, module: str, paths: list[str]) -> None:
        PATH_INDEX[module] = paths