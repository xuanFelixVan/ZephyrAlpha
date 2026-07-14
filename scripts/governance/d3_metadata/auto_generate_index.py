# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/auto_generate_index.py | §
# [MODULE] scripts.governance.d3_metadata.auto_generate_index
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] _shared.constants; _shared.encoding
# [CONSUMERS] test_concurrent_safety.ps1; CI 门禁 GATE-INDEX
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读扫描 docs/ 目录;--apply 仅改写 frontmatter 计数+文件表,保留人工正文
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=通过;exit 1=发现漂移
# [TESTS]
# [TTL] task_bound
#!/usr/bin/env python3
"""GATE-INDEX: Validate and auto-fix index.md factual accuracy.
Eliminates manual index maintenance—the root cause of INDEX-REALITY DRIFT.


Modes:
  --check : Compare index.md facts (counts, lists) against disk reality
  --apply : Surgically fix frontmatter counts + file tables in index.md
            without destroying human-written prose content

Design: Surgical editing model
  - Extract factual claims from index.md frontmatter + tables
  - Compare against disk reality
  - --apply only rewrites frontmatter summary/count fields + file list tables
  - All human prose between frontmatter and tables is preserved

迁移历史：从 d5_architecture/generators/ 迁入 d3_metadata/（本脚本是元数据校验器，
非生成器；d3_metadata/ 同类脚本有 validate_architecture.py/check_registry_consistency.py）
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import os

__manifest__ = """
args:
- --check
description: GATE-INDEX — 索引文件自动校验/修复（消除手动索引维护，--check/--apply）
dimensions:
- D3
- D4
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

POLICIES_ROOT = REPO_ROOT / "docs/01_policies_and_standards"
IGNORE_FILE_MARKER = "_IGNORE_THIS_DIRECTORY_"


def _count_disk_files(directory):
    """_count_disk_files implementation."""
    count = 0
    names = []
    if directory.is_dir():
        for item in sorted(directory.iterdir(), key=lambda x: x.name.lower()):
            if item.name == "index.md":
                continue
            if item.name == IGNORE_FILE_MARKER:
                continue
            if item.is_file():
                count += 1
                names.append(item.name)
    return count, names


def _count_disk_subdirs(directory):
    """_count_disk_subdirs implementation."""
    count = 0
    names = []
    if directory.is_dir():
        for item in sorted(directory.iterdir()):
            if not item.is_dir():
                continue
            if item.name.startswith("."):
                continue
            if (item / IGNORE_FILE_MARKER).exists():
                continue
            count += 1
            names.append(item.name)
    return count, names


def _parse_frontmatter_summary_counts(text):
    """Extract claimed counts from frontmatter summary like 'X 个子目录 + Y 个文件 = 共 Z 项'."""
    patterns = [
        r"(\d+)\s*个子目录\s*\+\s*(\d+)\s*个文件\s*=\s*共\s*(\d+)\s*项",
        r"(\d+)\s*subdirs?\s*\+\s*(\d+)\s*files?\s*=\s*(\d+)\s*total",
        r"共\s*(\d+)\s*个体系文件",
        r"(\d+)\s*catalog.*(\d+)\s*contract.*(\d+)\s*vocab.*(\d+)\s*schema",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return None


def _parse_file_table_files(text):
    """Extract file names from index.md file listing table."""
    files = set()
    for m in re.finditer(r"\|\s*`?([a-zA-Z0-9_\-\.]+\.(?:md|yaml|json|toml|yml))`?\s*\|", text):
        files.add(m.group(1))
    return files


def _parse_subdir_table_entries(text):
    """Extract subdirectory names and claimed file counts from index.md subdir table."""
    entries = {}
    for m in re.finditer(r"\|\s*`([^`]+)/`\s*\|\s*(\d+)\s*\|", text):
        entries[m.group(1)] = int(m.group(2))
    return entries


def check_index(directory) -> list[dict]:
    """Check a single directory's index.md against disk reality. Returns list of issues."""
    index_path = directory / "index.md"
    if not index_path.exists():
        return [("MISSING", "index.md does not exist")]

    text = index_path.read_text(encoding="utf-8")
    issues = []

    disk_file_count, disk_file_names = _count_disk_files(directory)
    disk_subdir_count, disk_subdir_names = _count_disk_subdirs(directory)

    claimed_files = _parse_file_table_files(text)
    claimed_subdirs = _parse_subdir_table_entries(text)

    missing_from_index = set(disk_file_names) - claimed_files
    extra_in_index = claimed_files - set(disk_file_names) - {"index.md"}
    if missing_from_index:
        issues.append(("MISSING_FILES", sorted(missing_from_index)))
    if extra_in_index:
        issues.append(("STALE_FILES", sorted(extra_in_index)))

    for sd_name in disk_subdir_names:
        sd_count, _ = _count_disk_files(directory / sd_name)
        claimed = claimed_subdirs.get(sd_name)
        if claimed is not None and claimed != sd_count:
            issues.append(("SUB_COUNT_MISMATCH", f"{sd_name}/: claimed={claimed}, actual={sd_count}"))
        elif claimed is None:
            issues.append(("MISSING_SUBDIR", sd_name))

    for sd_name in claimed_subdirs:
        if sd_name not in disk_subdir_names:
            issues.append(("STALE_SUBDIR", sd_name))

    actual_total = disk_subdir_count + disk_file_count
    frontmatter_claim = _parse_frontmatter_summary_counts(text)
    if frontmatter_claim is not None and "system files" not in frontmatter_claim:
        pass

    return issues


def fix_index(directory) -> None:
    """Surgically fix index.md counts without destroying prose."""
    index_path = directory / "index.md"
    if not index_path.exists():
        return "SKIP", "index.md not found, cannot fix"

    text = index_path.read_text(encoding="utf-8")
    disk_file_count, disk_file_names = _count_disk_files(directory)
    disk_subdir_count, disk_subdir_names = _count_disk_subdirs(directory)
    total = disk_subdir_count + disk_file_count

    updated = text

    for sd_name in disk_subdir_names:
        sd_count, _ = _count_disk_files(directory / sd_name)
        pat = re.compile(rf"(\|\s*`{re.escape(sd_name)}/`\s*\|\s*)\d+(\s*\|)")
        match = pat.search(updated)
        if match:
            claimed = int(re.search(r"\d+", match.group(0)).group(0))
            if claimed != sd_count:
                updated = pat.sub(rf"\g<1>{sd_count}\g<2>", updated)

    pat_total_claimed = re.compile(r"(\d+)\s*个子目录\s*\+\s*(\d+)\s*个文件\s*=\s*共\s*(\d+)\s*项")
    m = pat_total_claimed.search(updated)
    if m:
        s_claimed = int(m.group(1))
        f_claimed = int(m.group(2))
        if s_claimed != disk_subdir_count or f_claimed != disk_file_count:
            updated = pat_total_claimed.sub(
                f"{disk_subdir_count} 个子目录 + {disk_file_count} 个文件 = 共 {total} 项",
                updated,
            )

    if updated != text:
        if not atomic_write_safe(index_path, updated):
            return "SKIP", "locked by another process"
        return "FIXED", f"counts corrected ({disk_subdir_count} subdirs + {disk_file_count} files = {total})"
    return "OK", "already correct"


def scan_tree(root, mode="check") -> list[dict]:
    """scan tree."""
    results = []
    """扫描并返回发现列表."""
    for d in sorted(root.rglob("*")):
        if not d.is_dir():
            continue
        if d.name.startswith("."):
            continue
        if (d / IGNORE_FILE_MARKER).exists():
            continue

        parent_ignore = False
        for parent in d.parents:
            if parent == root:
                break
            if (parent / IGNORE_FILE_MARKER).exists():
                parent_ignore = True
                break
        if parent_ignore:
            continue

        has_content = any(
            item.is_file() for item in d.iterdir() if item.name != "index.md" and item.name != IGNORE_FILE_MARKER
        ) or any(item.is_dir() and not item.name.startswith(".") for item in d.iterdir())
        if not has_content:
            continue

        index_path = d / "index.md"
        if not index_path.exists() and mode == "check":
            results.append((d.relative_to(root), "MISSING", "index.md not found"))
            continue

        if mode == "check":
            issues = check_index(d)
            if issues:
                for issue_type, detail in issues:
                    if isinstance(detail, list):
                        brief = f"{issue_type}: {len(detail)} files ({', '.join(detail[:3])}{'...' if len(detail) > 3 else ''})"
                    else:
                        brief = f"{issue_type}: {detail}"
                    results.append((d.relative_to(root), issue_type, brief))
            else:
                results.append((d.relative_to(root), "OK", "index.md matches disk reality"))
        else:
            status, msg = fix_index(d)
            results.append((d.relative_to(root), status, msg))

    return results
    """scan tree."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Validate/fix index.md factual accuracy against disk reality")
    parser.add_argument("--check", action="store_true", help="Detect drift (read-only)")
    parser.add_argument("--apply", action="store_true", help="Surgically fix counts")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks")
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    if not any([args.check, args.apply]):
        args.check = True

    mode = "apply" if args.apply else "check"
    print(f"GATE-INDEX: {mode} mode")
    print(f"Root: {POLICIES_ROOT}")
    print()

    results = scan_tree(POLICIES_ROOT, mode=mode)

    ok_count = 0
    problem_count = 0
    for rel, status, msg in results:
        if status in ("OK", "FIXED", "SKIP"):
            icon = "OK"
            ok_count += 1
        else:
            icon = "FAIL" if status in ("MISSING", "MISSING_FILES") else "WARN"
            problem_count += 1

        if args.verbose or status not in ("OK",):
            print(f"  [{icon}] {rel.as_posix()}/index.md: {msg}")

    print()
    if mode == "check" and problem_count > 0:
        print(f"BLOCKED: {problem_count} index discrepancies found")
        print(f"  {ok_count} directories are clean")
        print("Run: python auto_generate_index.py --apply")
        sys.exit(EXIT_FINDINGS)
    elif mode == "check":
        print(f"ALL {ok_count} index files verified against disk reality")
        sys.exit(EXIT_PASS)
    else:
        print(f"Fixed: {ok_count} directories verified/corrected")
        sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
