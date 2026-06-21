# [A_module] module_id=MOD-SEC_auto_fix_engine_03 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto-fix-engine/blueprint.md | §3

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
# [MODULE] zephyr.security.access_control.auto_fix_engine_03

# [INVARIANTS] All public symbols MUST be re-exported; __all__ MUST match actual exports

# [MODIFY-GUARD] blueprint.md §0; _fixer-registry.yaml; auto-fix-config.yaml

# [CONSUMERS] MOD-INF-027;MOD-INF-023;MOD-INF-029;MOD-INF-028;MOD-INF-022

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ImportError on missing sub-module

# [TESTS] tests/auto-fix-engine/

from zephyr.security.access_control.auto_fix_engine_03.alignment_syncer import AlignmentSyncer
from zephyr.security.access_control.auto_fix_engine_03.all_completer import AllCompleter
from zephyr.security.access_control.auto_fix_engine_03.dedup_extractor import DedupExtractor
from zephyr.security.access_control.auto_fix_engine_03.dep_version_fixer import DepVersionFixer
from zephyr.security.access_control.auto_fix_engine_03.drift_fixer import DriftFixer
from zephyr.security.access_control.auto_fix_engine_03.import_fixer import ImportFixer
from zephyr.security.access_control.auto_fix_engine_03.models import (
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
from zephyr.security.access_control.auto_fix_engine_03.scaffold_registrar import ScaffoldRegistrar
from zephyr.security.access_control.auto_fix_engine_03.batch_fixer import BatchFixer
from zephyr.security.access_control.auto_fix_engine_03.compliance_auditor import ComplianceAuditor
from zephyr.security.access_control.auto_fix_engine_03.config_fixer import ConfigFixer
from zephyr.security.access_control.auto_fix_engine_03.escalation_bridge import EscalationBridge
from zephyr.security.access_control.auto_fix_engine_03.event_hooks import EventHooks
from zephyr.security.access_control.auto_fix_engine_03.fix_diff import FixDiff
from zephyr.security.access_control.auto_fix_engine_03.fix_health_check import FixHealthCheck
from zephyr.security.access_control.auto_fix_engine_03.fix_pattern_miner import FixPatternMiner
from zephyr.security.access_control.auto_fix_engine_03.fix_scheduler import FixScheduler
from zephyr.security.access_control.auto_fix_engine_03.interrupt_guard import InterruptGuard
from zephyr.security.access_control.auto_fix_engine_03.llm_fix_adapter import LLMFixAdapter
from zephyr.security.access_control.auto_fix_engine_03.self_heal_agent import SelfHealAgent
from zephyr.security.access_control.auto_fix_engine_03.shadow_workspace import ShadowWorkspace

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
    "__main__",
    "fix_reliability",
    "fix_report",
    "fix_safety",
    "state_machine",
    "batch_fixer",
    "compliance_auditor",
    "escalation_bridge",
    "fix_budget",
    "fix_diff",
    "fix_health_check",
    "fix_pattern_miner",
    "models",
    "shadow_workspace",
    "zombie_cleaner",
]

try:
    from zephyr.security.access_control.auto_fix_engine_03.engine import AutoFixEngine
except ImportError:
    AutoFixEngine = None  # type: ignore[assignment,misc]
