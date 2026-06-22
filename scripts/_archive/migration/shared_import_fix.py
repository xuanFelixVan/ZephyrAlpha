# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.4
# [MODULE] scripts.migration.shared_import_fix
# [INVARIANTS] 从磁盘实际文件构建zephyr.shared.*映射; 最长前缀匹配; 原子写入; 并行
# [MODIFY-GUARD] shared目录结构变更需同步
# [CONSUMERS] TC-6-4 shared import修复
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无shared目录->exit 0
# [TESTS] tests/test_shared_import_fix.py
"""修复 zephyr.shared.* import 引用。

策略:
  1. 扫描 integration/shared_08/ 和 integration/shared/ 下的所有 .py 文件
  2. 推导旧模块路径 (zephyr.shared.xxx) 和新模块路径 (zephyr.integration.shared_08.xxx)
  3. 版本后缀映射: shared_08->shared, api_03->api, observability_02->observability, etc.
  4. 最长前缀优先匹配替换

用法:
    python scripts/migration/shared_import_fix.py --dry-run
    python scripts/migration/shared_import_fix.py
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZEPHYR_SRC = PROJECT_ROOT / "src" / "zephyr"

EXCLUDED_DIRS = {"__pycache__", ".git", "scripts/migration", "data/asset_index"}

VERSION_SUFFIX_RE = re.compile(r"^(.+?)_\d+$")


def _build_shared_mapping() -> dict[str, str]:
    mapping: dict[str, str] = {}

    shared_08_dir = ZEPHYR_SRC / "integration" / "shared_08"
    if shared_08_dir.exists():
        for f in shared_08_dir.rglob("*.py"):
            if not f.is_file() or "__pycache__" in str(f):
                continue
            rel = f.relative_to(shared_08_dir)
            parts = list(rel.parts)
            parts[-1] = parts[-1][:-3]
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                continue

            new_module = "zephyr.integration.shared_08." + ".".join(parts)
            old_parts = []
            for p in parts:
                m = VERSION_SUFFIX_RE.match(p)
                old_parts.append(m.group(1) if m else p)
            old_module = "zephyr.shared." + ".".join(old_parts)

            if old_module != new_module:
                mapping[old_module] = new_module

    shared_dir = ZEPHYR_SRC / "integration" / "shared"
    if shared_dir.exists():
        for f in shared_dir.rglob("*.py"):
            if not f.is_file() or "__pycache__" in str(f):
                continue
            rel = f.relative_to(shared_dir)
            parts = list(rel.parts)
            parts[-1] = parts[-1][:-3]
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                continue

            new_module = "zephyr.integration.shared." + ".".join(parts)
            old_parts = []
            for p in parts:
                m = VERSION_SUFFIX_RE.match(p)
                old_parts.append(m.group(1) if m else p)
            old_module = "zephyr.shared." + ".".join(old_parts)

            if old_module != new_module:
                if old_module not in mapping:
                    mapping[old_module] = new_module

    for domain in ["infrastructure.runtime_integration", "infra_ops"]:
        domain_shared = ZEPHYR_SRC / domain / "shared"
        if not domain_shared.exists():
            continue
        for f in domain_shared.rglob("*.py"):
            if not f.is_file() or "__pycache__" in str(f):
                continue
            rel = f.relative_to(domain_shared)
            parts = list(rel.parts)
            parts[-1] = parts[-1][:-3]
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                continue

            new_module = f"zephyr.{domain}.shared." + ".".join(parts)
            old_parts = []
            for p in parts:
                m = VERSION_SUFFIX_RE.match(p)
                old_parts.append(m.group(1) if m else p)
            old_module = "zephyr.shared." + ".".join(old_parts)

            if old_module != new_module:
                if old_module not in mapping:
                    mapping[old_module] = new_module

    return mapping


def _build_prefix_mapping(module_mapping: dict[str, str]) -> list[tuple[str, str]]:
    items = sorted(module_mapping.items(), key=lambda x: len(x[0]), reverse=True)
    return items


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
    for exc in EXCLUDED_DIRS:
        if exc in rel:
            return {"file": rel, "status": "excluded", "changes": 0}

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
    parser = argparse.ArgumentParser(description="Fix zephyr.shared.* import references")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual changes")
    args = parser.parse_args()

    print("=== Shared Import Fix ===")
    if args.dry_run:
        print("(dry-run mode)")

    module_mapping = _build_shared_mapping()
    print(f"Module path mappings: {len(module_mapping)}")

    sample_count = 0
    for old_mod, new_mod in sorted(module_mapping.items()):
        if sample_count < 30:
            print(f"  {old_mod} -> {new_mod}")
            sample_count += 1
    if len(module_mapping) > 30:
        print(f"  ... and {len(module_mapping) - 30} more")

    prefix_map = _build_prefix_mapping(module_mapping)

    py_files: list[Path] = []
    scan_dirs = [ZEPHYR_SRC, PROJECT_ROOT / "tests"]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob("*.py"):
            if f.is_file() and "__pycache__" not in str(f):
                py_files.append(f)

    print(f"\nScanning {len(py_files)} .py files...")

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

    print("\n=== Results ===")
    print(f"  Files updated: {total_updated}")
    print(f"  Import changes: {total_changes}")
    print(f"  Errors: {total_errors}")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
