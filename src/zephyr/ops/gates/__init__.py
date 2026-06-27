# [A_module] module_id=MOD-UNK_gates | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.ops.gates
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""feedback-loop.gates — auto-generated package init."""

import importlib

from zephyr.ops.gates._governance_gates import SUBMODULES as _governance_submodules
from zephyr.ops.gates._operational_gates import SUBMODULES as _operational_submodules
from zephyr.ops.gates._safety_gates import SUBMODULES as _safety_submodules
from zephyr.ops.gates._security_gates import SUBMODULES as _security_submodules

_SUBMODULES = sorted(set(_safety_submodules + _governance_submodules + _security_submodules + _operational_submodules))


def __getattr__(name):
    if name in _SUBMODULES:
        mod = importlib.import_module(f"zephyr.ops.gates.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "_governance_gates",
    "_operational_gates",
    "_safety_gates",
    "_security_gates",
    "action_reversibility",
    "adversarial_validation",
    "autonomy_credit",
    "autonomy_maturity",
    "blueprint_code_reconciler",
    "blueprint_validator",
    "checkpoint_manager",
    "ci_cd_pre_scanner",
    "concurrent_change_deconfliction",
    "config_complexity_budget",
    "config_governance",
    "conflict_arbitration",
    "cve_scanner",
    "data_quality_gate",
    "db_integrity",
    "deployment_suppression",
    "dynamic_llm_cost_router",
    "emergency_takeover",
    "federated_security",
    "flag_lifecycle_manager",
    "license_compliance",
    "llm_cost_router",
    "merkle_audit_root",
    "meta_performance_gate",
    "parameterized_safety_gate",
    "safety_gate_L1_L27",
    "safety_gate_L28_L29",
    "safety_gate_L36_L37",
    "safety_gate_L38_L39",
    "safety_gate_L40_L41",
    "safety_gate_L42_L43",
    "safety_gate_L44_L45",
    "safety_gate_L46_L47",
    "safety_gate_L48_L49",
    "safety_gate_L50_L51",
    "safety_gate_L52_L53",
    "safety_gate_L54_L55",
    "safety_gate_L56_L57",
    "safety_gate_L58_L59",
    "safety_gate_L60_L61",
    "safety_gate_L62_L63",
    "safety_gate_L64_L65",
    "safety_gate_L66_L67",
    "safety_gate_l1_l27",
    "safety_gate_l28_l29",
    "safety_gate_l36_l37",
    "safety_gate_l38_l39",
    "safety_gate_l40_l41",
    "safety_gate_l42_l43",
    "safety_gate_l44_l45",
    "safety_gate_l46_l47",
    "safety_gate_l48_l49",
    "safety_gate_l50_l51",
    "safety_gate_l52_l53",
    "safety_gate_l54_l55",
    "safety_gate_l56_l57",
    "safety_gate_l58_l59",
    "safety_gate_l60_l61",
    "safety_gate_l62_l63",
    "safety_gate_l64_l65",
    "safety_gate_l66_l67",
    "scope_creep_monitor",
]
