# [A_module] module_id=MOD-GOV_drift_detection | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md | §
from . import absence_manager
from . import ai_context_injector
from . import alert_router
from . import backcompat_checker
from . import baseline_manager
from . import baseline_poisoning_guard
from . import brain_integration
from . import canary_controller
from . import config_consistency
from . import cross_module_score
from . import dashboard
from . import detector_dispatcher
from . import drift_cron_scheduler
from . import drift_result_types
from . import drift_training
from . import file_attr_checker
from . import gate_persistence
from . import git_bisector
from . import gitignore_auditor
from . import handoff_manager
from . import headless_scanner
from . import incremental_scanner
from . import integration_test_runner
from . import naming_magic_checker
from . import python_compat
from . import resource_guard
from . import roi_engine
from . import runbook_generator
from . import scan_mutex
from . import suppression_learner
from . import symlink_checker
from . import tamper_proof_audit
from . import test_fixture_checker
from . import trend_analyzer
"""
ZephyrAlpha 漂移运行时检测系统 — Drift Detector

B 轨平台能力（cross_layer），module_id=MOD-INF-023。
蓝图真源路径: docs/docs/03_modules/_domain-governance/drift-detector/blueprint.md

基于 git diff + YAML 对比的运行时漂移检测引擎。
整合治理脚本为运行时检测 + 自动对账（可自动修复的漂移自动修，不可自动修复的生成修复建议）。
包含基线快照、漂移状态机、时序趋势分析、AI 施工场景专项检测器等能力。

对标: Terraform drift detection + K8s reconciliation loop + OPA decision trace + Datadog anomaly detection
"""

__all__ = [
    'absence_manager',
    'ai_construction_detectors',
    'ai_context_injector',
    'alert_router',
    'backcompat_checker',
    'baseline_manager',
    'baseline_poisoning_guard',
    'brain_integration',
    'canary_controller',
    'cascade_detector',
    'chaos_injector',
    'cold_start',
    'config_consistency',
    'correlation_engine',
    'credibility_engine',
    'cross_module_score',
    'dashboard',
    'detector_dispatcher',
    'drift_cron_scheduler',
    'drift_engine',
    'drift_hotfix_bypass',
    'drift_infrastructure',
    'drift_models',
    'drift_result_types',
    'drift_training',
    'file_attr_checker',
    'forensics_engine',
    'gate_persistence',
    'git_bisector',
    'gitignore_auditor',
    'handoff_manager',
    'headless_scanner',
    'incremental_scanner',
    'integration_test_runner',
    'naming_magic_checker',
    'orphan_scanner',
    'python_compat',
    'reconciler',
    'resource_guard',
    'roi_engine',
    'runbook_generator',
    'scan_mutex',
    'self_check',
    'self_test_verifier',
    'state_machine',
    'suppression_learner',
    'symlink_checker',
    'tamper_proof_audit',
    'test_fixture_checker',
    'trend_analyzer',
    '__main__',
]

__version__ = "1.0.0"