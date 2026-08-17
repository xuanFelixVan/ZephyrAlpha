# [DOMAIN] D_FEEDBACK_LOOP

# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md

# [MODULE] zephyr.feedback_loop.gates

# [INVARIANTS] pending_review

# [MODIFY-GUARD] no structural changes without owner approval

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [CONSUMERS]

# [ERROR_CONTRACT]

# [TESTS]

# [TTL] permanent

"""


feedback-loop.gates — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: _governance_gates 子模块符号 1个
#   fields: SUBMODULES
#   code: zephyr.feedback_loop.gates._governance_gates
# - id: I2
#   name: _operational_gates 子模块符号 1个
#   fields: SUBMODULES
#   code: zephyr.feedback_loop.gates._operational_gates
# - id: I3
#   name: _safety_gates 子模块符号 1个
#   fields: SUBMODULES
#   code: zephyr.feedback_loop.gates._safety_gates
# - id: I4
#   name: _security_gates 子模块符号 1个
#   fields: SUBMODULES
#   code: zephyr.feedback_loop.gates._security_gates
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.feedback_loop.gates.__init__
#   intro: feedback-loop.gates — auto-generated package init.
#   desc: MOD-GATE_ENGINE 包入口，包级聚合再导出并声明 __all__（48项）
#   inputs: I1 I2 I3 I4
#   outputs: zephyr.feedback_loop.gates 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（48项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.feedback_loop.gates 包公共 API
#   name_en: __all__ 48项
#   intro: feedback-loop.gates — auto-generated package init.——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

import importlib

from zephyr.feedback_loop.gates._governance_gates import SUBMODULES as _governance_submodules
from zephyr.feedback_loop.gates._operational_gates import SUBMODULES as _operational_submodules
from zephyr.feedback_loop.gates._safety_gates import SUBMODULES as _safety_submodules
from zephyr.feedback_loop.gates._security_gates import SUBMODULES as _security_submodules

_SUBMODULES = sorted(set(_safety_submodules + _governance_submodules + _security_submodules + _operational_submodules))


def __getattr__(name):

    if name in _SUBMODULES:
        mod = importlib.import_module(f"zephyr.feedback_loop.gates.{name}")

        globals()[name] = mod

        return mod

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [  # noqa: n114-final  n114-final豁免: __all__是Python导出约定且本文件运行时动态append，Final标注不适用
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
