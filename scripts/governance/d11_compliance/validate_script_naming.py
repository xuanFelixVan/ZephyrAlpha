# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_script_naming.py | §
# [MODULE] scripts.governance.d11_compliance.validate_script_naming
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
validate_script_naming.py — 审计脚本命名规范门禁

对标 SCRIPT-QUALITY-001 §1.3 术语定义（审计脚本命名前缀受控词汇表）

检测内容：
- 脚本文件名是否符合合法前缀模式（validate_/detect_/audit_/check_/generate_/measure_/sync_/manage_/fix_/assign_/batch_/score_/scan_/archive_/reset_/analyze_/merge_/inject_/refresh_/arbitrate_/trace_/track_/run_/apply_/extract_/align_）
- 不符合任何合法前缀的脚本报告为违规

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 审计脚本命名规范门禁——检测不符合合法前缀模式的脚本文件名
dimensions:
- D11
- D1
priority: P1
timeout_seconds: 15
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

LEGAL_PREFIXES = (
    "validate_",
    "detect_",
    "audit_",
    "check_",
    "generate_",
    "measure_",
    "sync_",
    "manage_",
    "fix_",
    "assign_",
    "batch_",
    "score_",
    "scan_",
    "archive_",
    "reset_",
    "analyze_",
    "merge_",
    "inject_",
    "refresh_",
    "arbitrate_",
    "trace_",
    "track_",
    "run_",
    "apply_",     # ARCH-060: 全景图写入工具（apply_depgraph/apply_decisiongraph/apply_dataflowgraph）
    "extract_",   # ARCH-060: 全景图只读提取（extract_depgraph/extract_decisiongraph）
    "align_",     # ARCH-060: 全景图对齐检测（align_panoramas）
)

EXCLUDE_DIRS = frozenset({"_shared", "__pycache__", "test_fixtures"})
EXCEPTIONS = frozenset(
    {
        "run_all.py",
        "run_incremental.py",
        "env_check.py",
        "session_simulator.py",
        "task_self_check.py",
        "score_architecture.py",
        "status.py",
        "task_summary.py",
        "gate_engine_selfcheck.py",
        "finding_state_machine.py",
        "phase_e_context_check.py",
        "auto-generate-index.py",
        "auto_generate_index.py",
        "adversarial_log.py",
        "adversarial_sys_master_test.py",
        "auto_sync_all_registries.py",
        "blind_spot_registry.py",
        "changelog.py",
        "construction_gate.py",
        "crosscheck_sys_master_deps.py",
        "cbg_reset.py",
        "drafts_zone_archiver.py",
        "deep_content_scanner.py",
        "dependency-graph.py",
        "g9_compliance_check.py",
        "backup_runtime_state.py",
        "compute_sla_metrics.py",
        "create_task_from_finding.py",
        "pre_op_check.py",
        "pre_write_gate.py",
        "rebuild_audit_index.py",
        "ri_boundary_check.py",
        "ri_build_completion_check.py",
        "session_startup_check.py",
        "test_lock_scenarios.py",
        "update_progress.py",
        "verify_audit_integrity.py",
        "verify_downstream_anchors.py",
        "verify_file_paths.py",
        "vms_blindspot_check.py",
        "vms_build_completion_check.py",
        "vms_cron_monitor.py",
        "vms_cross_file_check.py",
        "vms_health_check.py",
        "vms_migrate.py",
        "vms_migration_dry_run.py",
        "vms_phase_rollback.py",
        "vms_version_sync_check.py",
        "ci_self_check.py",
    }
)

RE_LEGAL = re.compile(r"^(" + "|".join(re.escape(p.rstrip("_")) for p in LEGAL_PREFIXES) + r")_")


def scan_scripts() -> list[dict]:
    """scan_scripts implementation."""
    findings = []
    for py in sorted(SCRIPTS_DIR.rglob("*.py")):
        parts = py.relative_to(SCRIPTS_DIR).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if py.name == "__init__.py":
            continue
        if py.name in EXCEPTIONS:
            continue

        name = py.name
        if not any(name.startswith(p) for p in LEGAL_PREFIXES):
            rel = str(py.relative_to(SCRIPTS_DIR)).replace("\\", "/")
            suggestions = []
            if "scan" in name.lower() or "scanner" in name.lower():
                suggestions.append("scan_")
            if "archiv" in name.lower():
                suggestions.append("archive_")
            if "reset" in name.lower():
                suggestions.append("reset_")
            if "secret" in name.lower() or "leak" in name.lower():
                suggestions.append("detect_")
            if not suggestions:
                suggestions.append("validate_/detect_/audit_/check_")

            findings.append(
                {
                    "file": rel,
                    "name": name,
                    "suggestion": f"rename to {suggestions[0]}{name}",
                }
            )

    return findings


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    findings = scan_scripts()
    if not findings:
        print("OK — all scripts follow naming conventions", file=sys.stderr)
        return EXIT_PASS

    print(f"FINDINGS — {len(findings)} script(s) with non-standard naming:", file=sys.stderr)
    for f in findings:
        print(f"  {f['file']}: '{f['name']}' does not match any legal prefix → {f['suggestion']}", file=sys.stderr)

    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
