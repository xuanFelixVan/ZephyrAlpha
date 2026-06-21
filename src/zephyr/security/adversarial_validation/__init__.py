# [A_module] module_id=MOD-SEC_adversarial_validation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red-blue-validator/blueprint.md
# [MODULE] zephyr.security.adversarial_validation
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""
Red-Blue Adversarial Validator — 红白对抗攻击场景注册表。
"""

from zephyr.security.adversarial_validation.models import (
    AttackScenario,
    AttackTier,
    BlastRadiusLevel,
    BypassEntry,
    ConvergenceResult,
    DefenseResult,
    GameDayResult,
    InjectionResult,
    InjectionType,
    RedBlueReport,
    ResultClass,
    ScenarioResult,
    ScenarioSource,
    Severity,
)
from zephyr.security.adversarial_validation.scenario_loader import ScenarioLoader
from zephyr.security.adversarial_validation.injection_engine import InjectionEngine
from zephyr.security.adversarial_validation.defense_runner import DefenseRunner
from zephyr.security.adversarial_validation.bypass_recorder import BypassRecorder
from zephyr.security.adversarial_validation.steady_state import SteadyState, SteadyStateDriftError
from zephyr.security.adversarial_validation.cleanup import Cleanup, CleanupVerificationError
from zephyr.security.adversarial_validation.blast_radius import BlastRadius, AbortThresholdError
from zephyr.security.adversarial_validation.validator import RedBlueValidator, SessionError
from zephyr.security.adversarial_validation.constitution_guard import ConstitutionGuard, ConstitutionArticle, ConstitutionViolationError
from zephyr.security.adversarial_validation.constitution_engine import ConstitutionEngine, RegistryWriteError
from zephyr.security.adversarial_validation.convergence_checker import ConvergenceChecker, ConvergenceFailureError
from zephyr.security.adversarial_validation.game_day_runner import GameDayRunner, GameDayFrequency, GameDayError
from zephyr.security.adversarial_validation.game_day_scheduler import GameDayScheduler, ScheduleConflictError
from zephyr.security.adversarial_validation.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenError
from zephyr.security.adversarial_validation.cold_start import ColdStart, BootstrapPhase, BootstrapVerificationError
from zephyr.security.adversarial_validation.cli import main
from zephyr.security.adversarial_validation.mcp_endpoints import MCPEndpoints, McpEndpointError, McpTool
from zephyr.security.adversarial_validation.ai_attack_generator import AIAttackGenerator, AttackGenerationError
from zephyr.security.adversarial_validation.async_monitor import AsyncMonitor, MonitorState, MonitorAlert, MonitorStallError

from . import attack_registry

__all__: list[str] = [
    "AbortThresholdError",
    "AIAttackGenerator",
    "AsyncMonitor",
    "AttackGenerationError",
    "AttackScenario",
    "AttackTier",
    "BlastRadius",
    "BlastRadiusLevel",
    "BootstrapPhase",
    "BootstrapVerificationError",
    "BypassEntry",
    "BypassRecorder",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
    "Cleanup",
    "CleanupVerificationError",
    "ColdStart",
    "ConstitutionArticle",
    "ConstitutionEngine",
    "ConstitutionGuard",
    "ConstitutionViolationError",
    "ConvergenceChecker",
    "ConvergenceFailureError",
    "ConvergenceResult",
    "DefenseResult",
    "DefenseRunner",
    "GameDayError",
    "GameDayFrequency",
    "GameDayResult",
    "GameDayRunner",
    "GameDayScheduler",
    "InjectionEngine",
    "InjectionResult",
    "InjectionType",
    "main",
    "McpEndpointError",
    "MCPEndpoints",
    "McpTool",
    "MonitorAlert",
    "MonitorStallError",
    "MonitorState",
    "RedBlueReport",
    "RedBlueValidator",
    "RegistryWriteError",
    "ResultClass",
    "ScenarioLoader",
    "ScenarioResult",
    "ScenarioSource",
    "ScheduleConflictError",
    "SessionError",
    "Severity",
    "SteadyState",
    "SteadyStateDriftError",
    "__main__",
    "ai_attack_generator",
    "attack_registry",
    "async_monitor",
    "blast_radius",
    "bypass_recorder",
    "circuit_breaker",
    "cleanup",
    "cli",
    "cold_start",
    "constitution_engine",
    "constitution_guard",
    "convergence_checker",
    "defense_runner",
    "game_day_runner",
    "game_day_scheduler",
    "injection_engine",
    "mcp_endpoints",
    "models",
    "scenario_loader",
    "steady_state",
    "validator",
]
