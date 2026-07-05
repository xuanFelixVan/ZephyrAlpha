# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_position_limit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types; zephyr.governance.rule_enforcement.risk_ssot
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
# [A_module] module_id=MOD-GOV_ct_position_limit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

PositionLimitHandler — PositionLimitHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class PositionLimitHandler(CheckTypeHandler):
    name = "position_limit"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations = []

        from zephyr.governance.rule_enforcement.risk_ssot import load_risk_params_ssot

        ssot = load_risk_params_ssot(project_root)

        nav = ssot.get("max_single_position_nav_ratio")

        d_default = params.get("max_single_position_default")

        if d_default is not None and nav is not None and float(d_default) > float(nav) + 1e-12:
            violations.append(
                {
                    "message": f"G10 SSoT conflict: max_single_position_default={d_default} > {nav}",
                    "severity": check.severity,
                }
            )

        sec_cap = ssot.get("max_sector_concentration_nav_ratio")

        s_default = params.get("max_sector_concentration_default")

        if s_default is not None and sec_cap is not None and float(s_default) > float(sec_cap) + 1e-12:
            violations.append(
                {
                    "message": f"G10 SSoT conflict: max_sector_concentration_default={s_default} > {sec_cap}",
                    "severity": check.severity,
                }
            )

        adv_cap = ssot.get("max_adv_participation_ratio")

        adv_p = params.get("max_adv_ratio")

        if adv_p is not None and adv_cap is not None and float(adv_p) > float(adv_cap) + 1e-12:
            violations.append(
                {"message": f"G10 SSoT conflict: max_adv_ratio={adv_p} > {adv_cap}", "severity": check.severity}
            )

        return violations
