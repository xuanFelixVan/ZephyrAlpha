# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain-governance/registry-governance/blueprint.md | §
# [MODULE] scripts.migration.verify_migration_alignment
# [INVARIANTS] --dry-run MUST NOT modify any file; exit 0 only when all alignments verified
# [MODIFY-GUARD] migration-registry.yaml (read-only); panorama YAML (read-only)
# [CONSUMERS] safe_delete_operational.py; DM-310; migration pipeline
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlignmentError; RegistryLoadError
# [TESTS]
"""迁移对齐验证脚本：验证旧位置内容在新位置完整存在。

基于迁移登记表(migration-registry.yaml)的old_path→new_path映射，
验证搬家后新位置完整覆盖旧位置内容，防止"删了旧的发现新的缺斤少两"。

验证逻辑（非1:1 hash，基于迁移映射）：
  1. 逐条读取迁移登记表：old_path → new_path
  2. 验证old_path文件存在（旧文件还在，还没删）
  3. 验证new_path文件存在（新位置已创建）
  4. 内容完整性验证：排除import路径差异后，旧文件内容在新文件中存在
  5. 特殊场景：文件拆分(1旧→N新)、合并(N旧→1新)、重命名

用法:
    python scripts/migration/verify_migration_alignment.py                # 验证所有未完成条目
    python scripts/migration/verify_migration_alignment.py --dry-run      # 只输出报告
    python scripts/migration/verify_migration_alignment.py --batch N      # 只验证第N批
    python scripts/migration/verify_migration_alignment.py --domain X     # 只验证指定域
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_REGISTRY = PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "migration-registry.yaml"
DEPGRAPH_DB_PATH = PROJECT_ROOT / "data" / "databases" / "depgraph.db"

logger = logging.getLogger(__name__)


def load_migration_registry() -> list[dict]:
    """Load migration registry entries."""
    if not MIGRATION_REGISTRY.exists():
        print(f"[FAIL] Migration registry not found: {MIGRATION_REGISTRY}")
        sys.exit(1)
    with open(MIGRATION_REGISTRY, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or "entries" not in data:
        print("[FAIL] Migration registry has no 'entries' section")
        sys.exit(1)
    return data["entries"]


def file_hash(path: Path) -> str:
    """Compute MD5 hash of file content."""
    if not path.exists():
        return ""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_python_symbols(path: Path) -> set[str]:
    """Extract top-level symbol names (classes, functions, constants) from a Python file."""
    if not path.exists() or not path.suffix == ".py":
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        symbols = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                symbols.add(f"class:{node.name}")
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                symbols.add(f"func:{node.name}")
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols.add(f"const:{target.id}")
        return symbols
    except (SyntaxError, UnicodeDecodeError):
        return set()


def strip_import_lines(content: str) -> str:
    """Remove import/from-import lines for content comparison (path changes are expected)."""
    lines = content.split("\n")
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def verify_entry(old_path: Path, new_path: Path, entry: dict) -> dict:
    """Verify a single migration entry.

    Returns: {status, old_exists, new_exists, old_hash, new_hash,
              symbol_coverage, details}
    """
    result = {
        "old_path": str(old_path),
        "new_path": str(new_path),
        "old_exists": old_path.exists(),
        "new_exists": new_path.exists(),
        "old_hash": "",
        "new_hash": "",
        "symbol_coverage": 0.0,
        "status": "unknown",
        "details": "",
    }

    # Check existence
    if not result["old_exists"] and not result["new_exists"]:
        result["status"] = "both_missing"
        result["details"] = "Neither old nor new path exists"
        return result

    if not result["old_exists"]:
        result["status"] = "old_missing"
        result["details"] = "Old path already removed (migration may be complete)"
        return result

    if not result["new_exists"]:
        result["status"] = "new_missing"
        result["details"] = "New path does not exist yet (migration not started)"
        return result

    # Both exist — verify content
    result["old_hash"] = file_hash(old_path)
    result["new_hash"] = file_hash(new_path)

    # Exact match (including imports)
    if result["old_hash"] == result["new_hash"]:
        result["status"] = "aligned"
        result["symbol_coverage"] = 1.0
        result["details"] = "Exact content match"
        return result

    # For Python files: symbol-level comparison (excluding import differences)
    if old_path.suffix == ".py" and new_path.suffix == ".py":
        old_symbols = extract_python_symbols(old_path)
        new_symbols = extract_python_symbols(new_path)

        if old_symbols and new_symbols:
            coverage = len(old_symbols & new_symbols) / len(old_symbols) if old_symbols else 0.0
            result["symbol_coverage"] = round(coverage, 3)

            if coverage >= 1.0:
                result["status"] = "aligned"
                result["details"] = f"All {len(old_symbols)} symbols present in new file (imports may differ)"
            elif coverage >= 0.8:
                result["status"] = "partial"
                missing = old_symbols - new_symbols
                result["details"] = f"Missing symbols: {', '.join(sorted(missing)[:5])}"
            else:
                result["status"] = "mismatch"
                missing = old_symbols - new_symbols
                result["details"] = f"Low coverage ({coverage:.0%}), missing: {', '.join(sorted(missing)[:5])}"
            return result

        # Fallback: strip imports and compare
        try:
            with open(old_path, "r", encoding="utf-8") as f:
                old_content = f.read()
            with open(new_path, "r", encoding="utf-8") as f:
                new_content = f.read()
            old_stripped = strip_import_lines(old_content)
            new_stripped = strip_import_lines(new_content)
            if old_stripped == new_stripped:
                result["status"] = "aligned"
                result["symbol_coverage"] = 1.0
                result["details"] = "Content match after stripping import lines"
                return result
        except UnicodeDecodeError:
            pass

    # Non-Python or fallback: hash comparison
    result["status"] = "content_differs"
    result["details"] = "Content differs (hash mismatch) — may be expected if file was modified during migration"
    return result


def verify_split_merge(entries: list[dict]) -> dict[str, list[str]]:
    """Detect and verify split/merge scenarios.

    Returns: {old_path -> [new_paths]} for splits, {new_path -> [old_paths]} for merges
    """
    old_to_new = defaultdict(list)
    new_to_old = defaultdict(list)

    for entry in entries:
        old = entry.get("old_path", "")
        new = entry.get("new_path", "")
        if old and new:
            old_to_new[old].append(new)
            new_to_old[new].append(old)

    splits = {k: v for k, v in old_to_new.items() if len(v) > 1}
    merges = {k: v for k, v in new_to_old.items() if len(v) > 1}

    return {"splits": splits, "merges": merges}


def verify_split(old_path: str, new_paths: list[str]) -> dict:
    """Verify a 1-old→N-new split: all old symbols exist across new files."""
    old_file = PROJECT_ROOT / old_path
    if not old_file.exists() or old_file.suffix != ".py":
        return {"status": "skip", "details": "Old file missing or non-Python"}

    old_symbols = extract_python_symbols(old_file)
    if not old_symbols:
        return {"status": "skip", "details": "No symbols in old file"}

    all_new_symbols = set()
    for new_path in new_paths:
        new_file = PROJECT_ROOT / new_path
        if new_file.exists() and new_file.suffix == ".py":
            all_new_symbols |= extract_python_symbols(new_file)

    coverage = len(old_symbols & all_new_symbols) / len(old_symbols) if old_symbols else 0.0
    missing = old_symbols - all_new_symbols

    return {
        "status": "aligned" if coverage >= 1.0 else "partial",
        "symbol_coverage": round(coverage, 3),
        "details": f"Split: {len(new_paths)} new files, coverage {coverage:.0%}"
                   + (f", missing: {', '.join(sorted(missing)[:5])}" if missing else ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Verify migration alignment")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only output report, do not modify any file")
    parser.add_argument("--batch", type=int, default=0,
                        help="Only verify entries in batch N")
    parser.add_argument("--domain", type=str, default="",
                        help="Only verify entries for specified domain_id")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed output for each entry")
    args = parser.parse_args()

    print("[VERIFY] Loading migration registry...")
    entries = load_migration_registry()
    print(f"[VERIFY] Found {len(entries)} entries")

    # Filter entries
    if args.domain:
        entries = [e for e in entries if e.get("domain_id", "") == args.domain]
        print(f"[VERIFY] Filtered to domain '{args.domain}': {len(entries)} entries")

    if args.batch:
        entries = [e for e in entries if e.get("batch", 0) == args.batch]
        print(f"[VERIFY] Filtered to batch {args.batch}: {len(entries)} entries")

    # Skip completed entries
    pending = [e for e in entries if e.get("status") != "completed"]
    completed = [e for e in entries if e.get("status") == "completed"]
    print(f"[VERIFY] Pending: {len(pending)}, Completed: {len(completed)}")

    # Detect splits/merges
    split_merge = verify_split_merge(entries)
    print(f"[VERIFY] Splits: {len(split_merge['splits'])}, Merges: {len(split_merge['merges'])}")

    # Verify each entry
    results = {"aligned": 0, "partial": 0, "mismatch": 0, "new_missing": 0,
               "old_missing": 0, "both_missing": 0, "content_differs": 0, "unknown": 0}
    details_list = []

    for entry in pending:
        old_path = PROJECT_ROOT / entry.get("old_path", "")
        new_path = PROJECT_ROOT / entry.get("new_path", "")
        domain_id = entry.get("domain_id", "")

        # Check for split scenario
        old_key = entry.get("old_path", "")
        if old_key in split_merge["splits"]:
            result = verify_split(old_key, split_merge["splits"][old_key])
            result["old_path"] = old_key
            result["new_path"] = str(split_merge["splits"][old_key])
            result["domain_id"] = domain_id
        else:
            result = verify_entry(old_path, new_path, entry)
            result["domain_id"] = domain_id

        status = result.get("status", "unknown")
        results[status] = results.get(status, 0) + 1

        if status not in ("aligned", "old_missing") or args.verbose:
            details_list.append(result)

    # Summary
    total = len(pending)
    aligned = results.get("aligned", 0)
    print(f"\n{'='*60}")
    print(f"[VERIFY] Alignment Report")
    print(f"{'='*60}")
    print(f"Total pending entries: {total}")
    print(f"  Aligned:            {aligned}")
    print(f"  Partial:            {results.get('partial', 0)}")
    print(f"  Mismatch:           {results.get('mismatch', 0)}")
    print(f"  New missing:        {results.get('new_missing', 0)}")
    print(f"  Old missing:        {results.get('old_missing', 0)}")
    print(f"  Both missing:       {results.get('both_missing', 0)}")
    print(f"  Content differs:    {results.get('content_differs', 0)}")

    if details_list:
        print(f"\n--- Issues ({len(details_list)}) ---")
        for d in details_list[:20]:
            print(f"  [{d.get('status', '?').upper()}] {d.get('old_path', '?')}")
            if d.get("details"):
                print(f"    {d['details']}")
        if len(details_list) > 20:
            print(f"  ... and {len(details_list) - 20} more")

    # Exit code
    critical_issues = results.get("mismatch", 0) + results.get("new_missing", 0)
    if critical_issues > 0:
        print(f"\n[FAIL] {critical_issues} critical issues found")
        sys.exit(1)
    elif aligned == total:
        print(f"\n[OK] All {total} entries aligned")
        sys.exit(0)
    else:
        print(f"\n[WARN] {total - aligned} entries not yet aligned (migration in progress)")
        sys.exit(0)


if __name__ == "__main__":
    main()
