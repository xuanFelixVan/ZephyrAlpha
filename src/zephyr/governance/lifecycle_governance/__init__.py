# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TESTS] none
# [TTL] permanent
# [A_module] module_id=MOD-GOV-lifecycle_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/lifecycle_governance/lifecycle_governance__init__.yaml
"""

__all__ = [
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
    "evaluate_rollback",
    "get_next_phase",
    "get_phase_def",
    "get_phase_spec",
    "get_plv_spec",
    "load_persisted_state",
    "migration_strategy",
    "paper_live_transition",
    "persist_state",
    "post_live_verification",
    "recover",
    "rollback_state_machine",
    "safe_read_state",
    "valid_transition",
    "transition",
]


# ---------------------------------------------------------------------------
# PEP 562 惰性外观（2026-08-18 AI-R4 治本，对齐母包 zephyr.governance.__init__
# AI-AUDIT13 先例）：__all__ 声明的符号映射到所属子模块，首次访问时按需
# import 再取符号。原 32 项中 29 项裸声明不可解析（无 import 机制），
# from zephyr.governance.lifecycle_governance import RollbackState 必 ImportError。
# 消费方现存全量子模块路径 import 不受影响（零 import 时成本）。
# ---------------------------------------------------------------------------
_SYMBOL_TO_SUBMODULE: dict[str, str] = {
    # migration_strategy
    "MigrationPhase": "migration_strategy",
    "PhaseDef": "migration_strategy",
    "get_phase_def": "migration_strategy",
    # paper_live_transition（get_next_phase 二义名归此——主 transition API；
    # migration_strategy.get_next_phase 经子模块全路径访问）
    "TransitionPhase": "paper_live_transition",
    "PhaseSpec": "paper_live_transition",
    "TransitionState": "paper_live_transition",
    "check_promotion_allowed": "paper_live_transition",
    "create_transition_state": "paper_live_transition",
    "get_next_phase": "paper_live_transition",
    "get_phase_spec": "paper_live_transition",
    "valid_transition": "paper_live_transition",
    # post_live_verification
    "PLVCheck": "post_live_verification",
    "PLVSpec": "post_live_verification",
    "get_plv_spec": "post_live_verification",
    # rollback_state_machine（MOD-GOV-045，DGR-001 落地）
    "RollbackState": "rollback_state_machine",
    "STATE_NAMESPACE": "rollback_state_machine",
    "evaluate_rollback": "rollback_state_machine",
    "load_persisted_state": "rollback_state_machine",
    "persist_state": "rollback_state_machine",
    "recover": "rollback_state_machine",
    "safe_read_state": "rollback_state_machine",
}


def __getattr__(name: str):
    """按 _SYMBOL_TO_SUBMODULE 惰性 import 子模块再取符号（PEP 562）。"""
    if name in _SYMBOL_TO_SUBMODULE:
        import importlib

        mod = importlib.import_module(f"{__name__}.{_SYMBOL_TO_SUBMODULE[name]}")
        return getattr(mod, name)
    # 子模块名本身（migration_strategy/paper_live_transition/
    # post_live_verification/rollback_state_machine/transition）按需 import
    if name in {
        "migration_strategy",
        "paper_live_transition",
        "post_live_verification",
        "rollback_state_machine",
        "transition",
    }:
        import importlib

        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
