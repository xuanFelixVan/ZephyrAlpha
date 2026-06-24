# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md | §6.4
# [MODULE] scripts.migration.comprehensive_import_fix
# [INVARIANTS] 从path-migration-mapping.yaml构建old->new模块路径映射; 最长前缀匹配; 排除根包zephyr; 原子写入(RULE-ONE); 并行(RULE-SEVEN)
# [MODIFY-GUARD] 映射逻辑变更需同步mapping格式
# [CONSUMERS] TC-6-4 import全面修复
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] mapping缺失->exit 1
# [TESTS] tests/test_comprehensive_import_fix.py
"""从 path-migration-mapping.yaml 构建全面的 old→new 模块路径映射，修复所有 .py 文件的 import。

策略:
  1. 从 path-migration-mapping.yaml 的 moved 文件提取 old_dir→new_dir 映射
  2. 转换为 Python 模块路径映射 (zephyr.xxx -> zephyr.yyy.zzz)
  3. 过滤: 排除根包 zephyr; 要求至少2级深度(zephyr.xxx)
  4. 最长前缀优先匹配替换
  5. 排除 scripts/migration/ 和 data/asset_index/

用法:
    python scripts/migration/comprehensive_import_fix.py --dry-run
    python scripts/migration/comprehensive_import_fix.py
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING_FILE = PROJECT_ROOT / "data" / "asset_index" / "path-migration-mapping.yaml"

EXCLUDED_DIRS = {"__pycache__", ".git", "scripts/migration", "data/asset_index"}


def _load_yaml_safe(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed.", file=sys.stderr)
        sys.exit(2)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _dir_to_python_module(dir_path: str) -> str:
    p = dir_path.replace("\\", "/").rstrip("/")
    if p.startswith("src/"):
        p = p[4:]
    parts = p.split("/")
    if parts and parts[0] == "zephyr":
        return ".".join(parts)
    return ""


def _build_module_path_mapping(mapping_data: dict) -> dict[str, str]:
    mappings = mapping_data.get("mappings", [])
    dir_votes: dict[str, Counter] = defaultdict(Counter)

    for m in mappings:
        if m.get("change_type") != "moved":
            continue
        op = m.get("old_path", "")
        tp = m.get("target_path", "")
        if not op or not tp:
            continue

        old_dir = op.rsplit("/", 1)[0] if "/" in op else ""
        new_dir = tp.rsplit("/", 1)[0] if "/" in tp else ""

        if not old_dir or not new_dir or old_dir == new_dir:
            continue

        old_module = _dir_to_python_module(old_dir)
        new_module = _dir_to_python_module(new_dir)

        if not old_module or not new_module:
            continue
        if old_module == "zephyr":
            continue
        parts = old_module.split(".")
        if len(parts) < 2:
            continue

        dir_votes[old_module][new_module] += 1

    result: dict[str, str] = {}
    for old_mod, votes in dir_votes.items():
        best_new = votes.most_common(1)[0][0]
        total = sum(votes.values())
        best_count = votes[best_new]
        confidence = best_count / total if total > 0 else 0

        if confidence < 0.5:
            top2 = votes.most_common(2)
            print(f"  [SKIP] Ambiguous: {old_mod} -> {top2} (confidence {confidence:.0%})")
            continue

        if " " in best_new or "(" in best_new or ")" in best_new:
            print(f"  [SKIP] Invalid chars in target: {old_mod} -> {best_new}")
            continue

        if ".src." in best_new or best_new.endswith(".src") or ".src.zephyr" in best_new:
            print(f"  [SKIP] Unnormalized path: {old_mod} -> {best_new}")
            continue

        result[old_mod] = best_new

    return result


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
    parser = argparse.ArgumentParser(description="Comprehensive import fix from path-migration-mapping")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual changes")
    parser.add_argument("--scope", choices=["src", "scripts", "all"], default="src", help="Which directories to scan")
    args = parser.parse_args()

    print("=== Comprehensive Import Fix ===")
    if args.dry_run:
        print("(dry-run mode)")

    mapping_data = _load_yaml_safe(MAPPING_FILE)
    module_mapping = _build_module_path_mapping(mapping_data)
    print(f"Module path mappings: {len(module_mapping)}")

    for old_mod, new_mod in sorted(module_mapping.items()):
        print(f"  {old_mod} -> {new_mod}")

    prefix_map = _build_prefix_mapping(module_mapping)

    scan_dirs: list[Path] = []
    if args.scope in ("src", "all"):
        scan_dirs.append(PROJECT_ROOT / "src" / "zephyr")
    if args.scope in ("scripts", "all"):
        scan_dirs.append(PROJECT_ROOT / "scripts")
    if args.scope in ("tests", "all"):
        scan_dirs.append(PROJECT_ROOT / "tests")

    py_files: list[Path] = []
    for d in scan_dirs:
        if d.exists():
            for f in d.rglob("*.py"):
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
