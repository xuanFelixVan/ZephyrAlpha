# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-lifecycle_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.lifecycle_governance
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明（PEP 562 懒导出）
#   name_en: zephyr.governance.lifecycle_governance.__init__
#   intro: __unmanaged__src/zephyr/governance/lifecycle_governance/__init__.py 包入口
#   desc: __all__ 33 项（26 属性+7 子模块名）经 PEP 562 __getattr__ 按名懒解析到真源子模块（S4-C import 零副作用；2026-08-18 AI-R5 治本——原 33 项死声明无 import 无 __getattr__，from import * 必炸）
#   inputs: I1
#   outputs: zephyr.governance.lifecycle_governance 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（33 项）；__getattr__ 未知名必抛 AttributeError
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.lifecycle_governance 包公共 API
#   name_en: __all__ 33 项 (lazy)
#   intro: __unmanaged__src/zephyr/governance/lifecycle_governance/__init__.py 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import importlib
from typing import Final

__all__: Final = [
    # ── 属性（经 _LAZY_ATTR_MODULES 映射到真源子模块）──
    "APIEndpoint",
    "APIState",
    "DeprecationNotice",
    "MigrationPhase",
    "PLVCheck",
    "PLVSpec",
    "PhaseDef",
    "PhaseSpec",
    "RollbackState",
    "STATE_NAMESPACE",
    "TransitionPhase",
    "TransitionState",
    "check_promotion_allowed",
    "create_transition_state",
    "deprecate_api",
    "evaluate_rollback",
    "get_next_phase",
    "get_phase_def",
    "get_phase_spec",
    "get_plv_spec",
    "load_persisted_state",
    "persist_state",
    "recover",
    "remove_api",
    "safe_read_state",
    "valid_transition",
    # ── 子模块名（import 机制属性）──
    "api_lifecycle",
    "migration_strategy",
    "paper_live_transition",
    "post_live_verification",
    "rollback_state_machine",
    "strategy_retirement_evaluator",
    "transition",
]

# PEP 562 懒导出映射：__all__ 属性名 → 真源子模块（2026-08-18 AI-R5 治本：
# 原死声明 __all__ 33 项无 import/无 __getattr__，from import * 必抛 AttributeError，
# 且含 get_next_phase 重复条目与 'transition' 孤儿串；本表为唯一映射真源）。
#
# get_next_phase 双真源裁定：migration_strategy（API 迁移阶段 MigrationPhase）与
# paper_live_transition（交易迁移阶段 TransitionPhase）同名异义，包级名映射后者
# （53 号 memo §3.6 语境），前者经全名 migration_strategy.get_next_phase 访问。
_LAZY_ATTR_MODULES: Final[dict[str, str]] = {
    # api_lifecycle 真源
    "APIEndpoint": "api_lifecycle",
    "APIState": "api_lifecycle",
    "DeprecationNotice": "api_lifecycle",
    "deprecate_api": "api_lifecycle",
    "remove_api": "api_lifecycle",
    # migration_strategy 真源
    "MigrationPhase": "migration_strategy",
    "PhaseDef": "migration_strategy",
    "get_phase_def": "migration_strategy",
    # paper_live_transition 真源
    "PhaseSpec": "paper_live_transition",
    "TransitionPhase": "paper_live_transition",
    "TransitionState": "paper_live_transition",
    "check_promotion_allowed": "paper_live_transition",
    "create_transition_state": "paper_live_transition",
    "get_next_phase": "paper_live_transition",
    "get_phase_spec": "paper_live_transition",
    "valid_transition": "paper_live_transition",
    # post_live_verification 真源
    "PLVCheck": "post_live_verification",
    "PLVSpec": "post_live_verification",
    "get_plv_spec": "post_live_verification",
    # rollback_state_machine 真源（RollbackState 真源=本模块，paper_live_transition 转售不计）
    "STATE_NAMESPACE": "rollback_state_machine",
    "RollbackState": "rollback_state_machine",
    "evaluate_rollback": "rollback_state_machine",
    "load_persisted_state": "rollback_state_machine",
    "persist_state": "rollback_state_machine",
    "recover": "rollback_state_machine",
    "safe_read_state": "rollback_state_machine",
}

_SUBMODULE_NAMES: Final[frozenset[str]] = frozenset({
    "api_lifecycle",
    "migration_strategy",
    "paper_live_transition",
    "post_live_verification",
    "rollback_state_machine",
    "strategy_retirement_evaluator",
    "transition",
})


def __getattr__(name: str):
    """PEP 562 包级懒导出：属性名查映射表解析到真源子模块，子模块名按需 import。"""
    mod_name = _LAZY_ATTR_MODULES.get(name)
    if mod_name is not None:
        return getattr(importlib.import_module(f"{__name__}.{mod_name}"), name)
    if name in _SUBMODULE_NAMES:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
