# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_path_consistency.py | §
# [MODULE] scripts.governance.d5_architecture.validators.blueprint.validate_blueprint_path_consistency
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.blueprint.__init__
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
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

#!/usr/bin/env python3
"""
validate_blueprint_path_consistency.py — 蓝图路径一致性校验器
============================================================
依据：GOV-DOC-002 §一（LPC 双轨架构）+ PS-STD-005 §4（蓝图体系架构标准）
铁律 #4：产出物路径必须与 GOV-DOC-002 一致

检查项
------
1. 每份蓝图的 frontmatter `submodule_path` 与正文"代码落位"是否一致
2. submodule_path 是否符合 LPC 双轨规范（C轨 l<NN>_ 前缀 / B轨 无前缀）
3. submodule_path 是否在 validate_directory_structure.py 白名单中

Usage:
    python scripts/governance/d5_architecture/validate_blueprint_path_consistency.py
    python scripts/governance/d5_architecture/validate_blueprint_path_consistency.py --warn-only
"""

__manifest__ = {
    "args": ["--warn-only", "--jsonl"],
    "description": "蓝图路径一致性校验（frontmatter submodule_path vs 正文代码落位 vs 白名单）",
    "dimensions": ["D5", "D8"],
    "priority": "P0",
    "timeout_seconds": 60,
    "warn_only": False,
}

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import BLUEPRINTS_DIR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.walk import iter_files
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

C_TRACK_PATTERN = re.compile(r"^src/zephyr/l\d{2}_")
B_TRACK_NAMES = {
    "llm-security",
    "vector-memory",
    "context-engine",
    "orchestrator",
    "feedback-loop",
    "gates",
    "pipeline",
    "core",
    "db",
    "kb",
    "mcp",
    "shared",
    "hooks",
    "agent-rbac",
    "agent-spec",
    "audit-trail",
    "rollback",
    "escalation",
    "drift-detector",
    "budget-enforcer",
    "a2a",
    "telemetry",
}


def _extract_frontmatter_path(content: str) -> str | None:
    """_extract_frontmatter_path implementation."""
    m = re.search(r"^submodule_path:\s*(.+?)\s*$", content, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def _extract_frontmatter_scope(content: str) -> str | None:
    """_extract_frontmatter_scope implementation."""
    m = re.search(r"^submodule_paths_scope:\s*(.+?)\s*$", content, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def _extract_body_code_path(content: str) -> str | None:
    """_extract_body_code_path implementation."""
    patterns = [
        r"代码落位[：:]\s*`?([^`\n]+)`?",
        r"代码落位\s*\|\s*`?([^`|\n]+)`?",
    ]
    for pat in patterns:
        m = re.search(pat, content)
        if m:
            found = m.group(1) if m.lastindex else m.group(0)
            path_m = re.search(r"(src/zephyr/[^\s|`\n,]+)", found)
            if path_m:
                return path_m.group(1).rstrip("/")
    return None


def _classify_path(path: str) -> str:
    """_classify_path implementation."""
    if C_TRACK_PATTERN.match(path):
        return "C-track"
    short = path.replace("src/zephyr/", "").split("/")[0]
    if short in B_TRACK_NAMES:
        return "B-track"
    return "UNKNOWN"


def _scan_blueprints() -> list[dict]:
    """_scan_blueprints implementation."""
    results = []
    for bp in iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md"):
        content = bp.read_text(encoding="utf-8")
        fm_path = _extract_frontmatter_path(content)
        body_path = _extract_body_code_path(content)
        rel = str(bp.relative_to(REPO_ROOT)).replace("\\", "/")

        module_id_m = re.search(r'^module_id:\s*"?([^"\n]+)"?', content, re.MULTILINE)
        module_id = module_id_m.group(1) if module_id_m else "UNKNOWN"

        issues = []
        scope = _extract_frontmatter_scope(content)
        is_domain = scope is not None
        if fm_path and body_path and not is_domain:
            fm_norm = fm_path.rstrip("/")
            body_norm = body_path.rstrip("/")
            if fm_norm != body_norm:
                issues.append(f"frontmatter({fm_norm}) != body({body_norm})")
        if fm_path and not is_domain:
            track = _classify_path(fm_path)
            if track == "UNKNOWN":
                issues.append(f"submodule_path({fm_path}) not in C-track or B-track whitelist")
        if not fm_path:
            issues.append("frontmatter missing submodule_path")

        results.append(
            {
                "module_id": module_id,
                "blueprint": rel,
                "submodule_path": fm_path,
                "body_code_path": body_path,
                "track": _classify_path(fm_path) if fm_path else "NONE",
                "issues": issues,
            }
        )
    return results


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="蓝图路径一致性校验")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()

    results = _scan_blueprints()
    all_issues = [r for r in results if r["issues"]]

    if not all_issues:
        print("\u2705 蓝图路径一致性校验通过: 所有蓝图 submodule_path 与正文代码落位一致", file=sys.stderr)
        if args.jsonl:
            print(
                json.dumps({"severity": "INFO", "check_id": "BP-PATH-CONSISTENCY", "violations": 0}, ensure_ascii=False)
            )
        return EXIT_PASS
    print(f"\u274c 发现 {len(all_issues)} 份蓝图路径不一致:", file=sys.stderr)
    for r in all_issues:
        print(f"  [{r['module_id']}] {r['blueprint']}", file=sys.stderr)
        for issue in r["issues"]:
            print(f"    - {issue}", file=sys.stderr)

    if args.jsonl:
        for r in all_issues:
            print(
                json.dumps(
                    {
                        "severity": "HIGH",
                        "check_id": "BP-PATH-CONSISTENCY",
                        "module_id": r["module_id"],
                        "issues": r["issues"],
                    },
                    ensure_ascii=False,
                )
            )

    if args.warn_only:
        print("\n\u26a0\ufe0f  --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
        return EXIT_PASS
    print("\n\u274c 阻断: 请修复蓝图路径不一致。参考 GOV-DOC-002 \u00a7\u4e00 LPC 双轨架构。", file=sys.stderr)
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
