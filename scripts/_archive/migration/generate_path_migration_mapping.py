# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.8
# [MODULE] scripts.migration.generate_path_migration_mapping
# [INVARIANTS] 输出YAML格式; 数据源=depgraph.db; 每条mapping是单个文件(非目录); domain_group从path-tree补充; 同一源文件多模块声明用最具体优先; 目标路径冲突用模块名消歧
# [MODIFY-GUARD] mapping格式变更需同步STEP 6搬家脚本
# [CONSUMERS] STEP 6 execute_move.py; update_imports.py; verify_batch.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError:depgraph_or_path_tree -> exit 1; unresolvable_conflict -> exit 2
# [TESTS] tests/test_generate_path_migration_mapping.py
"""从 depgraph v3 domain draft 的 physical_files 生成文件级 path-migration-mapping.yaml。

核心策略:
  1. 文件级映射: 每条 mapping 是一个具体文件，不是目录
  2. 源文件去重: 同一 old_path 被多个模块声明时，physical_files 最少的模块优先(最具体声明)
  3. 目标消歧: 多个不同源文件映射到同一 target_path 时，用模块名作子目录消歧
  4. 排除: scripts/migration/ 和 data/asset_index/ 下的文件
  5. 不变标记: old_path == target_path 的文件标记为 unchanged

用法:
    python scripts/migration/generate_path_migration_mapping.py
    python scripts/migration/generate_path_migration_mapping.py --write
    python scripts/migration/generate_path_migration_mapping.py --validate
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPGRAPH_FILE = PROJECT_ROOT / "data" / "databases" / "depgraph.db"
PATH_TREE_FILE = PROJECT_ROOT / "data" / "asset_index" / "project-path-tree.yaml"
OUTPUT_FILE = PROJECT_ROOT / "data" / "asset_index" / "path-migration-mapping.yaml"

EXCLUDED_PREFIXES = [
    "scripts/migration/",
    "scripts\\migration\\",
    "data/asset_index/",
    "data\\asset_index\\",
]


def _load_yaml_safe(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed.", file=sys.stderr)
        sys.exit(2)
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print(f"[ERROR] Invalid YAML: {path}", file=sys.stderr)
        sys.exit(2)
    return data


def _build_domain_group_map(path_tree: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    domains_by_group = path_tree.get("domains_by_group", {})
    for group_key, group_domains in domains_by_group.items():
        if not isinstance(group_domains, list):
            continue
        for domain in group_domains:
            domain_id = domain.get("domain_id", "")
            if domain_id:
                result[domain_id] = group_key
    domains = path_tree.get("domains", [])
    if isinstance(domains, list):
        for domain in domains:
            domain_id = domain.get("domain_id", "")
            dg = domain.get("domain_group", "")
            if domain_id and dg:
                result[domain_id] = dg
    return result


def _build_domain_target_dir_map(path_tree: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    domains_by_group = path_tree.get("domains_by_group", {})
    for group_key, group_domains in domains_by_group.items():
        if not isinstance(group_domains, list):
            continue
        for domain in group_domains:
            domain_id = domain.get("domain_id", "")
            td = domain.get("target_directory", "")
            if domain_id and td:
                result[domain_id] = td.replace("\\", "/").rstrip("/") + "/"
    return result


def _is_excluded(filepath: str) -> bool:
    for prefix in EXCLUDED_PREFIXES:
        if prefix in filepath:
            return True
    return False


def _normalize_path(p: str) -> str:
    return p.replace("\\", "/").rstrip("/") + "/"


def _collect_raw_claims(depgraph: dict, domain_group_map: dict[str, str]) -> list[dict]:
    modules_section = depgraph.get("modules", {})
    if not modules_section:
        print("[ERROR] No 'modules' section in depgraph", file=sys.stderr)
        sys.exit(1)

    claims: list[dict] = []
    empty_pf_count = 0
    skipped_no_path = 0
    excluded_count = 0
    already_at_target_count = 0
    found_at_original_count = 0
    not_found_count = 0

    for domain_id, domain_data in modules_section.items():
        if not isinstance(domain_data, dict):
            continue
        items = domain_data.get("items", [])
        if not isinstance(items, list):
            continue

        for mod in items:
            if not isinstance(mod, dict):
                continue

            module_id = mod.get("module_id", "")
            mod_name = mod.get("name", "")
            mod_type = mod.get("type", "module")
            mod_path = mod.get("path", "")
            build_status = mod.get("build_status", "unknown")
            physical_files = mod.get("physical_files", [])

            if not isinstance(physical_files, list) or not physical_files:
                empty_pf_count += 1
                continue

            if not mod_path:
                skipped_no_path += 1
                continue

            target_dir = _normalize_path(mod_path)
            pf_count = len([pf for pf in physical_files if isinstance(pf, str) and pf.strip()])

            for pf in physical_files:
                if not isinstance(pf, str) or not pf.strip():
                    continue

                depgraph_path = pf.replace("\\", "/")

                if depgraph_path.endswith("/"):
                    continue

                if _is_excluded(depgraph_path):
                    excluded_count += 1
                    continue

                filename = os.path.basename(depgraph_path)
                if not filename or filename.startswith("#"):
                    continue
                target_path = target_dir + filename

                original_file = PROJECT_ROOT / depgraph_path
                target_file = PROJECT_ROOT / target_path

                if original_file.exists() and original_file.is_file():
                    old_path = depgraph_path
                    found_at_original_count += 1
                elif target_file.exists() and target_file.is_file():
                    old_path = target_path
                    already_at_target_count += 1
                else:
                    not_found_count += 1
                    continue

                change_type = "unchanged" if old_path == target_path else "moved"

                claims.append(
                    {
                        "old_path": old_path,
                        "target_path": target_path,
                        "type": mod_type,
                        "domain": domain_id,
                        "domain_group": domain_group_map.get(domain_id, ""),
                        "module_id": module_id,
                        "module_name": mod_name,
                        "build_status": build_status,
                        "pf_count": pf_count,
                        "target_dir": target_dir,
                        "change_type": change_type,
                    }
                )

    print(f"  Raw claims collected: {len(claims)}")
    print(f"  Found at original:   {found_at_original_count}")
    print(f"  Already at target:   {already_at_target_count}")
    print(f"  Not found on disk:   {not_found_count}")
    print(f"  Empty PF modules:    {empty_pf_count}")
    print(f"  No-path modules:     {skipped_no_path}")
    print(f"  Excluded files:      {excluded_count}")

    return claims


def _resolve_source_conflicts(claims: list[dict]) -> list[dict]:
    by_old_path: dict[str, list[dict]] = defaultdict(list)
    for c in claims:
        by_old_path[c["old_path"]].append(c)

    resolved: list[dict] = []
    conflict_count = 0

    for old_path, claim_list in by_old_path.items():
        if len(claim_list) == 1:
            resolved.append(claim_list[0])
            continue

        conflict_count += 1
        claim_list.sort(key=lambda c: (c["pf_count"], c["module_id"]))
        winner = claim_list[0]
        resolved.append(winner)

    print(f"  Source file conflicts resolved: {conflict_count} (kept most-specific claim)")
    return resolved


def _resolve_target_conflicts(claims: list[dict], domain_target_dir_map: dict[str, str]) -> list[dict]:
    by_target: dict[str, list[dict]] = defaultdict(list)
    for c in claims:
        by_target[c["target_path"]].append(c)

    resolved: list[dict] = []
    conflict_count = 0
    disambig_count = 0

    for target_path, claim_list in by_target.items():
        if len(claim_list) == 1:
            resolved.append(claim_list[0])
            continue

        conflict_count += 1
        domain_td = domain_target_dir_map.get(claim_list[0]["domain"], "")
        target_dir = claim_list[0]["target_dir"]

        needs_subdir = target_dir == domain_td or not domain_td

        if needs_subdir:
            for c in claim_list:
                mod_name = c["module_name"]
                filename = os.path.basename(c["old_path"])
                new_target = target_dir + mod_name + "/" + filename
                c["target_path"] = new_target
                c["disambiguated"] = True
            disambig_count += 1
        else:
            claim_list.sort(key=lambda c: (c["pf_count"], c["module_id"]))
            for i, c in enumerate(claim_list):
                if i > 0:
                    mod_name = c["module_name"]
                    filename = os.path.basename(c["old_path"])
                    new_target = target_dir + mod_name + "/" + filename
                    c["target_path"] = new_target
                    c["disambiguated"] = True
                    disambig_count += 1

        resolved.extend(claim_list)

    print(f"  Target path conflicts: {conflict_count} (disambiguated {disambig_count} with module_name subdir)")
    return resolved


def generate_file_level_mapping(depgraph: dict, path_tree: dict) -> dict:
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    domain_group_map = _build_domain_group_map(path_tree)
    domain_target_dir_map = _build_domain_target_dir_map(path_tree)

    print("=== Step 1: Collect raw claims ===")
    claims = _collect_raw_claims(depgraph, domain_group_map)

    print("\n=== Step 2: Resolve source file conflicts (same old_path) ===")
    claims = _resolve_source_conflicts(claims)

    print("\n=== Step 3: Resolve target path conflicts (same target_path) ===")
    claims = _resolve_target_conflicts(claims, domain_target_dir_map)

    print("\n=== Step 4: Final deduplication ===")
    seen_targets: dict[str, str] = {}
    final_claims: list[dict] = []
    for c in claims:
        tp = c["target_path"]
        if tp in seen_targets:
            if seen_targets[tp] != c["old_path"]:
                print(f"  [WARN] Still conflicting target: {tp} old1={seen_targets[tp]} old2={c['old_path']}")
                continue
        seen_targets[tp] = c["old_path"]
        final_claims.append(c)

    mappings: list[dict] = []
    moved_count = 0
    unchanged_count = 0

    for c in final_claims:
        old_path = c["old_path"]
        target_path = c["target_path"]

        if c.get("disambiguated") and old_path != target_path:
            change_type = "moved"
        else:
            change_type = c.get("change_type", "moved")

        if change_type == "unchanged":
            unchanged_count += 1
        else:
            change_type = "moved"
            moved_count += 1

        entry = {
            "old_path": old_path,
            "target_path": target_path,
            "type": c["type"],
            "domain": c["domain"],
            "domain_group": c["domain_group"],
            "module_id": c["module_id"],
            "module_name": c["module_name"],
            "build_status": c["build_status"],
            "change_type": change_type,
        }
        if c.get("disambiguated"):
            entry["disambiguated"] = True
        mappings.append(entry)

    result = {
        "meta": {
            "generated_at": now,
            "auto_generated_by": "scripts/migration/generate_path_migration_mapping.py",
            "data_source": "depgraph.db",
            "mapping_level": "file",
            "total_mappings": len(mappings),
            "moved_files": moved_count,
            "unchanged_files": unchanged_count,
        },
        "mappings": mappings,
    }

    return result


def validate_mapping(result: dict) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    mappings = result.get("mappings", [])

    old_paths = Counter()
    target_paths = Counter()
    for m in mappings:
        if m.get("change_type") == "unchanged":
            continue
        op = m.get("old_path", "")
        tp = m.get("target_path", "")
        old_paths[op] += 1
        target_paths[tp] += 1

    for op, count in old_paths.items():
        if count > 1:
            warnings.append(f"DUPLICATE_OLD_PATH: {op} appears {count} times")

    for tp, count in target_paths.items():
        if count > 1:
            errors.append(f"DUPLICATE_TARGET_PATH: {tp} appears {count} times")

    for m in mappings:
        if m.get("change_type") == "unchanged":
            continue
        op = m.get("old_path", "")
        tp = m.get("target_path", "")

        if op.endswith("/"):
            errors.append(f"DANGEROUS_DIRECTORY_MAPPING: old_path is directory: {op}")
        if tp.endswith("/"):
            errors.append(f"DANGEROUS_DIRECTORY_MAPPING: target_path is directory: {tp}")

    for m in mappings:
        op = m.get("old_path", "")
        for prefix in EXCLUDED_PREFIXES:
            clean = prefix.replace("\\", "/")
            if clean in op:
                errors.append(f"EXCLUDED_FILE_IN_MAPPING: {op}")
                break

    print("\n=== Validation Results ===")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("\n  ERRORS (first 20):")
        for e in errors[:20]:
            print(f"    {e}")
        if len(errors) > 20:
            print(f"    ... and {len(errors) - 20} more")

    if warnings:
        print("\n  WARNINGS (first 20):")
        for w in warnings[:20]:
            print(f"    {w}")
        if len(warnings) > 20:
            print(f"    ... and {len(warnings) - 20} more")

    if not errors and not warnings:
        print("  All checks passed!")

    return errors


def _mapping_to_yaml(result: dict) -> str:
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed.", file=sys.stderr)
        sys.exit(2)
    return yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _atomic_write(path: Path, content: str) -> None:
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate file-level path-migration-mapping.yaml from depgraph physical_files"
    )
    parser.add_argument("--write", action="store_true", help="Write output file")
    parser.add_argument("--validate", action="store_true", help="Validate mapping after generation")
    args = parser.parse_args()

    depgraph = _load_yaml_safe(DEPGRAPH_FILE)
    path_tree = _load_yaml_safe(PATH_TREE_FILE)

    result = generate_file_level_mapping(depgraph, path_tree)

    meta = result["meta"]
    print("\n=== Summary ===")
    print(f"  Total mappings:   {meta['total_mappings']}")
    print(f"  Moved files:      {meta['moved_files']}")
    print(f"  Unchanged files:  {meta['unchanged_files']}")

    if args.validate:
        errors = validate_mapping(result)
        if errors:
            print(f"\n[ABORT] {len(errors)} validation errors. Fix before writing.", file=sys.stderr)
            sys.exit(2)

    if args.write:
        yaml_str = _mapping_to_yaml(result)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(OUTPUT_FILE, yaml_str)
        print(f"\n[OK] Written to {OUTPUT_FILE}")
    else:
        print("\n(Dry run — use --write to save, --validate to check)")


if __name__ == "__main__":
    main()
