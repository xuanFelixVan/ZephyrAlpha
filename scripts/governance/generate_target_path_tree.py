# [BLUEPRINT] GOV-074 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §2.1
# [MODULE] scripts.governance.generate_target_path_tree
# [INVARIANTS] 输出MUST覆盖35域; 每个模块MUST有target_path; target_path MUST按ssot_path推导
# [MODIFY-GUARD] target-path-tree.yaml结构变更需同步panorama/depgraph
# [CONSUMERS] DM-107; 迁移执行脚本; depgraph对齐验证
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DepgraphLoadError; PanoramaLoadError; MigrationRegistryLoadError
# [TESTS]
"""从最新depgraph重新生成target-path-tree.yaml全量目标路径树。

DM-107: 确保模块的path字段与35域新命名规则对齐。

核心逻辑:
  1. 从depgraph读取所有模块节点（含domain_id, path, type等）
  2. 从panorama读取35域定义（domain_id→ssot_path映射）
  3. 从migration-registry读取旧路径→新路径映射
  4. 对每个模块计算target_path:
     - 有migration entry → 使用new_path + subdomain_id
     - 无migration entry → 通过路径前缀匹配35子域ssot_path推导
  5. 生成树形结构输出到target-path-tree.yaml

用法:
    python scripts/governance/generate_target_path_tree.py            # stdout
    python scripts/governance/generate_target_path_tree.py --write    # 写入文件
    python scripts/governance/generate_target_path_tree.py --check    # 验证对齐
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import yaml

try:
    from yaml import CLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader as SafeLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPGRAPH_PATH = PROJECT_ROOT / "data" / "databases" / "depgraph.db"
PANORAMA_PATH = PROJECT_ROOT / "data" / "databases" / "depgraph.db"
MIGRATION_REGISTRY_PATH = PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "migration-registry.yaml"
FUNC_DOMAIN_REGISTRY_PATH = (
    PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "functional-domain-registry.yaml"
)
OUTPUT_PATH = PROJECT_ROOT / "data" / "asset_index" / "target-path-tree.yaml"


def load_yaml(path: Path) -> dict:
    """Load YAML file with error handling."""
    if not path.exists():
        print(f"[FAIL] File not found: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=SafeLoader) or {}


def load_depgraph_from_db(db_path: Path) -> dict:
    """Load depgraph from SQLite DB, returning YAML-compatible dict."""
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    data = {"nodes": {}, "edges": [], "metadata": {}}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = node.pop("node_id")
        node["type"] = node.pop("node_type", "")
        data["nodes"][nid] = node
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        edge["from"] = edge.pop("from_node", "")
        edge["to"] = edge.pop("to_node", "")
        data["edges"].append(edge)
    conn.close()
    return data


def load_panorama_from_db(db_path: Path) -> dict:
    """Load panorama from SQLite DB arch_ tables, returning YAML-compatible dict."""
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    data = {"domains": {}}
    # Load domains from arch_path_mappings (has ssot_path, domain_id)
    for row in conn.execute("SELECT * FROM arch_path_mappings"):
        entry = dict(row)
        did = entry.get("domain_id", "")
        path_pattern = entry.get("path_pattern", "")
        state = entry.get("state", "design")
        if did not in data["domains"]:
            data["domains"][did] = {
                "domain_id": did,
                "ssot_path": path_pattern,
                "parent_domain": "",
                "change_policy": "evolving",
                "modification_permission": "ai_modifiable",
                "state": state,
            }
        else:
            if not data["domains"][did].get("ssot_path"):
                data["domains"][did]["ssot_path"] = path_pattern
    # Enrich from domains table
    for row in conn.execute("SELECT * FROM domains"):
        entry = dict(row)
        did = entry.pop("domain_id", "")
        if did not in data["domains"]:
            data["domains"][did] = {
                "domain_id": did,
                "ssot_path": entry.get("ssot_path", ""),
                "parent_domain": entry.get("domain_group", ""),
                "change_policy": "evolving",
                "modification_permission": "ai_modifiable",
            }
        else:
            if entry.get("ssot_path") and not data["domains"][did].get("ssot_path"):
                data["domains"][did]["ssot_path"] = entry["ssot_path"]
            if entry.get("domain_group"):
                data["domains"][did]["parent_domain"] = entry["domain_group"]
    # v6: arch_domain_capacity已合并入domains，capacity字段已在domains中
    # domains表已含 current_modules/max_modules/growth_pattern/target_modules/feasibility/bottleneck_description/last_capacity_check
    conn.close()
    return data


def build_domain_ssot_map(panorama: dict, func_reg: dict) -> dict:
    """Build subdomain_id → {ssot_path, parent_domain, ...} mapping."""
    domain_map = {}

    for dname, dval in panorama.get("domains", {}).items():
        if not isinstance(dval, dict):
            continue
        subdomain_id = dval.get("domain_id", dname)
        domain_map[subdomain_id] = {
            "ssot_path": dval.get("ssot_path", "").replace("\\", "/").rstrip("/") + "/",
            "parent_domain": dval.get("parent_domain", ""),
            "change_policy": dval.get("change_policy", dval.get("stability", "evolving")),
            "modification_permission": dval.get("modification_permission", dval.get("ai_autonomy", "ai_modifiable")),
        }

    for entry in func_reg.get("entries", []):
        subdomain = entry.get("subdomain", "")
        if subdomain and subdomain not in domain_map:
            domain_map[subdomain] = {
                "ssot_path": entry.get("ssot_path", "").replace("\\", "/").rstrip("/") + "/",
                "parent_domain": entry.get("domain", ""),
                "stability": entry.get("stability", "evolving"),
                "ai_autonomy": entry.get("ai_autonomy", "ai_modifiable"),
            }

    return domain_map


def build_migration_map(migration_reg: dict) -> dict:
    """Build old_path → {new_path, domain_id, subdomain_id, status} mapping."""
    migration_map = {}
    for entry in migration_reg.get("entries", []):
        old_path = entry.get("old_path", "").replace("\\", "/")
        if not old_path:
            continue
        migration_map[old_path] = {
            "new_path": entry.get("new_path", "").replace("\\", "/"),
            "domain_id": entry.get("domain_id", ""),
            "subdomain_id": entry.get("subdomain_id", ""),
            "status": entry.get("status", "pending"),
        }
    return migration_map


def build_path_prefix_to_subdomain(domain_ssot_map: dict) -> dict:
    """Build path prefix → subdomain_id mapping from ssot_path values."""
    prefix_map = {}
    for subdomain_id, info in domain_ssot_map.items():
        ssot_path = info.get("ssot_path", "")
        if ssot_path and ssot_path != "/":
            prefix_map[ssot_path] = subdomain_id
    return dict(sorted(prefix_map.items(), key=lambda x: len(x[0]), reverse=True))


def build_old_path_prefix_to_subdomain(migration_map: dict) -> dict:
    """Build old path prefix → subdomain_id mapping from migration registry."""
    prefix_subdomain = defaultdict(lambda: defaultdict(int))

    for old_path, entry in migration_map.items():
        subdomain = entry.get("subdomain_id", "")
        if not subdomain or not old_path:
            continue
        if "/" in old_path:
            dir_prefix = old_path.rsplit("/", 1)[0] + "/"
            prefix_subdomain[dir_prefix][subdomain] += 1

    result = {}
    for prefix, subdomain_counts in prefix_subdomain.items():
        best_subdomain = max(subdomain_counts, key=subdomain_counts.get)
        result[prefix] = best_subdomain

    return dict(sorted(result.items(), key=lambda x: len(x[0]), reverse=True))


def build_depgraph_domain_to_subdomain(migration_map: dict, depgraph_nodes: dict) -> dict:
    """Build depgraph domain_id → subdomain_id count mapping."""
    domain_subdomain = defaultdict(lambda: defaultdict(int))

    for old_path, entry in migration_map.items():
        domain_id = entry.get("domain_id", "")
        subdomain = entry.get("subdomain_id", "")
        if domain_id and subdomain:
            domain_subdomain[domain_id][subdomain] += 1

    result = {}
    for domain_id, subdomain_counts in domain_subdomain.items():
        result[domain_id] = dict(subdomain_counts)

    return result


def derive_subdomain_from_path(current_path: str, path_prefix_map: dict, old_prefix_map: dict) -> str:
    """Derive subdomain_id from current path by matching prefixes."""
    norm_path = current_path.replace("\\", "/") + "/"

    for prefix, subdomain_id in path_prefix_map.items():
        if norm_path.startswith(prefix):
            return subdomain_id

    for prefix, subdomain_id in old_prefix_map.items():
        if norm_path.startswith(prefix):
            return subdomain_id

    return ""


def derive_target_path(
    current_path: str,
    subdomain_id: str,
    domain_ssot_map: dict,
    migration_map: dict,
    path_prefix_map: dict,
    old_prefix_map: dict,
    depgraph_domain_id: str,
    domain_to_subdomain: dict,
) -> tuple[str, str, str]:
    """Derive target path for a module based on 35-domain naming rules.

    Priority:
      1. Migration registry entry
      2. Path prefix match to subdomain ssot_path
      3. depgraph domain_id → subdomain mapping
      4. Keep as-is

    Returns: (target_path, resolved_subdomain_id, resolved_parent_domain)
    """
    norm_path = current_path.replace("\\", "/")

    # Priority 1: Check migration registry
    if norm_path in migration_map:
        entry = migration_map[norm_path]
        new_path = entry.get("new_path", "")
        subdomain = entry.get("subdomain_id", "")
        if new_path:
            parent = domain_ssot_map.get(subdomain, {}).get("parent_domain", "")
            return new_path, subdomain, parent

    # Priority 2: Path prefix match to subdomain
    if not subdomain_id:
        subdomain_id = derive_subdomain_from_path(norm_path, path_prefix_map, old_prefix_map)

    # Priority 3: depgraph domain_id → subdomain mapping
    if not subdomain_id and depgraph_domain_id:
        subdomain_map = domain_to_subdomain.get(depgraph_domain_id, {})
        if subdomain_map:
            subdomain_id = max(subdomain_map, key=subdomain_map.get)

    if subdomain_id and subdomain_id in domain_ssot_map:
        domain_info = domain_ssot_map[subdomain_id]
        ssot_path = domain_info["ssot_path"]
        parent_domain = domain_info.get("parent_domain", "")

        if ssot_path and ssot_path != "/" and norm_path.startswith("src/zephyr/"):
            if norm_path.startswith(ssot_path):
                return norm_path, subdomain_id, parent_domain
            filename = norm_path.rsplit("/", 1)[-1]
            target = ssot_path + filename
            return target, subdomain_id, parent_domain

    # Priority 4: Keep as-is
    if subdomain_id:
        parent = domain_ssot_map.get(subdomain_id, {}).get("parent_domain", "")
        return norm_path, subdomain_id, parent

    return norm_path, "", ""


def build_target_tree(depgraph: dict, domain_ssot_map: dict, migration_map: dict) -> tuple:
    """Build the full target path tree from depgraph nodes."""
    nodes = depgraph.get("nodes", {})
    path_prefix_map = build_path_prefix_to_subdomain(domain_ssot_map)
    old_prefix_map = build_old_path_prefix_to_subdomain(migration_map)
    domain_to_subdomain = build_depgraph_domain_to_subdomain(migration_map, nodes)

    subdomain_modules = defaultdict(list)
    all_modules = []

    for nid, node in nodes.items():
        ntype = node.get("type", "")
        if ntype not in ("module", "script", "config", "registry", "contract", "schema", "data"):
            continue

        current_path = node.get("path", "")
        depgraph_domain_id = node.get("domain_id", "")
        if not current_path:
            continue

        initial_subdomain = derive_subdomain_from_path(current_path, path_prefix_map, old_prefix_map)

        target_path, resolved_subdomain, resolved_parent = derive_target_path(
            current_path,
            initial_subdomain,
            domain_ssot_map,
            migration_map,
            path_prefix_map,
            old_prefix_map,
            depgraph_domain_id,
            domain_to_subdomain,
        )

        module_entry = {
            "current_path": current_path,
            "target_path": target_path,
            "subdomain_id": resolved_subdomain,
            "parent_domain": resolved_parent,
            "type": ntype,
            "blueprint_id": node.get("blueprint_id", ""),
            "architecture_layer": node.get("architecture_layer", ""),
            "lifecycle": node.get("deployment_lifecycle", "operational"),
            "needs_migration": current_path.replace("\\", "/") != target_path,
        }

        subdomain_modules[resolved_subdomain].append(module_entry)
        all_modules.append(module_entry)

    return subdomain_modules, all_modules


def generate_yaml_output(
    subdomain_modules: dict, all_modules: list, domain_ssot_map: dict, depgraph_meta: dict
) -> dict:
    """Generate the YAML structure for target-path-tree.yaml."""
    domains_output = {}

    # All 35 domains from ssot_map (even if no modules yet)
    for subdomain_id in sorted(domain_ssot_map.keys()):
        domain_info = domain_ssot_map[subdomain_id]
        modules = subdomain_modules.get(subdomain_id, [])
        domains_output[subdomain_id] = {
            "parent_domain": domain_info.get("parent_domain", ""),
            "ssot_path": domain_info.get("ssot_path", ""),
            "change_policy": domain_info.get("change_policy", domain_info.get("stability", "evolving")),
            "modification_permission": domain_info.get(
                "modification_permission", domain_info.get("ai_autonomy", "ai_modifiable")
            ),
            "module_count": len(modules),
            "needs_migration_count": sum(1 for m in modules if m.get("needs_migration")),
            "modules": [
                {
                    "current_path": m["current_path"],
                    "target_path": m["target_path"],
                    "type": m["type"],
                    "blueprint_id": m.get("blueprint_id", ""),
                    "architecture_layer": m.get("architecture_layer", ""),
                    "needs_migration": m.get("needs_migration", False),
                }
                for m in sorted(modules, key=lambda x: x["target_path"])
            ],
        }

    # Unmapped subdomains with modules
    for subdomain_id in sorted(subdomain_modules.keys()):
        if subdomain_id and subdomain_id not in domains_output:
            modules = subdomain_modules[subdomain_id]
            domains_output[subdomain_id] = {
                "parent_domain": "",
                "ssot_path": "",
                "change_policy": "evolving",
                "modification_permission": "ai_modifiable",
                "module_count": len(modules),
                "needs_migration_count": sum(1 for m in modules if m.get("needs_migration")),
                "modules": [
                    {
                        "current_path": m["current_path"],
                        "target_path": m["target_path"],
                        "type": m["type"],
                        "blueprint_id": m.get("blueprint_id", ""),
                        "architecture_layer": m.get("architecture_layer", ""),
                        "needs_migration": m.get("needs_migration", False),
                    }
                    for m in sorted(modules, key=lambda x: x["target_path"])
                ],
            }

    # Unclassified modules
    empty_subdomain_mods = subdomain_modules.get("", [])
    if empty_subdomain_mods:
        domains_output["_unclassified"] = {
            "parent_domain": "",
            "ssot_path": "",
            "change_policy": "volatile",
            "modification_permission": "ai_modifiable",
            "module_count": len(empty_subdomain_mods),
            "needs_migration_count": sum(1 for m in empty_subdomain_mods if m.get("needs_migration")),
            "modules": [
                {
                    "current_path": m["current_path"],
                    "target_path": m["target_path"],
                    "type": m["type"],
                    "blueprint_id": m.get("blueprint_id", ""),
                    "architecture_layer": m.get("architecture_layer", ""),
                    "needs_migration": m.get("needs_migration", False),
                }
                for m in sorted(empty_subdomain_mods, key=lambda x: x["target_path"])
            ],
        }

    tree = build_directory_tree(all_modules)

    total_modules = len(all_modules)
    needs_migration = sum(1 for m in all_modules if m.get("needs_migration"))
    subdomain_coverage = len(set(m["subdomain_id"] for m in all_modules if m["subdomain_id"]))
    empty_subdomain = sum(1 for m in all_modules if not m.get("subdomain_id"))

    output = {
        "meta": {
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "auto_generated_by": "scripts/governance/generate_target_path_tree.py",
            "task_id": "DM-107",
            "source_depgraph": "data/databases/depgraph.db",
            "source_panorama": "data/databases/depgraph.db",
            "source_migration_registry": "docs/02_enterprise_architecture/migration-registry.yaml",
            "depgraph_version": depgraph_meta.get("version", ""),
            "depgraph_generated_at": depgraph_meta.get("generated_at", ""),
            "total_modules": total_modules,
            "total_subdomains": len(domains_output),
            "subdomain_coverage": subdomain_coverage,
            "empty_subdomain_count": empty_subdomain,
            "needs_migration_count": needs_migration,
            "aligned_count": total_modules - needs_migration,
            "alignment_rate": f"{(total_modules - needs_migration) / total_modules * 100:.1f}%"
            if total_modules
            else "0%",
        },
        "domains": domains_output,
        "tree": tree,
    }

    return output


def build_directory_tree(all_modules: list) -> dict:
    """Build a directory tree structure from target_path values."""
    tree: dict = {}

    for m in all_modules:
        target = m.get("target_path", "")
        if not target:
            continue

        parts = target.replace("\\", "/").split("/")
        current = tree

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        filename = parts[-1]
        if "__files__" not in current:
            current["__files__"] = []
        if "__module_info__" not in current:
            current["__module_info__"] = {}

        current["__files__"].append(filename)
        current["__module_info__"][filename] = {
            "subdomain_id": m.get("subdomain_id", ""),
            "type": m.get("type", ""),
            "needs_migration": m.get("needs_migration", False),
        }

    def sort_tree(node: dict) -> None:
        if "__files__" in node:
            node["__files__"] = sorted(node["__files__"])
        for key in list(node.keys()):
            if key.startswith("__"):
                continue
            if isinstance(node[key], dict):
                sort_tree(node[key])

    sort_tree(tree)
    return tree


def cmd_write() -> None:
    """Generate and write target-path-tree.yaml."""
    print("[DM-107] Loading data sources...")

    depgraph = load_depgraph_from_db(DEPGRAPH_PATH)
    panorama = load_panorama_from_db(PANORAMA_PATH)
    migration_reg = load_yaml(MIGRATION_REGISTRY_PATH)
    func_reg = load_yaml(FUNC_DOMAIN_REGISTRY_PATH)

    print(f"[DM-107] Depgraph: {depgraph.get('metadata', {}).get('total_nodes', '?')} nodes")
    print(f"[DM-107] Migration registry: {len(migration_reg.get('entries', []))} entries")

    domain_ssot_map = build_domain_ssot_map(panorama, func_reg)
    migration_map = build_migration_map(migration_reg)

    print(f"[DM-107] Domain SSOT map: {len(domain_ssot_map)} subdomains")
    print(f"[DM-107] Migration map: {len(migration_map)} old→new path mappings")

    subdomain_modules, all_modules = build_target_tree(depgraph, domain_ssot_map, migration_map)

    print(f"[DM-107] Total modules processed: {len(all_modules)}")
    needs_migration = sum(1 for m in all_modules if m.get("needs_migration"))
    empty_subdomain = sum(1 for m in all_modules if not m.get("subdomain_id"))
    print(f"[DM-107] Needs migration: {needs_migration}")
    print(f"[DM-107] Already aligned: {len(all_modules) - needs_migration}")
    print(f"[DM-107] Empty subdomain: {empty_subdomain}")

    depgraph_meta = depgraph.get("metadata", {})
    output = generate_yaml_output(subdomain_modules, all_modules, domain_ssot_map, depgraph_meta)

    total_subdomains = output["meta"]["total_subdomains"]
    subdomain_coverage = output["meta"]["subdomain_coverage"]
    print(f"[DM-107] Total subdomains in output: {total_subdomains}")
    print(f"[DM-107] Subdomain coverage (with modules): {subdomain_coverage}")

    if total_subdomains < 35:
        print(f"[WARN] Expected 35 subdomains, got {total_subdomains}")

    tmp_path = f"{OUTPUT_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, str(OUTPUT_PATH))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

    print(f"[OK] Target path tree written to {OUTPUT_PATH}")
    print(f"     Modules: {len(all_modules)} | Subdomains: {total_subdomains} | Needs migration: {needs_migration}")


def cmd_check() -> None:
    """Verify target-path-tree.yaml is aligned with depgraph."""
    if not OUTPUT_PATH.exists():
        print("[FAIL] target-path-tree.yaml not found")
        sys.exit(1)

    with open(OUTPUT_PATH, encoding="utf-8") as f:
        target_tree = yaml.safe_load(f)

    meta = target_tree.get("meta", {})
    total_modules = meta.get("total_modules", 0)
    total_subdomains = meta.get("total_subdomains", 0)
    needs_migration = meta.get("needs_migration_count", 0)
    empty_subdomain = meta.get("empty_subdomain_count", 0)

    errors = []

    if total_subdomains < 35:
        errors.append(f"Total subdomains {total_subdomains} < 35")

    domains = target_tree.get("domains", {})
    missing_target = 0
    for subdomain_id, domain_data in domains.items():
        for m in domain_data.get("modules", []):
            if not m.get("target_path"):
                missing_target += 1
    if missing_target:
        errors.append(f"{missing_target} modules missing target_path")

    if empty_subdomain > total_modules * 0.3:
        errors.append(f"Too many modules with empty subdomain: {empty_subdomain}/{total_modules}")

    if errors:
        print("[FAIL] Alignment check failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(
            f"[OK] Target path tree aligned: {total_modules} modules, {total_subdomains} subdomains, {needs_migration} need migration"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate target-path-tree.yaml from depgraph")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="Write target-path-tree.yaml")
    group.add_argument("--check", action="store_true", help="Verify alignment")
    args = parser.parse_args()

    if args.check:
        cmd_check()
    elif args.write:
        cmd_write()
    else:
        depgraph = load_depgraph_from_db(DEPGRAPH_PATH)
        panorama = load_panorama_from_db(PANORAMA_PATH)
        migration_reg = load_yaml(MIGRATION_REGISTRY_PATH)
        func_reg = load_yaml(FUNC_DOMAIN_REGISTRY_PATH)

        domain_ssot_map = build_domain_ssot_map(panorama, func_reg)
        migration_map = build_migration_map(migration_reg)
        subdomain_modules, all_modules = build_target_tree(depgraph, domain_ssot_map, migration_map)
        depgraph_meta = depgraph.get("metadata", {})
        output = generate_yaml_output(subdomain_modules, all_modules, domain_ssot_map, depgraph_meta)
        print(yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
