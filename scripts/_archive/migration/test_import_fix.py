# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.4
# [MODULE] scripts.migration.test_import_fix
# [INVARIANTS] 磁盘索引+后缀剥离+后缀匹配; 最长前缀替换; 原子写入; 并行
# [MODIFY-GUARD] 域目录结构变更需同步
# [CONSUMERS] TC-6-7 tests/ import修复
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无py文件->exit 0
# [TESTS] tests/test_test_import_fix.py
"""修复 tests/ 目录中的 import 引用。

策略:
  1. 构建磁盘模块索引
  2. 收集 tests/ 中所有无法解析的 import
  3. 三重匹配策略:
     a. 精确匹配（后缀剥离: core -> core_06）
     b. 后缀匹配（尾部 N 段匹配）
     c. 父目录匹配（同域目录下的同名文件）
  4. 最长前缀优先替换

用法:
    python scripts/migration/test_import_fix.py --dry-run
    python scripts/migration/test_import_fix.py
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZEPHYR_SRC = PROJECT_ROOT / "src" / "zephyr"
TESTS_DIR = PROJECT_ROOT / "tests"

EXCLUDED_DIRS = {"__pycache__", ".git", "integration/mcp_server"}
VERSION_SUFFIX_RE = re.compile(r"^(.+?)_\d+$")


def _build_disk_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for f in ZEPHYR_SRC.rglob("*.py"):
        if not f.is_file():
            continue
        rel_str = str(f.relative_to(ZEPHYR_SRC)).replace("\\", "/")
        skip = False
        for exc in EXCLUDED_DIRS:
            if exc in rel_str:
                skip = True
                break
        if skip or "__pycache__" in rel_str:
            continue
        parts = rel_str.split("/")
        parts[-1] = parts[-1][:-3]
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        mod_path = "zephyr." + ".".join(parts)
        index[mod_path] = rel_str
    return index


def _strip_version_suffix(mod_path: str) -> str:
    parts = mod_path.split(".")
    stripped = []
    for p in parts:
        m = VERSION_SUFFIX_RE.match(p)
        stripped.append(m.group(1) if m else p)
    return ".".join(stripped)


def _collect_missing_imports(disk_index: dict[str, str]) -> Counter:
    missing: Counter = Counter()
    for f in TESTS_DIR.rglob("*.py"):
        if not f.is_file() or "__pycache__" in str(f):
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in re.finditer(r"(?:from|import)\s+(zephyr\.\w+(?:\.\w+)*)", content):
            mod = m.group(1)
            if mod not in disk_index:
                missing[mod] += 1
    return missing


def _build_stripped_index(disk_index: dict[str, str]) -> dict[str, list[str]]:
    stripped_index: dict[str, list[str]] = {}
    for mod_path in disk_index:
        stripped = _strip_version_suffix(mod_path)
        if stripped not in stripped_index:
            stripped_index[stripped] = []
        stripped_index[stripped].append(mod_path)
    return stripped_index


def _build_filename_index(disk_index: dict[str, str]) -> dict[str, list[str]]:
    filename_index: dict[str, list[str]] = {}
    for mod_path in disk_index:
        parts = mod_path.split(".")
        if parts:
            fname = parts[-1]
            if fname not in filename_index:
                filename_index[fname] = []
            filename_index[fname].append(mod_path)
    return filename_index


def _suffix_match(missing_mod: str, disk_keys: list[str], min_score: int = 2) -> str | None:
    missing_parts = missing_mod.split(".")
    best_score = 0
    best_match = None
    for disk_mod in disk_keys:
        disk_parts = disk_mod.split(".")
        score = 0
        mi = len(missing_parts) - 1
        di = len(disk_parts) - 1
        while mi >= 0 and di >= 0:
            if missing_parts[mi] == disk_parts[di]:
                score += 1
                mi -= 1
                di -= 1
            else:
                break
        if score > best_score:
            best_score = score
            best_match = disk_mod
    if best_score >= min_score:
        return best_match
    return None


def _resolve_all(
    missing: Counter,
    disk_index: dict[str, str],
    stripped_index: dict[str, list[str]],
    filename_index: dict[str, list[str]],
) -> dict[str, str]:
    resolved: dict[str, str] = {}
    unresolved: list[tuple[str, int]] = []

    for mod, cnt in missing.items():
        if mod in disk_index:
            continue

        # Strategy A: exact match via version suffix stripping
        stripped = _strip_version_suffix(mod)
        if stripped in stripped_index:
            candidates = stripped_index[stripped]
            if len(candidates) == 1:
                resolved[mod] = candidates[0]
                continue
            best = max(candidates, key=lambda c: len(c))
            resolved[mod] = best
            continue

        # Strategy B: suffix match (trailing parts match)
        suffix_result = _suffix_match(mod, list(disk_index.keys()), min_score=2)
        if suffix_result:
            resolved[mod] = suffix_result
            continue

        # Strategy C: filename match in same domain
        parts = mod.split(".")
        if len(parts) >= 3:
            domain = parts[1]
            fname = parts[-1]
            if fname in filename_index:
                domain_candidates = [
                    c for c in filename_index[fname]
                    if domain in c
                ]
                if len(domain_candidates) == 1:
                    resolved[mod] = domain_candidates[0]
                    continue
                elif len(domain_candidates) > 1:
                    best = max(domain_candidates, key=lambda c: len(c))
                    resolved[mod] = best
                    continue

        unresolved.append((mod, cnt))

    return resolved, unresolved


def _build_prefix_mapping(module_mapping: dict[str, str]) -> list[tuple[str, str]]:
    return sorted(module_mapping.items(), key=lambda x: len(x[0]), reverse=True)


def _replace_imports_in_content(content: str, prefix_map: list[tuple[str, str]]) -> tuple[str, int]:
    changes = 0
    for old_mod, new_mod in prefix_map:
        if old_mod not in content:
            continue
        count = content.count(old_mod)
        if count > 0:
            content = content.replace(old_mod, new_mod)
            changes += count
    return content, changes


def _process_file(filepath: Path, prefix_map: list[tuple[str, str]], dry_run: bool = False) -> dict:
    rel = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"file": rel, "status": "read_error", "changes": 0}

    new_content, changes = _replace_imports_in_content(content, prefix_map)

    if changes == 0:
        return {"file": rel, "status": "no_change", "changes": 0}

    if dry_run:
        return {"file": rel, "status": "would_update", "changes": changes}

    tmp_path = f"{filepath}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(new_content, encoding="utf-8")
        os.replace(tmp_path, filepath)
        return {"file": rel, "status": "updated", "changes": changes}
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": rel, "status": "write_error", "changes": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix test import references")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--min-confidence", type=int, default=2, help="Min suffix match score")
    args = parser.parse_args()

    print("=== Test Import Fix ===")
    if args.dry_run:
        print("(dry-run mode)")

    print("\nStep 1: Building disk index...")
    disk_index = _build_disk_index()
    print(f"  Indexed {len(disk_index)} modules")

    print("\nStep 2: Collecting missing imports from tests/...")
    missing = _collect_missing_imports(disk_index)
    print(f"  Found {len(missing)} unique missing modules ({sum(missing.values())} occurrences)")

    if not missing:
        print("\nNo missing imports found. Exiting.")
        sys.exit(0)

    print("\nStep 3: Building auxiliary indexes...")
    stripped_index = _build_stripped_index(disk_index)
    filename_index = _build_filename_index(disk_index)
    print(f"  Stripped index: {len(stripped_index)} entries")
    print(f"  Filename index: {len(filename_index)} entries")

    print("\nStep 4: Resolving missing imports...")
    resolved, unresolved = _resolve_all(missing, disk_index, stripped_index, filename_index)
    print(f"  Resolved: {len(resolved)}")
    print(f"  Unresolved: {len(unresolved)}")

    if unresolved:
        total_unresolved = sum(cnt for _, cnt in unresolved)
        print(f"\n  Top unresolved (by frequency):")
        for mod, cnt in sorted(unresolved, key=lambda x: -x[1])[:20]:
            print(f"    {mod} ({cnt})")

    if not resolved:
        print("\nNo mappings to apply. Exiting.")
        sys.exit(0)

    prefix_map = _build_prefix_mapping(resolved)

    print(f"\nStep 5: Scanning tests/ .py files for replacements...")
    py_files: list[Path] = []
    if TESTS_DIR.exists():
        for f in TESTS_DIR.rglob("*.py"):
            if f.is_file() and "__pycache__" not in str(f):
                py_files.append(f)

    print(f"  Scanning {len(py_files)} .py files...")

    total_updated = 0
    total_changes = 0
    total_errors = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_process_file, f, prefix_map, args.dry_run): f for f in py_files}
        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                total_updated += 1
                total_changes += result["changes"]
            elif result["status"] == "write_error":
                total_errors += 1
                print(f"  ERROR: {result['file']}")

    print(f"\n=== Results ===")
    print(f"  Files updated: {total_updated}")
    print(f"  Import changes: {total_changes}")
    print(f"  Errors: {total_errors}")
    print(f"  Remaining unresolved: {len(unresolved)}")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
