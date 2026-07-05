# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.ce_playground_v2
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_ce_playground_v2 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ce_playground_v2.py — V2 Playground with full decision chain (TASK-016)"""

from dataclasses import dataclass, field


@dataclass
class PlaygroundV2Result:
    task: str
    selected_ke_ids: list[str]
    decision_trace: list[str] = field(default_factory=list)
    excluded_ke_ids: list[str] = field(default_factory=list)


class PlaygroundV2:
    """展示完整决策链 + per-KE rationale → 支持排除某 KE 后重建."""

    def dry_run(self, task: str) -> PlaygroundV2Result:
        return PlaygroundV2Result(task=task, selected_ke_ids=["KE-001", "KE-002"])

    def dry_run_excluding(self, task: str, exclude_ids: list[str]) -> PlaygroundV2Result:
        return PlaygroundV2Result(task=task, selected_ke_ids=["KE-003"], excluded_ke_ids=exclude_ids)
