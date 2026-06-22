# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.4
# [MODULE] scripts.migration.domain_prefix_import_fix
# [INVARIANTS] 从域目录结构推导old->new模块路径映射; 域前缀插入; 原子写入; 并行
# [MODIFY-GUARD] 域目录变更需同步
# [CONSUMERS] TC-6-4 import域前缀修复
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无域目录->exit 0
# [TESTS] tests/test_domain_prefix_import_fix.py
"""从域目录结构推导 old→new 模块路径映射，修复 import 的域前缀。

策略:
  1. 扫描 src/zephyr/ 下的域目录 (autonomy_core, governance, etc.)
  2. 对每个域目录下的子目录，推导旧模块路径 (zephyr.subdir -> zephyr.domain.subdir)
  3. 验证映射: 旧路径不存在但新路径存在
  4. 应用到所有 .py 文件的 import 语句

用法:
    python scripts/migration/domain_prefix_import_fix.py --dry-run
    python scripts/migration/domain_prefix_import_fix.py
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ZEPHYR_SRC = PROJECT_ROOT / "src" / "zephyr"

EXCLUDED_DIRS = {"__pycache__", ".git", "scripts/migration", "data/asset_index", "integration"}

DOMAIN_DIRS = [
    "autonomy_core",
    "autonomy_perm",
    "infrastructure.runtime_integration",
    "infra_ops",
    "security",
    "governance",
    "ops",
    "data",
    "alt_data",
    "factor",
    "signal",
    "pf_core",
    "pf_alloc",
    "ex_core",
    "risk",
    "ml_train",
    "ml_serve",
    "cross_asset",
    "compliance",
    "trading",
    "simulation",
    "research",
    "knowledge",
]


def _build_domain_prefix_mapping() -> dict[str, str]:
    mapping: dict[str, str] = {}
    ambiguous: dict[str, list[str]] = {}

    for domain in DOMAIN_DIRS:
        domain_dir = ZEPHYR_SRC / domain
        if not domain_dir.exists() or not domain_dir.is_dir():
            continue

        for child in sorted(domain_dir.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith("_") or child.name.startswith("."):
                continue
            if "__pycache__" in child.name:
                continue
            if " " in child.name or "(" in child.name or ")" in child.name:
                continue

            old_module = f"zephyr.{child.name}"
            new_module = f"zephyr.{domain}.{child.name}"

            old_dir = ZEPHYR_SRC / child.name
            if old_dir.exists() and old_dir.is_dir():
                py_files = list(old_dir.glob("*.py"))
                if py_files:
                    continue

            if old_module not in ambiguous:
                ambiguous[old_module] = []
            ambiguous[old_module].append(new_module)

            for grandchild in sorted(child.rglob("*.py")):
                if not grandchild.is_file() or "__pycache__" in str(grandchild):
                    continue
                rel = grandchild.relative_to(child)
                parts = list(rel.parts)
                parts[-1] = parts[-1][:-3]
                if parts[-1] == "__init__":
                    parts = parts[:-1]
                if not parts:
                    continue

                sub_module = ".".join(parts)
                if " " in sub_module or "(" in sub_module or ")" in sub_module:
                    continue
                old_sub = f"zephyr.{child.name}.{sub_module}"
                new_sub = f"zephyr.{domain}.{child.name}.{sub_module}"

                old_sub_path = (
                    ZEPHYR_SRC / child.name / "/".join(parts[:-1]) if len(parts) > 1 else ZEPHYR_SRC / child.name
                )
                if old_sub_path.exists() and any(old_sub_path.glob("*.py")):
                    continue

                if old_sub not in ambiguous:
                    ambiguous[old_sub] = []
                ambiguous[old_sub].append(new_sub)

    for old_mod, new_mods in ambiguous.items():
        if len(new_mods) == 1:
            mapping[old_mod] = new_mods[0]
        else:
            from collections import Counter

            counts = Counter(new_mods)
            best, count = counts.most_common(1)[0]
            if count > 1 and count / len(new_mods) >= 0.5:
                mapping[old_mod] = best
            else:
                print(f"  [SKIP] Ambiguous: {old_mod} -> {new_mods[:3]}")

    filtered: dict[str, str] = {}
    for old_mod, new_mod in mapping.items():
        if ".src." in new_mod or new_mod.endswith(".src"):
            print(f"  [SKIP] Unnormalized: {old_mod} -> {new_mod}")
            continue
        if old_mod == "zephyr.shared" and new_mod != "zephyr.shared":
            print(f"  [SKIP] Cross-domain package: {old_mod} (would map to {new_mod})")
            continue
        filtered[old_mod] = new_mod

    return filtered


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
    parser = argparse.ArgumentParser(description="Fix domain prefix in imports")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual changes")
    args = parser.parse_args()

    print("=== Domain Prefix Import Fix ===")
    if args.dry_run:
        print("(dry-run mode)")

    module_mapping = _build_domain_prefix_mapping()
    print(f"Module path mappings: {len(module_mapping)}")

    for old_mod, new_mod in sorted(module_mapping.items()):
        print(f"  {old_mod} -> {new_mod}")

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
