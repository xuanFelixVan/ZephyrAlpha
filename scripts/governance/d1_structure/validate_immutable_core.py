# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/validate_immutable_core.py | §
# [MODULE] scripts.governance.d1_structure.validate_immutable_core
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
validate_immutable_core.py — immutable_core 文件修改检测



对标：PS-STD-003 ABS-01（AI 不可改 immutable_core 层）
     AGENTS.md §4（编码安全——唯一始终生效的硬规则）
     metadata_registry.yaml（immutable_core 标记字段）

检测内容：
- 扫描 frontmatter 中标记了 immutable_core 或类似的保护标记的文件
- 通过 git log 检查最近修改是否由 AI 执行（非 Owner）
- 对比 frontmatter 中声明的 immutable 字段与实际文件的任何修改

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: immutable_core 文件修改检测（ABS-01 — P1治理完整性）
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXCLUDE_DIRS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse
import subprocess

IMMUTABLE_MARKERS = ["immutable_core", "immutable", "readonly_ai", "ai_cannot_modify"]
AI_AUTONOMY_MARKERS = ["ai_autonomy", "autonomy_level"]
_EXTRA_EXCLUDE = EXCLUDE_DIRS | {"scripts"}


def is_immutable(frontmatter: dict) -> bool:
    """Return True if frontmatter marks this file as immutable (AI should not modify)."""
    for marker in IMMUTABLE_MARKERS:
        if marker in frontmatter:
            return True
    autonomy = frontmatter.get("modification_permission", frontmatter.get("ai_autonomy", ""))
    if isinstance(autonomy, str) and "immutable" in autonomy.lower():
        return True
    return False


def get_recent_modifications(filepath: Path, max_commits: int = 10) -> list[dict]:
    """get recent modifications"""
    try:
        result = subprocess.run(
            ["git", "log", f"-n{max_commits}", "--pretty=format:%H|%an|%ae|%s|%ci", "--", str(filepath)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            return []
        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 4)
            if len(parts) >= 5:
                commits.append(
                    {
                        "hash": parts[0][:8],
                        "author": parts[1],
                        "email": parts[2],
                        "message": parts[3][:120],
                        "date": parts[4],
                    }
                )
        return commits
    except (subprocess.SubprocessError, OSError):
        return []
    "get recent modifications."


def scan_docs() -> tuple[list[dict], int]:
    """scan docs"""
    findings = []
    "扫描并返回发现列表."
    files_scanned = 0
    docs_dir = REPO_ROOT / "docs"
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        files_scanned += 1
        fm = parse_frontmatter_from_file(filepath)
        if not fm or not is_immutable(fm):
            continue
        rel = str(filepath.relative_to(REPO_ROOT))
        commits = get_recent_modifications(filepath, max_commits=5)
        finding = {
            "file": rel,
            "immutable_marks": [m for m in IMMUTABLE_MARKERS if m in fm],
            "modification_permission": fm.get("modification_permission", fm.get("ai_autonomy", "N/A")),
            "recent_commits": commits,
            "owner_is_committer": any("ZephyrAlpha-Owner" in c["author"] or "Owner" in c["author"] for c in commits),
        }
        findings.append(finding)
    return (findings, files_scanned)
    "scan docs."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="immutable_core 文件修改检测")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()
    findings, files_scanned = scan_docs()
    immutable_files = [f for f in findings]
    violated = [f for f in immutable_files if f["recent_commits"] and (not f["owner_is_committer"])]
    print(f"\n[IMMUTABLE-SCAN] 扫描 {files_scanned} 个 .md 文件", file=sys.stderr)
    print(f"  不可变标记文件: {len(immutable_files)}", file=sys.stderr)
    print(f"  疑似 AI 修改: {len(violated)}", file=sys.stderr)
    for f in immutable_files:
        print(f"\n  📄 {f['file']}", file=sys.stderr)
        print(f"     标记: {', '.join(f['immutable_marks'])}", file=sys.stderr)
        print(f"     AI自治: {f['modification_permission']}", file=sys.stderr)
        if f["recent_commits"]:
            print(f"     最近修改: {len(f['recent_commits'])} 次", file=sys.stderr)
            for c in f["recent_commits"][:3]:
                status = "✅ Owner" if "Owner" in c["author"] else "⚠ NOT Owner"
                print(f"       [{status}] {c['hash']} {c['author']}: {c['message'][:80]}", file=sys.stderr)
    if violated:
        print(f"\n⚠ {len(violated)} 个 immutable_core 文件被非 Owner 修改！", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if violated else 0)


if __name__ == "__main__":
    main()
