# [A_module] module_id=MOD-AUT_red_blue_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: red-blue-validator has migrated to zephyr.security.adversarial_validation"""

from zephyr.security.adversarial_validation.attack_registry import AttackRegistry
from zephyr.security.adversarial_validation.bypass_recorder import BypassRecorder
from zephyr.security.adversarial_validation.constitution_guard import (
    ConstitutionArticle,
    ConstitutionGuard,
    ConstitutionViolationError,
)
from zephyr.security.adversarial_validation.convergence_checker import (
    ConvergenceChecker,
    ConvergenceFailureError,
)
from zephyr.security.adversarial_validation.defense_runner import DefenseRunner, GateEvaluationError
from zephyr.security.adversarial_validation.game_day_runner import (
    GameDayError,
    GameDayFrequency,
    GameDayRunner,
)

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
]
