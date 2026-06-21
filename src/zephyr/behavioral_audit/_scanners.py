# [A_module] module_id=MOD-SEC__scanners | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.behavioral_audit._scanners
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.behavioral_audit.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_behavioral_auditor_imports.py

from zephyr.behavioral_audit.incremental_scanner import (
    FileChange,
    ChangeSet,
    DetectorFileMapping,
    IncrementalScanner,
)
from zephyr.behavioral_audit.headless_scanner import (
    HeadlessDiffEntry,
    InterruptLog,
    headless_scan_light,
    parse_interrupt_log,
)
from zephyr.behavioral_audit.file_attr_checker import (
    FileAttrIssue,
    capture_baseline,
    check_size_anomaly,
    check_encoding,
)
from zephyr.behavioral_audit.gitignore_auditor import (
    GitignoreAudit,
    parse_gitignore,
    find_untracked_generated,
    find_over_ignored_critical,
    find_uncovered_types,
    audit_gitignore,
)
from zephyr.behavioral_audit.symlink_checker import SymlinkIssue, check_broken_symlinks
from zephyr.behavioral_audit.naming_magic_checker import NamingMagicAlert, scan_naming_magic
from zephyr.behavioral_audit.test_fixture_checker import (
    FixtureDriftEvent,
    scan_fixture_schema_drift,
    scan_mock_target_drift,
    scan_expected_output_drift,
    run_fixture_check,
)
from zephyr.behavioral_audit.python_compat import (
    PythonCompatIssue,
    scan_python_compat,
    auto_fix_compat,
    generate_compat_report,
)
from zephyr.behavioral_audit.orphan_scanner import (
    OrphanResource,
    find_orphan_scripts,
    find_orphan_data,
    find_orphan_docs,
    scan_orphan_resources,
)
from zephyr.behavioral_audit.scan_mutex import ScanLockRecord, QueuedScan, ScanMutex

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
    "FileChange",
    "ChangeSet",
    "DetectorFileMapping",
    "IncrementalScanner",
    "HeadlessDiffEntry",
    "InterruptLog",
    "headless_scan_light",
    "parse_interrupt_log",
    "FileAttrIssue",
    "capture_baseline",
    "check_size_anomaly",
    "check_encoding",
    "GitignoreAudit",
    "parse_gitignore",
    "find_untracked_generated",
    "find_over_ignored_critical",
    "find_uncovered_types",
    "audit_gitignore",
    "SymlinkIssue",
    "check_broken_symlinks",
    "NamingMagicAlert",
    "scan_naming_magic",
    "FixtureDriftEvent",
    "scan_fixture_schema_drift",
    "scan_mock_target_drift",
    "scan_expected_output_drift",
    "run_fixture_check",
    "PythonCompatIssue",
    "scan_python_compat",
    "auto_fix_compat",
    "generate_compat_report",
    "OrphanResource",
    "find_orphan_scripts",
    "find_orphan_data",
    "find_orphan_docs",
    "scan_orphan_resources",
    "ScanLockRecord",
    "QueuedScan",
    "ScanMutex",
]
