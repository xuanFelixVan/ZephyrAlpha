# ============================================================================
# _scanners 聚合 — 扫描器与检查器簇（功能域门面，ARCH-034）
# ============================================================================
# 职责：增量/无头/孤儿扫描 + 符号链接/文件属性/命名魔法/测试夹具检查 + 数据质量扫描
# 归属规则：*_scanner/*_checker/scan_mutex/data_*/cross_env_consistency/python_compat/
#   gitignore_auditor/benchmark_integrity/code_review_ai
# 完整模块清单见 __init__.py 顶部"模块地图"
# ============================================================================
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.gov_drift._scanners
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.incremental_scanner; zephyr.gov_drift.headless_scanner; zephyr.gov_drift.file_attr_checker; zephyr.gov_drift.gitignore_auditor; zephyr.gov_drift.symlink_checker; zephyr.gov_drift.naming_magic_checker; zephyr.gov_drift.test_fixture_checker; zephyr.gov_drift.python_compat; zephyr.gov_drift.orphan_scanner; zephyr.gov_drift.scan_mutex
# [CONSUMERS] zephyr.gov_drift.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py
# [A_module] module_id=MOD-SEC__scanners | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.gov_drift.incremental_scanner import (
    ChangeSet,
    DetectorFileMapping,
    FileChange,
    IncrementalScanner,
)
from zephyr.gov_drift.naming_magic_checker import NamingMagicAlert, scan_naming_magic
from zephyr.gov_drift.orphan_scanner import (
    OrphanResource,
    find_orphan_data,
    find_orphan_docs,
    find_orphan_scripts,
    scan_orphan_resources,
)
from zephyr.gov_drift.python_compat import (
    PythonCompatIssue,
    auto_fix_compat,
    generate_compat_report,
    scan_python_compat,
)
from zephyr.gov_drift.scan_mutex import QueuedScan, ScanLockRecord, ScanMutex
from zephyr.gov_drift.symlink_checker import SymlinkIssue, check_broken_symlinks
from zephyr.gov_drift.test_fixture_checker import (
    FixtureDriftEvent,
    run_fixture_check,
    scan_expected_output_drift,
    scan_fixture_schema_drift,
    scan_mock_target_drift,
)

_SUBMODULES = [
    "benchmark_integrity",
    "code_review_ai",
    "cross_env_consistency",
    "data_classification",
    "data_lifecycle",
    "data_quality",
    "data_source_reliability",
    "headless_scanner",
    "incremental_scanner",
]

__all__ = [
    "ChangeSet",
    "DetectorFileMapping",
    "FileAttrIssue",
    "FileChange",
    "FixtureDriftEvent",
    "GitignoreAudit",
    "HeadlessDiffEntry",
    "IncrementalScanner",
    "InterruptLog",
    "NamingMagicAlert",
    "OrphanResource",
    "PythonCompatIssue",
    "QueuedScan",
    "ScanLockRecord",
    "ScanMutex",
    "SymlinkIssue",
    "audit_gitignore",
    "auto_fix_compat",
    "capture_baseline",
    "check_broken_symlinks",
    "check_encoding",
    "check_size_anomaly",
    "find_orphan_data",
    "find_orphan_docs",
    "find_orphan_scripts",
    "find_over_ignored_critical",
    "find_uncovered_types",
    "find_untracked_generated",
    "generate_compat_report",
    "headless_scan_light",
    "parse_gitignore",
    "parse_interrupt_log",
    "run_fixture_check",
    "scan_expected_output_drift",
    "scan_fixture_schema_drift",
    "scan_mock_target_drift",
    "scan_naming_magic",
    "scan_orphan_resources",
    "scan_python_compat",
]
