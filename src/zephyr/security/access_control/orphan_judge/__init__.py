# [A_module] module_id=MOD-SEC_orphan_judge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""[BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan-judge/blueprint.md

[MODULE] zephyr.security.access_control.orphan_judge

[INVARIANTS] 蓝图 §4 文件清单与代码双向对齐

[MODIFY-GUARD] orphan-judge/blueprint.md; orphan-judge/__init__.py __all__

[CONSUMERS] 见蓝图 §4 接口契约

[STABILITY] evolving

[SAFETY] M

[AI_AUTONOMY] ai_modifiable

[ERROR_CONTRACT] OrphanJudgeError

[TESTS] tests/orphan-judge/

orphan-judge — MOD-INF-029 · 孤儿审判器

========================================

蓝图: docs/03_modules/_cross_layer/orphan-judge/blueprint.md

actual_disk_path: src/zephyr/security/access_control/orphan_judge/

职责

----

  孤儿文件五层判定——L0 注册表对齐 / L1 引用图可达 / L2 功能覆盖

  / L3 代码价值 / L4 安全围栏

  整合自 runtime/orphan_detector.py

模块结构

--------

  orphan_detector     — 孤儿检测器(从 runtime/ 整合)

  five_layer_judge    — 五层判定引擎

  reference_graph     — 引用图引擎

  judgment_cache      — 判定结果缓存

  safety_fence        — 安全围栏(批量删除保护)

  incremental_scanner — 增量扫描引擎

  script_scheduler    — 脚本调度器

  mcp_handler         — MCP 调用治理

"""

from zephyr.security.access_control.orphan_judge.__main__ import main as Main
from zephyr.security.access_control.orphan_judge.cascade_analyzer import CascadeAnalyzer, CascadeResult, CascadeRisk
from zephyr.security.access_control.orphan_judge.config_loader import ConfigLoader
from zephyr.security.access_control.orphan_judge.db import JudgmentDB as Db
from zephyr.security.access_control.orphan_judge.decision_table import DecisionTable, LayerResult, Verdict
from zephyr.security.access_control.orphan_judge.deprecation_tracker import DeprecationRecord, DeprecationTracker
from zephyr.security.access_control.orphan_judge.duplicate_detector import DuplicateDetector
from zephyr.security.access_control.orphan_judge.models import JudgmentRecord
from zephyr.security.access_control.orphan_judge.orphan_collector import CollectionResult, Judgment, OrphanCollector
from zephyr.security.access_control.orphan_judge.orphan_detector import OrphanDetector, OrphanReport
from zephyr.security.access_control.orphan_judge.reference_graph_engine import ReferenceGraphEngine
from zephyr.security.access_control.orphan_judge.registration_checker import RegistrationChecker
from zephyr.security.access_control.orphan_judge.report_generator import ReportGenerator
from zephyr.security.access_control.orphan_judge.safety_fence import SafetyCheckResult, SafetyFence
from zephyr.security.access_control.orphan_judge.standalone_evaluator import StandaloneEvaluator
from zephyr.security.access_control.orphan_judge.swid_tag import SwidTag
from zephyr.security.access_control.orphan_judge.unique_analyzer import UniqueValueAnalyzer

__all__ = [
    "OrphanDetector",
    "OrphanReport",
    "__main__",
    "cascade_analyzer",
    "config_loader",
    "db",
    "decision_table",
    "deprecation_tracker",
    "duplicate_detector",
    "models",
    "orphan_collector",
    "orphan_detector",
    "reference_graph_engine",
    "registration_checker",
    "report_generator",
    "safety_fence",
    "standalone_evaluator",
    "swid_tag",
    "unique_analyzer",
'drift_bridge', 'escalation_bridge', 'feedback_bridge', 'judge', 'kb_bridge', 'mcp_integration', 'rbac_bridge']

__all__.append("DuplicateDetector")
__all__.extend(
    [
        "CascadeAnalyzer",
        "CascadeResult",
        "CascadeRisk",
        "CollectionResult",
        "DecisionTable",
        "DeprecationRecord",
        "DeprecationTracker",
        "Judge",
        "Judgment",
        "LayerResult",
        "OrphanCollector",
        "SafetyCheckResult",
        "SafetyFence",
        "Verdict",
    ]
)

__all__.append("RegistrationChecker")

__all__.append("ReferenceGraphEngine")

__all__.append("UniqueValueAnalyzer")

__all__.append("StandaloneEvaluator")

__all__.append("Main")

__all__.append("JudgmentRecord")

__all__.append("Db")

__all__.append("ReportGenerator")

__all__.append("ConfigLoader")

__all__.append("SwidTag")
__all__.extend(
    [
        "models",
        "unique_analyzer",
    ]
)
