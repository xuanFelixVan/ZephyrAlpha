# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_script_naming.py | §
# [MODULE] scripts.governance.d11_compliance.validate_script_naming
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
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
    "apply_",  # ARCH-060: 全景图写入工具（apply_depgraph/apply_decisiongraph/apply_dataflowgraph）
    "extract_",  # ARCH-060: 全景图只读提取（extract_depgraph/extract_decisiongraph）
    "align_",  # ARCH-060: 全景图对齐检测（align_panoramas）
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
        "create_alignment_tasks.py",
        "dm105_depgraph_triage.py",
        "group_orphan_modules.py",
        "list_phase0_tasks.py",
        "migrate_clean_build_status.py",
        "migrate_domain_id_hyphen_to_underscore.py",
        "perf_depgraph_baseline.py",
        "phase_a_backup.py",
        "rename_kebab_to_snake.py",
        "rename_whitelist_cleanup.py",
        "verify_final_delivery.py",
        "verify_rule_yaml_migration.py",
        "cleanup_p0_auto_bridged.py",
        "cleanup_p0_ops_pending.py",
        "task_show.py",
        "architecture_health_dashboard.py",
        "ast_import_rewriter.py",
        "collect_system_threads.py",
        "verify_key_imports.py",
        "verify_schema_health.py",
        "cleanup_stash.py",
        "backfill_doctype_metadata.py",
        "backfill_ttl_metadata.py",
        "classify_ttl_by_content.py",
        "migrate_illegal_doctype.py",
        "dependency_graph.py",
        "diagnose_depgraph.py",
        "dm200912_query_domains.py",
        "dm200916_write_direct.py",
        "_common.py",
        "domain_name_mapping.py",
        "panorama_common.py",
        "pre_delete_safety_check.py",
        "blueprint_frontmatter_reconciler.py",
        "any_type_inferrer.py",
        "rewrite_imports.py",
        "metric_count_drift_reconciler.py",
        "readme_version_sync_reconciler.py",
        "git_health_smoke.py",
        "_concurrency.py",
        "governance_watchdog.py",
        "mutation_test_post_sync_validator.py",
        "mutation_test_reconciliation_registry.py",
        "verify_reconciliation_registry.py",
        "migrate_data.py",
        "seed_from_yaml.py",
        "migrate_to_metadata_tables.py",
        "gate_cache.py",
        "query_module_panorama.py",
        "concurrent_commit_test.py",
        "concurrent_write_test.py",
        "p2_pg_concurrent_test.py",
        "red_blue_test.py",
        "rollback_depgraph.py",
        "session_startup_health_check.py",
        "session_worktree_cli.py",
        "test_remediation_progress_smoke.py",
        "verify_sync_integrity.py",
        # --- #ARCH-114 豁免登记（2026-08-17 AI-GOVA-001 裁定路径 C：豁免登记）---
        # 裁定书=architecture_issue_registry.yaml #ARCH-114；三选一对比分析随
        # 治理批 A 包 commit 说明。以下条目按 D2 纪律逐组注明豁免理由。
        # （机制对齐上方既有条目：按 basename 匹配，注释标明所在目录）
        # [oneoff 一次性迁移/登记脚本——已执行完毕，重命名=死代码 churn，列退役候选]
        "_fix_remaining_en.py",  # oneoff/
        "data_domain_audit_query.py",  # oneoff/
        "data_domain_design_state_complete.py",  # oneoff/
        "factor_design_state_complete.py",  # oneoff/
        "load_acquisition_decisions.py",  # oneoff/
        "register_candidate_acquisitions.py",  # oneoff/
        # [import 库性质非 CLI 脚本——重命名断 import 链]
        "frontmatter.py",  # shared/
        "zoomable_html.py",  # d5_architecture/generators/
        # [git hook——引用方为 hook 安装面，重命名须同步仓外配置]
        "post_commit_regen_yaml.py",  # git_hooks/
        # [一次性迁移脚本——已执行]
        "add_acquisition_fields.py",  # migrations/
        # [存量活跃工具脚本——重命名须跨域同步 manifest/registry/引用方，
        #  与并发施工域碰撞风险高于词汇纯度收益，爷爷条款豁免]
        "add_deferred_design_edges.py",
        "add_module_translation.py",  # d3_metadata/
        "domain_header_maint.py",  # d3_metadata/
        "retire_tmp_artifacts.py",  # d6_security/
        "algo_flow_translation_reconciler.py",  # d8_doc_sync/
        "requirements_version_sync_reconciler.py",  # d8_doc_sync/
        "decision_node_plain_zh_backfill.py",
        "harvest_candidates_from_drafts.py",
        "query_candidate_registry.py",
        "reconcile_generators.py",
        "register_deferred_modules.py",
        "verify_generator_paths.py",
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
