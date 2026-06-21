# [A_module] module_id=MOD-GOV_path_index | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.governance.audit_orchestration.path_index

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""文件路径索引（Path Index）——Module→__init__.py→蓝图→任务卡→配置的完整映射。"""

from __future__ import annotations

PATH_INDEX: dict[str, list[str]] = {}

class PathIndex:
    def lookup(self, module: str) -> list[str]:
        return PATH_INDEX.get(module, [])

    def register(self, module: str, paths: list[str]) -> None:
        PATH_INDEX[module] = paths
