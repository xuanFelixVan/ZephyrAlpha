# [A_module] module_id=MOD-INF-auto_fix_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3

# [MODULE] zephyr.infrastructure.auto_fix_engine
# [INVARIANTS] All public symbols MUST be re-exported; __all__ MUST match actual exports
# [MODIFY-GUARD] blueprint.md §0; _fixer-registry.yaml; auto_fix_config.yaml
# [CONSUMERS] MOD-INF-027;MOD-INF-023;MOD-INF-029;MOD-INF-028;MOD-INF-022
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError on missing sub-module
# [TESTS] tests/auto-fix-engine/
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 修复器子模块符号
#   fields: 22 个子模块的修复器/引擎类（AlignmentSyncer…SelfHealAgent）+ models 的 14 个数据模型（FixReport/FixStatus/BlastRadius 等）
#   code: import 块 L14-51
# - id: I2
#   name: 引擎主类
#   fields: AutoFixEngine（可选导入，ImportError 时置 None）
#   code: engine L147-150
# 层: 算法
# - id: A1
#   name_zh: ① 公共符号聚合再导出
#   name_en: __init__ 再导出
#   intro: 把各自修复子模块的类集中到包命名空间统一出口
#   desc: 直接 import + __all__ 声明；注意 __all__ 含 FixBudget/FixReliability/FixSafety/Models/StateMachine/ZombieCleaner 等未实际导入的符号，与 [INVARIANTS]「__all__ MUST 匹配实际导出」存在偏差
#   inputs: I1 I2
#   outputs: 包公共 API 命名空间
#   invariant: 所有公共符号 MUST 再导出；__all__ MUST 匹配实际导出（[INVARIANTS] 头）
# 层: 输出
# - id: O1
#   name_zh: 自动修复引擎公共 API
#   name_en: __all__
#   intro: 修复执行/预算/安全/调度等能力的统一入口
#   downstream: 自动修复消费方 MOD-INF-027 / MOD-INF-023 / MOD-INF-029 / MOD-INF-028 / MOD-INF-022（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.auto_fix_engine.alignment_syncer import AlignmentSyncer
from zephyr.infrastructure.auto_fix_engine.all_completer import AllCompleter
from zephyr.infrastructure.auto_fix_engine.batch_fixer import BatchFixer
from zephyr.infrastructure.auto_fix_engine.compliance_auditor import ComplianceAuditor
from zephyr.infrastructure.auto_fix_engine.config_fixer import ConfigFixer
from zephyr.infrastructure.auto_fix_engine.dedup_extractor import DedupExtractor
from zephyr.infrastructure.auto_fix_engine.dep_version_fixer import DepVersionFixer
from zephyr.infrastructure.auto_fix_engine.drift_fixer import DriftFixer
from zephyr.infrastructure.auto_fix_engine.escalation_bridge import EscalationBridge
from zephyr.infrastructure.auto_fix_engine.event_hooks import EventHooks
from zephyr.infrastructure.auto_fix_engine.fix_diff import FixDiff
from zephyr.infrastructure.auto_fix_engine.fix_health_check import FixHealthCheck
from zephyr.infrastructure.auto_fix_engine.fix_pattern_miner import FixPatternMiner
from zephyr.infrastructure.auto_fix_engine.fix_scheduler import FixScheduler
from zephyr.infrastructure.auto_fix_engine.import_fixer import ImportFixer
from zephyr.infrastructure.auto_fix_engine.interrupt_guard import InterruptGuard
from zephyr.infrastructure.auto_fix_engine.llm_fix_adapter import LLMFixAdapter
from zephyr.infrastructure.auto_fix_engine.models import (
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
from zephyr.infrastructure.auto_fix_engine.scaffold_registrar import ScaffoldRegistrar
from zephyr.infrastructure.auto_fix_engine.self_heal_agent import SelfHealAgent
from zephyr.infrastructure.auto_fix_engine.shadow_workspace import ShadowWorkspace

from . import (
    alignment_syncer,
    all_completer,
    config_fixer,
    dedup_extractor,
    dep_version_fixer,
    drift_fixer,
    event_hooks,
    fix_scheduler,
    import_fixer,
    interrupt_guard,
    llm_fix_adapter,
    scaffold_registrar,
    self_heal_agent,
)

__version__ = "0.1.0"
__module_id__ = "MOD-INF-031"

__all__ = [
    "AlignmentSyncer",
    "AllCompleter",
    "AutoFixEngine",
    "BaseFixer",
    "BatchFixer",
    "BlastRadius",
    "BudgetDecision",
    "BudgetInfo",
    "ComplianceAuditor",
    "ComplianceEvidence",
    "ConfigFixer",
    "DedupExtractor",
    "DepVersionFixer",
    "DriftFixer",
    "EscalationBridge",
    "EventHooks",
    "FixAction",
    "FixBudget",
    "FixConfidence",
    "FixDeadLetter",
    "FixDiff",
    "FixHealthCheck",
    "FixHealthReport",
    "FixHistory",
    "FixLevel",
    "FixPatternMiner",
    "FixReliability",
    "FixReport",
    "FixSafety",
    "FixScheduler",
    "FixStatus",
    "ImportFixer",
    "InterruptGuard",
    "LLMFixAdapter",
    "Models",
    "SafetyDecision",
    "ScaffoldRegistrar",
    "SelfHealAgent",
    "ShadowResult",
    "ShadowWorkspace",
    "StateMachine",
    "ValidationResult",
    "ZombieCleaner",
    "__main__",
    "alignment_syncer",
    "all_completer",
    "batch_fixer",
    "compliance_auditor",
    "config_fixer",
    "dedup_extractor",
    "dep_version_fixer",
    "drift_fixer",
    "engine",
    "escalation_bridge",
    "event_hooks",
    "fix_budget",
    "fix_diff",
    "fix_health_check",
    "fix_pattern_miner",
    "fix_reliability",
    "fix_report",
    "fix_safety",
    "fix_scheduler",
    "import_fixer",
    "interrupt_guard",
    "llm_fix_adapter",
    "models",
    "scaffold_registrar",
    "self_heal_agent",
    "shadow_workspace",
    "state_machine",
    "zombie_cleaner",
]

try:
    from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine
except ImportError:
    AutoFixEngine = None  # type: ignore[assignment,misc]
