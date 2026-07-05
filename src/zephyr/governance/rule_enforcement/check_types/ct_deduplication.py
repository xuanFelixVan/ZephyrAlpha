# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_deduplication
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_ct_deduplication | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class DeduplicationHandler(CheckTypeHandler):
    name = "deduplication"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        # 管线未接通（ARCH-027 §3b 合法保留理由）：
        #   zephyr.governance.scanner 模块不存在，code_dedup 引擎的 Scanner API
        #   （scan_files/find_duplicates）尚未实现。本 handler 为 task_types
        #   集成预留入口，待 Scanner API 落地后接通。
        # 生产侧去重通过 pre-commit → verify_dedup.py → cli.py verify 路径执行，
        # 不经过本 handler。此处显式返回"未接通"违规，不再静默吞错。
        check_id = getattr(check, "id", "DD-CHK-INCREMENTAL")
        return [
            dict(
                message=(
                    "Deduplication pipeline not connected: "
                    "zephyr.governance.scanner module not found. "
                    "Production dedup runs via pre-commit verify_dedup.py -> cli.py verify."
                ),
                severity="P2",
                check_id=check_id,
            )
        ]
