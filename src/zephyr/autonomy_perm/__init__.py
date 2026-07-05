# [A_module] module_id=MOD-AUT_autonomy_perm | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Autonomy Permission domain — Re-export wrapper (DM-298)

All modules have been migrated to zephyr.governance.
This package re-exports for backward compatibility.
"""

from __future__ import annotations

__all__ = [
    "AttackRegistry",
    "BypassRecorder",
    "ConstitutionArticle",
    "ConstitutionGuard",
    "ConstitutionViolationError",
    "ConvergenceChecker",
    "ConvergenceFailureError",
    "DefenseRunner",
    "GameDayError",
    "GameDayFrequency",
    "GameDayRunner",
    "GateEvaluationError",
    "red_blue_validator",
]

_LAZY_IMPORTS = {
    "AttackRegistry": ("zephyr.security.adversarial_validation.attack_registry", "AttackRegistry"),
    "BypassRecorder": ("zephyr.security.adversarial_validation.bypass_recorder", "BypassRecorder"),
    "ConstitutionGuard": ("zephyr.security.adversarial_validation.constitution_guard", "ConstitutionGuard"),
    "ConstitutionViolationError": (
        "zephyr.security.adversarial_validation.constitution_guard",
        "ConstitutionViolationError",
    ),
    "ConstitutionArticle": ("zephyr.security.adversarial_validation.constitution_guard", "ConstitutionArticle"),
    "ConvergenceChecker": ("zephyr.security.adversarial_validation.convergence_checker", "ConvergenceChecker"),
    "ConvergenceFailureError": (
        "zephyr.security.adversarial_validation.convergence_checker",
        "ConvergenceFailureError",
    ),
    "DefenseRunner": ("zephyr.security.adversarial_validation.defense_runner", "DefenseRunner"),
    "GateEvaluationError": ("zephyr.security.adversarial_validation.defense_runner", "GateEvaluationError"),
    "GameDayRunner": ("zephyr.security.adversarial_validation.game_day_runner", "GameDayRunner"),
    "GameDayFrequency": ("zephyr.security.adversarial_validation.game_day_runner", "GameDayFrequency"),
    "GameDayError": ("zephyr.security.adversarial_validation.game_day_runner", "GameDayError"),
}

_SUBMODULES = ["red-blue-validator"]


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module("zephyr.security.adversarial_validation")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
