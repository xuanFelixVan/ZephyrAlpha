# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_strategy_correlation
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
# [A_module] module_id=MOD-GOV_ct_strategy_correlation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

StrategyCorrelationHandler — StrategyCorrelationHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class StrategyCorrelationHandler(CheckTypeHandler):
    name = "strategy_correlation"

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

        ct_thr = params.get("correlation_threshold")

        ss_thr = ssot.get("max_strategy_correlation_threshold")

        if ct_thr is not None and ss_thr is not None and float(ct_thr) > float(ss_thr) + 1e-12:
            violations.append(
                {"message": f"G12 correlation threshold too loose: {ct_thr} > {ss_thr}", "severity": check.severity}
            )

        mo = params.get("max_factor_overlap")

        ss_mo = ssot.get("max_factor_overlap_threshold")

        if mo is not None and ss_mo is not None and float(mo) > float(ss_mo) + 1e-12:
            violations.append({"message": f"G12 factor overlap too loose: {mo} > {ss_mo}", "severity": check.severity})

        uo = params.get("max_universe_overlap")

        ss_uo = ssot.get("max_universe_overlap_threshold")

        if uo is not None and ss_uo is not None and float(uo) > float(ss_uo) + 1e-12:
            violations.append(
                {"message": f"G12 universe overlap too loose: {uo} > {ss_uo}", "severity": check.severity}
            )

        return violations
