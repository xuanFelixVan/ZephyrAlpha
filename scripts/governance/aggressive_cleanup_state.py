#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激进清理 docs/09_AUDIT/STATE/ 目录，目标：≤60 个文件

清理规则：
1. 永久保留（必须保留）：
   - 文件名含 LATEST, MASTER, INDEX, DECISION, RESOLUTION, CANONICAL
   - elimination-pipeline-tracker.yaml
   - module_id_registry.json

2. 删除（临时扫描产物，历史价值低）：
   - 所有含 AUDIT, SCAN, REPORT, CHECK, ANALYSIS, FIX, METRICS 的文件（除非是最新且必要的）
   - 所有日期在 2026-04-07 到 2026-04-12 之间的历史扫描文件
   - 所有 ROUND2, ROUND3, v2, v3, v4 等多版本文件
   - 所有 Untitled, temp, backup 类文件

3. 选择性保留（最近且重要）：
   - 2026-04-13 之后的文件
   - 与 orphan, governance, subsystem 相关的最终报告
"""

import re
from datetime import datetime
from pathlib import Path

STATE_DIR = Path("docs/09_AUDIT/STATE")

# 永久保留关键词
MUST_KEEP_KEYWORDS = ["LATEST", "MASTER", "INDEX", "DECISION", "RESOLUTION", "CANONICAL",
                      "TRACKER", "REGISTRY", "ELIMINATION-PIPELINE", "MODULE_ID_REGISTRY"]

# 优先删除关键词（临时扫描产物）
DELETE_KEYWORDS = ["ROUND2", "ROUND3", "ROUND4", "ROUND5", "ROUND6", "ROUND7", "ROUND8", "ROUND9", "ROUND10", "ROUND11",
                   "_V2_", "_V3_", "_V4_", "_V5_", "_V6_", "_V7_",
                   "UNTITLE", "TEMP_", "TEMP-", ".BACKUP", "_BACKUP_", "-BACKUP-"]

# 可删除的扫描类关键词（保留最近日期的）
SCAN_KEYWORDS = ["AUDIT", "SCAN", "REPORT", "CHECK", "ANALYSIS", "FIX-", "_FIX_", "METRICS", "MONITORING",
                 "SUPPLEMENT", "COMPREHENSIVE", "DEEP-", "_DEEP_", "GOVERNANCE_CHECK", "LAYER_CHECK",
                 "SPARSE_DIRECTORY", "INTEGRATION_RESULT", "DIRECTORY_INTEGRATION"]

# 额外删除 - 2026-04-13 之前的非关键文件
EXTRA_DELETE_PATTERNS = [
    "layer*_", "p0_", "p1_", "p2_", "weekly_", "reference_", "responsibility_",
    "orphan_governance_inventory", "sentinel-l1-after-", "sentinel-l1-p1c-readme",
    "sentinel-l1-post-remediation", "sentinel-l1-pre-construction",
    "phase4", "phase_4", "strict-orphan", "subsystem-health",
    "basename-collisions-2026", "basename-collisions-resolve",
    "ai-workflow-", "ai_strategy_", "architecture-service-catalog",
    "batch-metadata-supplement", "batch-responsibility",
    "metadata-completeness-check-report-20260413",
    "quality-metrics-report", "quality-standards-optimization",
    "comprehensive-", "fifth-", "sixth-", "third-",
    "sparse-directory-", "tier-a-overlap-",
    "trae-autonomous-work", "trae-blueprint-task", "trae-line-task-backlog",
    "continuous-audit", "precommit-failure",
    "fix-dead-links-20260416.md",  # 保留 json 版本
    # 进一步清理 - 删除更多非关键文件
    "layer2-", "layer4_", "layer9_", "layer11-",
    "orphan_eradication_execution_",
    "basename-collisions-decision-20260413",
    "governance-final-report", "governance_check_report",
    "phase-1-scan-completion", "professional-blueprint-governance",
    "repo-three-zone-cleanup", "repo-directory-rollup-20260416.md",
    "blueprint-d-overlap-", "blueprint-layer-mismatch",
    "arch-module-gap-register",
    "directory-refactoring-plan", "docs-nav-coverage-sample",
    "handoff-orphan-governance",
    "path-reference-human-review",
    "p1c-deferred", "p1-p2-fix-", "p2-issues-fix",
    "periodic-check-guide", "periodic-review-plan",
    "data-source-p2-",
    "cursor-rules-phantom-reference",
    "audit_comparison_report",
    "automated_workflow_result",
    "cjk_question_mark_stats",
    "encoding_artifact_",
    "early_warning_result",
    "fix_naming_issues",
    "frontmatter_audit_report",
    "gh-wave2-lost-files", "gh-wave3-priority-files",
    "git-tracked-path-anomalies",
    "inventory_md",
    "manifest-path-audit",
    "md-files-by-subdirectory",
    "missing_index_directories",
    "monitoring_history",
    "orphan_governance_program",
    "progress_table",
    "quick_audit_state",
    "readme_generation",
    "responsibility-boundary-map", "responsibility-overlap-analysis",
    "SENTINEL_L1_AFTER_", "SENTINEL_L2_SCAN",
    "sentinel-l2-scan",
    "SENTINEL_PROGRESS",
    "system_rectification_log",
    "yaml_error_files_list",
    "工作汇报-规则系统扫描",
]

# 保留的关键文件（即使匹配上述模式）
FORCE_KEEP_PATTERNS = [
    "sentinel-l1-scan-latest",
    "elimination-pipeline-tracker",
    "module_id_registry",
    "INDEX.md",
    "ORPHAN_DECISION",
    "orphan-decision",
    "orphan_eradication_master_plan",
    "subsystem-dedup-decisions",
    "basename-collisions-decision",
    "governance-decisions-locked",
    "trae-line-task-index",
    "trae-master-execution-checklist",
]

def get_file_date(path: Path) -> datetime:
    """从文件名提取日期"""
    match = re.search(r"(\d{4}-?\d{2}-?\d{2})", path.name)
    if match:
        date_str = match.group(1).replace("-", "")
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            pass
    return datetime.fromtimestamp(path.stat().st_mtime)

def should_keep(path: Path) -> tuple[bool, str]:
    """判断文件是否应该保留，返回 (是否保留, 原因)"""
    name_upper = path.name.upper()
    name_lower = path.name.lower()

    # 0. 强制保留的关键文件
    for pattern in FORCE_KEEP_PATTERNS:
        if pattern.lower() in name_lower:
            return True, f"FORCE_KEEP ({pattern})"

    # 1. 永久保留关键词
    for kw in MUST_KEEP_KEYWORDS:
        if kw in name_upper:
            return True, f"MUST_KEEP ({kw})"

    # 2. 优先删除关键词
    for kw in DELETE_KEYWORDS:
        if kw in name_upper:
            return False, f"DELETE_KEYWORD ({kw})"

    # 3. 检查额外删除模式
    for pattern in EXTRA_DELETE_PATTERNS:
        pattern_upper = pattern.upper().replace("*", "")
        if "*" in pattern:
            # 通配符匹配
            import fnmatch
            if fnmatch.fnmatch(name_upper, pattern_upper + "*"):
                return False, f"EXTRA_DELETE ({pattern})"
        elif pattern_upper in name_upper:
            return False, f"EXTRA_DELETE ({pattern})"

    # 4. 检查日期 - 删除 2026-04-12 之前的旧文件
    file_date = get_file_date(path)
    if file_date < datetime(2026, 4, 13):
        # 检查是否是扫描类文件
        for kw in SCAN_KEYWORDS:
            if kw in name_upper:
                return False, f"OLD_SCAN ({file_date.strftime('%Y-%m-%d')})"

    # 5. 默认保留
    return True, "KEEP"

def main(dry_run: bool = True):
    print(f"{'[DRY-RUN] ' if dry_run else ''}激进清理 STATE 目录...")
    print(f"目录: {STATE_DIR}")
    print("-" * 80)

    if not STATE_DIR.exists():
        print("错误: 目录不存在")
        return

    all_files = [p for p in STATE_DIR.iterdir() if p.is_file()]
    print(f"总文件数: {len(all_files)}")

    files_to_delete = []
    files_to_keep = []

    for p in all_files:
        keep, reason = should_keep(p)
        if keep:
            files_to_keep.append((p, reason))
        else:
            files_to_delete.append((p, reason))

    print(f"保留文件数: {len(files_to_keep)}")
    print(f"删除文件数: {len(files_to_delete)}")
    print()

    # 显示将要删除的文件
    if files_to_delete:
        print("将要删除的文件:")
        for p, reason in sorted(files_to_delete, key=lambda x: x[0].name):
            print(f"  [{reason}] {p.name}")
        print()

    # 显示保留的文件
    print("保留的文件:")
    for p, reason in sorted(files_to_keep, key=lambda x: x[0].name):
        print(f"  [{reason}] {p.name}")

    # 执行删除
    if not dry_run and files_to_delete:
        print()
        print("执行删除...")
        for p, _ in files_to_delete:
            try:
                p.unlink()
                print(f"  已删除: {p.name}")
            except Exception as e:
                print(f"  删除失败: {p.name} - {e}")

    print()
    print("-" * 80)
    if dry_run:
        print("[DRY-RUN] 完成。使用 --execute 参数执行实际删除。")
    else:
        print("清理完成!")

    final_count = len([p for p in STATE_DIR.iterdir() if p.is_file()])
    print(f"清理后文件数: {final_count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="激进清理 STATE 目录")
    parser.add_argument("--execute", action="store_true", help="执行实际删除（默认 dry-run）")
    args = parser.parse_args()
    main(dry_run=not args.execute)
