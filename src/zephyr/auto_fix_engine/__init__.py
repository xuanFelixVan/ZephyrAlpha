# [BLUEPRINT] MOD-INF-031 | 03_modules/_cross_layer/auto-fix-engine/blueprint.md | §3

from . import alignment_syncer
from . import all_completer
from . import config_fixer
from . import dedup_extractor
from . import dep_version_fixer
from . import drift_fixer
from . import event_hooks
from . import fix_scheduler
from . import import_fixer
from . import interrupt_guard
from . import llm_fix_adapter
from . import scaffold_registrar
from . import self_heal_agent
# [MODULE] zephyr.auto_fix_engine

# [INVARIANTS] All public symbols MUST be re-exported; __all__ MUST match actual exports

# [MODIFY-GUARD] blueprint.md §0; _fixer_registry.yaml; auto_fix_config.yaml

# [CONSUMERS] MOD-INF-027;MOD-INF-023;MOD-INF-029;MOD-INF-028;MOD-INF-022

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ImportError on missing sub-module

# [TESTS] tests/auto_fix_engine/

from zephyr.auto_fix_engine.alignment_syncer import AlignmentSyncer
from zephyr.auto_fix_engine.all_completer import AllCompleter
from zephyr.auto_fix_engine.dedup_extractor import DedupExtractor
from zephyr.auto_fix_engine.dep_version_fixer import DepVersionFixer
from zephyr.auto_fix_engine.drift_fixer import DriftFixer
from zephyr.auto_fix_engine.import_fixer import ImportFixer
from zephyr.auto_fix_engine.models import (
    BaseFixer,
    BlastRadius,
    BudgetDecision,
    BudgetInfo,
    ComplianceEvidence,
    FixAction,
    FixConfidence,
    FixDeadLetter,
    FixHealthReport,
    FixHistory,
    FixLevel,
    FixReport,
    FixStatus,
    SafetyDecision,
    ShadowResult,
    ValidationResult,
)
from zephyr.auto_fix_engine.scaffold_registrar import ScaffoldRegistrar
from zephyr.auto_fix_engine.batch_fixer import BatchFixer
from zephyr.auto_fix_engine.compliance_auditor import ComplianceAuditor
from zephyr.auto_fix_engine.config_fixer import ConfigFixer
from zephyr.auto_fix_engine.escalation_bridge import EscalationBridge
from zephyr.auto_fix_engine.event_hooks import EventHooks
from zephyr.auto_fix_engine.fix_diff import FixDiff
from zephyr.auto_fix_engine.fix_health_check import FixHealthCheck
from zephyr.auto_fix_engine.fix_pattern_miner import FixPatternMiner
from zephyr.auto_fix_engine.fix_scheduler import FixScheduler
from zephyr.auto_fix_engine.interrupt_guard import InterruptGuard
from zephyr.auto_fix_engine.llm_fix_adapter import LLMFixAdapter
from zephyr.auto_fix_engine.self_heal_agent import SelfHealAgent
from zephyr.auto_fix_engine.shadow_workspace import ShadowWorkspace
from .__main__ import cmd_fix, cmd_scan, cmd_health, cmd_report, main
from .zombie_cleaner import logger, ZombieCleaner

__version__ = "0.1.0"
__module_id__ = "MOD-INF-031"

__all__ = [
    "AlignmentSyncer",
    "AllCompleter",
    "AutoFixEngine",
    "BaseFixer",
    "BlastRadius",
    "BudgetDecision",
    "BudgetInfo",
    "ComplianceEvidence",
    "DedupExtractor",
    "DepVersionFixer",
    "DriftFixer",
    "FixAction",
    "FixBudget",
    "FixConfidence",
    "FixDeadLetter",
    "FixHealthReport",
    "FixHistory",
    "FixLevel",
    "FixReliability",
    "FixReport",
    "FixSafety",
    "FixStatus",
    "ImportFixer",
    "Models",
    "ScaffoldRegistrar",
    "SafetyDecision",
    "ShadowResult",
    "StateMachine",
    "ValidationResult",
    "ZombieCleaner",
    "BatchFixer",
    "ComplianceAuditor",
    "ConfigFixer",
    "EscalationBridge",
    "EventHooks",
    "FixDiff",
    "FixHealthCheck",
    "FixPatternMiner",
    "FixScheduler",
    "InterruptGuard",
    "LLMFixAdapter",
    "SelfHealAgent",
    "ShadowWorkspace",
    "engine",
    'alignment_syncer',
    'all_completer',
    'config_fixer',
    'dedup_extractor',
    'dep_version_fixer',
    'drift_fixer',
    'event_hooks',
    'fix_scheduler',
    'import_fixer',
    'interrupt_guard',
    'llm_fix_adapter',
    'scaffold_registrar',
    'self_heal_agent',
]

try:
    from zephyr.auto_fix_engine.engine import AutoFixEngine
except ImportError:
    AutoFixEngine = None  # type: ignore[assignment,misc]
