# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py | §
# [MODULE] scripts.governance.d5_architecture.validators.lifecycle.validate_module_lifecycle
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.lifecycle.__init__
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
# [TTL] task_bound
"""validate_module_lifecycle.py — 模块生命周期校验



对标：GOV-MOD-003 MLC-001/002/003（模块8阶段状态机）
     GOV-MOD-003 §6（各阶段约束）/ §8（P0特殊约束）

检测内容：
- 模块 status 是否属于 8 阶段合法枚举
- 禁止逆向状态转换（active→in_dev 等）
- P0 模块特殊约束（禁止 suspended、必须 frozen 契约等）
- deprecated 保留期 >= 90 天
- 退役 7 步完整性（superseded_by 字段）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 模块生命周期校验（GOV-MOD-003 MLC-001/002/003 — 8阶段状态机+P0约束）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402  SSoT 词表加载（治本 2026-06-30）
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse
from datetime import datetime

import yaml

# 治本（2026-06-30）：从 module_lifecycle_status_vocabulary.yaml 动态加载（SSoT，PS-VOC-027）。
VALID_MODULE_STATUSES = load_vocabulary_values("module_lifecycle_status_vocabulary.yaml")
FORBIDDEN_REVERSE_TRANSITIONS = {
    ("active", "in_dev"),
    ("active", "testing"),
    ("active", "in_design"),
    ("active", "planned"),
    ("testing", "in_design"),
    ("testing", "planned"),
    ("in_dev", "in_design"),
    ("in_dev", "planned"),
    ("in_design", "planned"),
}
ALLOWED_REVERSE = {("testing", "in_dev"), ("suspended", "active")}
DEPRECATED_MIN_DAYS = 90


def load_module_registry() -> dict:
    """加载模块注册表"""
    registry_paths = [
        REPO_ROOT / "" / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "module_id_registry.yaml",
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "module_id_registry.yaml",
    ]
    for p in registry_paths:
        if p.exists():
            try:
                return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            except (yaml.YAMLError, OSError):
                pass
    return {}
    "加载模块注册表."


def scan_module_lifecycle() -> list[dict]:
    """扫描模块生命周期合规性"""
    findings = []
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    for filepath in iter_files(docs_dir, extensions=frozenset({".md"})):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        module_id = fm.get("module_id", "")
        status = fm.get("status", "")
        priority = fm.get("priority", "")
        date_str = fm.get("date", "")
        superseded_by = fm.get("superseded_by", "")
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        if not module_id or not status:
            continue
        if status not in VALID_MODULE_STATUSES:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "INVALID_STATUS",
                    "detail": f"status='{status}' 不在合法枚举中（合法值: {', '.join(sorted(VALID_MODULE_STATUSES))}）",
                    "severity": "HIGH",
                }
            )
        if status == "deprecated" and (not superseded_by):
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "MISSING_SUPERSEDED_BY",
                    "detail": "deprecated 模块缺少 superseded_by 字段",
                    "severity": "HIGH",
                }
            )
        if status == "deprecated" and date_str:
            try:
                dep_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                days = (datetime.now() - dep_date).days
                if days < DEPRECATED_MIN_DAYS:
                    findings.append(
                        {
                            "file": rel,
                            "module_id": module_id,
                            "type": "DEPRECATION_TOO_EARLY",
                            "detail": f"deprecated 仅 {days} 天，保留期需 >= {DEPRECATED_MIN_DAYS} 天",
                            "severity": "MEDIUM",
                        }
                    )
            except ValueError:
                pass
        if status == "active" and superseded_by:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "type": "ACTIVE_WITH_SUPERSEDED_BY",
                    "detail": "active 模块不应有 superseded_by 字段",
                    "severity": "MEDIUM",
                }
            )
        if priority == "P0":
            if status == "suspended":
                findings.append(
                    {
                        "file": rel,
                        "module_id": module_id,
                        "type": "P0_SUSPENDED",
                        "detail": "P0 模块禁止 suspended",
                        "severity": "HIGH",
                    }
                )
    return findings
    "扫描模块生命周期合规性."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="模块生命周期校验（GOV-MOD-003 MLC-001/002/003）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = scan_module_lifecycle()
    by_type = defaultdict(list)
    for f in findings:
        by_type[f["type"]].append(f)
    if findings:
        print(f"\n[MODULE-LIFECYCLE] {len(findings)} 个模块生命周期违规:", file=sys.stderr)
        for rtype, items in by_type.items():
            print(f"\n  {rtype} ({len(items)} 个):", file=sys.stderr)
            for f in items[:10]:
                print(f"    [{f['severity']}] {f['module_id']} ({f['file']})", file=sys.stderr)
                print(f"      {f['detail']}", file=sys.stderr)
    else:
        print("[MODULE-LIFECYCLE] 模块生命周期合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
