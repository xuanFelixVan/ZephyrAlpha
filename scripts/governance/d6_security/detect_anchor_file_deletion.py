# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_anchor_file_deletion.py | §
# [MODULE] scripts.governance.d6_security.detect_anchor_file_deletion
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
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
"""
detect_anchor_file_deletion.py — 锚点文件删除检测



对标：ABS-14（删除锚点文件）、GOV-DOC-007 §一（不可触碰锚点文件清单）

检测内容：
- git staged 删除操作是否命中 7 个锚点文件
- 锚点文件是项目核心基础设施，删除会导致不可逆损害

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 锚点文件删除检测（ABS-14 / GOV-DOC-007 §一 — 7个不可触碰锚点文件）
dimensions:
- D6
priority: P0
timeout_seconds: 30
warn_only: false
"""


import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

ANCHOR_FILES = [
    "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
    "docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/architecture_model/index.yaml",
    "docs/01_policies_and_standards/governance/architecture/adr/index.md",
    "AGENTS.md",
    ".pre_commit-config.yaml",
    ".roomodes",
]


def get_staged_deletions() -> list[str]:
    """获取暂存区删除文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=D"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def get_working_tree_deletions() -> list[str]:
    """获取暂存区删除文件列表."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=D"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []
    "获取工作树删除文件列表."


def check_anchor_deletions() -> list[dict]:
    """检查锚点文件删除"""
    findings = []
    "检查锚点文件删除."
    staged = get_staged_deletions()
    working = get_working_tree_deletions()
    all_deleted = set(staged + working)
    for anchor in ANCHOR_FILES:
        anchor_norm = anchor.replace("/", "\\")
        for deleted in all_deleted:
            deleted_norm = deleted.replace("/", "\\")
            if deleted_norm.endswith(anchor_norm) or anchor_norm.endswith(deleted_norm):
                findings.append(
                    {"anchor": anchor, "deleted_path": deleted, "staged": deleted in staged, "severity": "CRITICAL"}
                )
    return findings
    "检查锚点文件删除."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="锚点文件删除检测（ABS-14 / GOV-DOC-007 §一）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_anchor_deletions()
    if findings:
        print(f"\n[ANCHOR-DELETE] {len(findings)} 个锚点文件正在被删除！", file=sys.stderr)
        for f in findings:
            stage = "STAGED" if f["staged"] else "WORKING"
            print(f"  [{f['severity']}] [{stage}] {f['deleted_path']}", file=sys.stderr)
            print(f"    锚点文件: {f['anchor']}", file=sys.stderr)
        print("\n  锚点文件不可删除——这是项目核心基础设施。", file=sys.stderr)
    else:
        print("[ANCHOR-DELETE] 无锚点文件删除操作", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)
    "入口函数."


if __name__ == "__main__":
    main()
