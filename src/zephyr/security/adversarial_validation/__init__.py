# [A_module] module_id=MOD-SEC-adversarial_validation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md
# [MODULE] zephyr.security.adversarial_validation
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
Red-Blue Adversarial Validator — 红白对抗攻击场景注册表。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: AIAttackGenerator, AttackGenerationError, AsyncMonitor, MonitorAlert,…
#   code: __init__.py import L43
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AIAttackGenerator, AttackGenerationError, AsyncMonitor, MonitorAlert, Monit…
#   desc: __init__ import L43；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（55 符号）
#   name_en: __all__
#   intro: AIAttackGenerator, AttackGenerationError, AsyncMonitor, MonitorAlert, MonitorSt…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.security.adversarial_validation.ai_attack_generator import AIAttackGenerator, AttackGenerationError
from zephyr.security.adversarial_validation.async_monitor import (
    AsyncMonitor,
    MonitorAlert,
    MonitorStallError,
    MonitorState,
)
from zephyr.security.adversarial_validation.blast_radius import AbortThresholdError, BlastRadius
from zephyr.security.adversarial_validation.bypass_recorder import BypassRecorder
from zephyr.security.adversarial_validation.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, CircuitState
from zephyr.security.adversarial_validation.cleanup import Cleanup, CleanupVerificationError
from zephyr.security.adversarial_validation.cli import main
from zephyr.security.adversarial_validation.cold_start import BootstrapPhase, BootstrapVerificationError, ColdStart
from zephyr.security.adversarial_validation.constitution_engine import ConstitutionEngine, RegistryWriteError
from zephyr.security.adversarial_validation.constitution_guard import (
    ConstitutionArticle,
    ConstitutionGuard,
    ConstitutionViolationError,
)
from zephyr.security.adversarial_validation.convergence_checker import ConvergenceChecker, ConvergenceFailureError
from zephyr.security.adversarial_validation.defense_runner import DefenseRunner
from zephyr.security.adversarial_validation.game_day_runner import GameDayError, GameDayFrequency, GameDayRunner
from zephyr.security.adversarial_validation.game_day_scheduler import GameDayScheduler, ScheduleConflictError
from zephyr.security.adversarial_validation.injection_engine import InjectionEngine
from zephyr.security.adversarial_validation.mcp_endpoints import McpEndpointError, MCPEndpoints, McpTool
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
from zephyr.security.adversarial_validation.steady_state import SteadyState, SteadyStateDriftError
from zephyr.security.adversarial_validation.validator import RedBlueValidator, SessionError

from . import attack_registry

__all__: list[str] = [
    "AIAttackGenerator",
    "AbortThresholdError",
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
    "MCPEndpoints",
    "McpEndpointError",
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
    "async_monitor",
    "attack_registry",
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
    "main",
    "mcp_endpoints",
    "models",
    "scenario_loader",
    "steady_state",
    "validator",
]

from typing import Final

__all__: Final = [
    "__main__",
    "ai_attack_generator",
    "async_monitor",
    "attack_registry",
    "blast_radius",
    "bypass_recorder",
    "circuit_breaker",
    "cleanup",
    "cli",
    "cold_start",
    "commit_trigger",
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
    "validator_event_bridge",
]
