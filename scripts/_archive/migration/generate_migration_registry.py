import os
import time
from collections import defaultdict

import yaml

OLD_DEPGRAPH = "data/databases/depgraph.db"
NEW_DEPGRAPH = "data/databases/depgraph.db"
PATH_TREE = "data/databases/depgraph.db"
OUTPUT = "data/asset_index/migration-registry.yaml"


def load_yaml(path):
    t0 = time.perf_counter()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"  Loaded {path}: {time.perf_counter() - t0:.2f}s")
    return data


def build_module_map(depgraph_v3):
    file_to_module = {}
    module_id_to_info = {}
    for domain_id, domain_data in depgraph_v3.get("modules", {}).items():
        for item in domain_data.get("items", []):
            mid = item.get("module_id", "")
            new_path = item.get("path", "")
            domain = item.get("domain", domain_id)
            mtype = item.get("type", "module")
            physical_files = item.get("physical_files", [])
            module_id_to_info[mid] = {
                "module_id": mid,
                "name": item.get("name", ""),
                "new_path": new_path,
                "domain": domain,
                "type": mtype,
                "blueprint_id": item.get("blueprint_id", ""),
                "stability": item.get("stability", ""),
                "safety_level": item.get("safety_level", ""),
                "ai_autonomy": item.get("ai_autonomy", ""),
                "build_status": item.get("build_status", ""),
            }
            for pf in physical_files:
                if pf not in file_to_module:
                    file_to_module[pf] = []
                file_to_module[pf].append(mid)
    return file_to_module, module_id_to_info


def resolve_ambiguous(file_to_module, module_id_to_info):
    file_to_domain = {}
    file_to_new_path = {}
    ambiguous_count = 0
    resolved_count = 0
    for fpath, mids in file_to_module.items():
        if len(mids) == 1:
            info = module_id_to_info[mids[0]]
            file_to_domain[fpath] = info["domain"]
            file_to_new_path[fpath] = info["new_path"]
        else:
            ambiguous_count += 1
            domain_counts = defaultdict(int)
            best_mid = mids[0]
            best_score = -1
            for mid in mids:
                info = module_id_to_info[mid]
                domain_counts[info["domain"]] += 1
                score = 0
                if info["type"] == "module":
                    score += 100
                if info["build_status"] == "built":
                    score += 50
                if info["stability"] in ("stable", "frozen"):
                    score += 30
                if info["safety_level"] == "H":
                    score += 20
                if len(info.get("physical_files", [])) > 0:
                    score += 10
                if score > best_score:
                    best_score = score
                    best_mid = mid
            info = module_id_to_info[best_mid]
            file_to_domain[fpath] = info["domain"]
            file_to_new_path[fpath] = info["new_path"]
            resolved_count += 1
    print(f"  Resolved {resolved_count}/{ambiguous_count} ambiguous file-to-module mappings")
    return file_to_domain, file_to_new_path


def build_old_path_prefix_map(module_id_to_info):
    prefix_map = {}
    for mid, info in module_id_to_info.items():
        old_path = info.get("new_path", "")
        if old_path:
            parts = old_path.rstrip("/").split("/")
            if len(parts) >= 3:
                prefix = "/".join(parts[:3]) + "/"
                if prefix not in prefix_map:
                    prefix_map[prefix] = []
                prefix_map[prefix].append(mid)
    return prefix_map


def build_domain_directory_map(path_tree):
    domain_dir_map = {}
    for domain in path_tree.get("path_design_spec", {}).get("domains", path_tree.get("domains", [])):
        did = domain.get("domain_id", "")
        td = domain.get("target_directory", "")
        domain_dir_map[did] = td
    return domain_dir_map


def build_blueprint_to_domain(depgraph_v3):
    bp_to_domain = {}
    for domain_id, domain_data in depgraph_v3.get("modules", {}).items():
        for item in domain_data.get("items", []):
            bp = item.get("blueprint_id", "")
            if bp:
                bp_to_domain[bp] = domain_id
    return bp_to_domain


OLD_LAYER_TO_DOMAIN = {
    "data": "D-DATA",
    "infra_runtime": "D-INFRA-RUNTIME",
    "factor": "D_FACTOR",
    "signal": "D-SIGNAL",
    "risk": "D_RISK",
    "pf_core": "D_PF_CORE",
    "ex_core": "D_EX_CORE",
    "pf_core": "D_REPORTING",
    "frontend": "D_FRONTEND",
    "research": "D-RESEARCH",
    "compliance": "D_COMPLIANCE",
    "ml_train": "D_ML_TRAIN",
    "simulation_backtesting": "D_SIMULATION",
    "integration": "D_SIMULATION",
}

OLD_DIR_TO_DOMAIN = {
    "src/zephyr/agent-rbac/": "D-AUTONOMY-CORE",
    "src/zephyr/autopilot/": "D-AUTONOMY-CORE",
    "src/zephyr/orchestrator/": "D-AUTONOMY-CORE",
    "src/zephyr/rollback/": "D-AUTONOMY-CORE",
    "src/zephyr/gates/": "D-AUTONOMY-CORE",
    "src/zephyr/pipeline/": "D-AUTONOMY-CORE",
    "src/zephyr/feedback-loop/": "D-AUTONOMY-CORE",
    "src/zephyr/runtime/": "D-AUTONOMY-CORE",
    "src/zephyr/core/": "D-AUTONOMY-CORE",
    "src/zephyr/db/": "D-AUTONOMY-CORE",
    "src/zephyr/llm-security/": "D_SECURITY",
    "src/zephyr/integration/": "D_INTEGRATION",
    "src/zephyr/governance/": "D_GOVERNANCE",
    "src/zephyr/kb/": "D_KNOWLEDGE",
    "src/zephyr/vector-memory/": "D_KNOWLEDGE",
    "src/zephyr/observability/telemetry/": "D_OPS",
    "src/zephyr/escalation-engine/": "D-AUTONOMY-CORE",
    "src/zephyr/budget-enforcer/": "D-AUTONOMY-CORE",
    "src/zephyr/capacity_calibrator/": "D_OPS",
    "src/zephyr/alert_manager/": "D_OPS",
    "src/zephyr/shared/": "D-INFRA-RUNTIME",
    "src/zephyr/factor/": "D_FACTOR",
    "src/zephyr/signal/": "D-SIGNAL",
    "src/zephyr/risk/": "D_RISK",
    "src/zephyr/portfolio/": "D_PF_CORE",
    "src/zephyr/execution/": "D_EX_CORE",
    "src/zephyr/trading/": "D_TRADING",
    "src/zephyr/governance/": "D_COMPLIANCE",
    "src/zephyr/ml/": "D_ML_TRAIN",
    "src/zephyr/data/": "D-DATA",
    "src/zephyr/research/": "D-RESEARCH",
    "src/zephyr/reporting/": "D_REPORTING",
    "src/zephyr/simulation/": "D_SIMULATION",
    "src/zephyr/position/": "D_POSITION",
    "src/zephyr/alt_data/": "D-ALT-DATA",
    "src/zephyr/cross_asset/": "D_CROSS_ASSET",
    "src/zephyr/data_eng/": "D-DATA-ENG",
    "src/zephyr/ml_serve/": "D_ML_SERVE",
    "src/zephyr/pf_alloc/": "D_PF_ALLOC",
    "src/zephyr/sell_decision/": "D_SELL_DECISION",
    "src/zephyr/ex_sor/": "D_EX_SOR",
    "src/zephyr/ex_core/": "D_EX_CORE",
    "src/zephyr/frontend/": "D_FRONTEND",
    "src/zephyr/infra_runtime/": "D-INFRA-RUNTIME",
    "src/zephyr/infra_ops/": "D-INFRA-OPS",
    "src/zephyr/autonomy_perm/": "D_AUTONOMY_PERM",
    "src/zephyr/autonomy_core/": "D-AUTONOMY-CORE",
    "src/zephyr/security/": "D_SECURITY",
    "src/zephyr/ops/": "D_OPS",
    "src/zephyr/knowledge/": "D_KNOWLEDGE",
}

SCRIPT_DIR_TO_DOMAIN = {
    "scripts/governance/": "D_GOVERNANCE",
    "scripts/ops/": "D_OPS",
    "scripts/context/": "D-AUTONOMY-CORE",
    "scripts/migration/": "D_GOVERNANCE",
    "scripts/fix_": "D_GOVERNANCE",
    "scripts/generate_": "D_GOVERNANCE",
    "scripts/security/": "D_SECURITY",
    "scripts/data/": "D-DATA",
}

NON_MIGRABLE_PREFIXES = [
    "data/",
    "docs/",
    "config/",
    ".github/",
    "infra/",
    ".runtime/",
    ".audit_cache/",
    ".ailocks/",
    ".aidrafts/",
]


def classify_file_type(path):
    if path.startswith("src/zephyr/"):
        if "/test" in path or path.endswith("_test.py"):
            return "test"
        return "module"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("data/"):
        return "data"
    if path.startswith("docs/"):
        return "doc"
    if path.startswith("config/"):
        return "config"
    if path.startswith(".github/"):
        return "infra"
    return "other"


def determine_domain(old_path, file_to_domain, file_to_new_path, bp_to_domain, old_node):
    if old_path in file_to_domain:
        domain = file_to_domain[old_path]
        new_module_path = file_to_new_path.get(old_path, "")
        return domain, "exact_physical_file_match", new_module_path

    bp = old_node.get("blueprint_id", "")
    if bp and bp in bp_to_domain:
        return bp_to_domain[bp], "blueprint_id_match", bp

    for prefix, domain in sorted(OLD_DIR_TO_DOMAIN.items(), key=lambda x: -len(x[0])):
        if old_path.startswith(prefix):
            return domain, "old_dir_prefix_match", prefix

    for prefix, domain in OLD_LAYER_TO_DOMAIN.items():
        if prefix in old_path:
            return domain, "old_layer_prefix_match", prefix

    for prefix, domain in SCRIPT_DIR_TO_DOMAIN.items():
        if old_path.startswith(prefix):
            return domain, "script_dir_match", prefix

    return None, "unassigned", None


def compute_new_path(old_path, domain, domain_dir_map, match_method, match_key):
    if domain is None:
        return None

    if match_method == "exact_physical_file_match" and match_key and "/" in match_key:
        filename = old_path.split("/")[-1]
        return match_key.rstrip("/") + "/" + filename

    domain_dir = domain_dir_map.get(domain, "")
    if not domain_dir:
        return None

    ftype = classify_file_type(old_path)

    if ftype == "module":
        old_parts = old_path.replace("src/zephyr/", "").split("/")
        filename = old_parts[-1]
        sub_parts = old_parts[:-1]
        new_path = (
            domain_dir.rstrip("/") + "/" + "/".join(sub_parts[1:])
            if len(sub_parts) > 1
            else domain_dir.rstrip("/") + "/"
        )
        new_path = new_path.rstrip("/") + "/" + filename
        return new_path

    if ftype == "script":
        filename = old_path.split("/")[-1]
        domain_name = domain_dir_map.get(domain, "unknown").replace("src/zephyr/", "").rstrip("/")
        return f"scripts/{domain_name}/{filename}"

    if ftype == "test":
        filename = old_path.split("/")[-1]
        domain_name = domain_dir_map.get(domain, "unknown").replace("src/zephyr/", "").rstrip("/")
        return f"tests/zephyr/{domain_name}/{filename}"

    return None


def compute_changes(old_path, new_path, domain, match_method):
    changes = []
    if new_path and old_path != new_path:
        changes.append(
            {
                "type": "physical_move",
                "from": old_path,
                "to": new_path,
            }
        )
    if new_path and old_path.startswith("src/zephyr/") and new_path.startswith("src/zephyr/"):
        old_import = old_path.replace("/", ".").removesuffix(".py")
        new_import = new_path.replace("/", ".").removesuffix(".py")
        if old_import != new_import:
            changes.append(
                {
                    "type": "self_import_update",
                    "old_import": old_import,
                    "new_import": new_import,
                }
            )
    if domain:
        changes.append({"type": "domain_assignment", "domain": domain})
    if match_method == "unassigned":
        changes.append({"type": "needs_domain_ruling"})
    return changes


def main():
    print("=== STEP 2C: Migration Registry Generator ===")
    print()

    print("[1/5] Loading YAML files...")
    old_dg = load_yaml(OLD_DEPGRAPH)
    new_dg = load_yaml(NEW_DEPGRAPH)
    pt = load_yaml(PATH_TREE)

    print("\n[2/5] Building lookup maps...")
    file_to_module, module_id_to_info = build_module_map(new_dg)
    file_to_domain, file_to_new_path = resolve_ambiguous(file_to_module, module_id_to_info)
    bp_to_domain = build_blueprint_to_domain(new_dg)
    domain_dir_map = build_domain_directory_map(pt)
    print(f"  file_to_module: {len(file_to_module)} entries")
    print(f"  file_to_domain (resolved): {len(file_to_domain)} entries")
    print(f"  module_id_to_info: {len(module_id_to_info)} entries")
    print(f"  bp_to_domain: {len(bp_to_domain)} entries")
    print(f"  domain_dir_map: {len(domain_dir_map)} entries")

    print("\n[3/5] Processing 22,929 old depgraph nodes...")
    old_nodes = old_dg.get("nodes", {})
    total = len(old_nodes)
    print(f"  Total old nodes: {total}")

    entries = []
    stats = defaultdict(int)
    domain_stats = defaultdict(int)
    unassigned_files = []
    non_migrable = []
    match_method_stats = defaultdict(int)

    for node_id, node_data in old_nodes.items():
        old_path = node_data.get("path", "")
        if not old_path:
            stats["no_path"] += 1
            continue

        is_non_migrable = any(old_path.startswith(p) for p in NON_MIGRABLE_PREFIXES)
        if is_non_migrable:
            non_migrable.append(
                {
                    "file_id": node_id,
                    "path": old_path,
                    "type": node_data.get("type", ""),
                    "reason": "non_migrable_prefix",
                }
            )
            stats["non_migrable"] += 1
            continue

        domain, match_method, match_key = determine_domain(
            old_path, file_to_domain, file_to_new_path, bp_to_domain, node_data
        )
        match_method_stats[match_method] += 1

        new_path = compute_new_path(old_path, domain, domain_dir_map, match_method, match_key)

        changes = compute_changes(old_path, new_path, domain, match_method)

        entry = {
            "file_id": node_id,
            "old_state": {
                "path": old_path,
                "type": node_data.get("type", ""),
                "blueprint_id": node_data.get("blueprint_id", ""),
                "stability": node_data.get("stability", ""),
                "safety": node_data.get("safety", ""),
                "ai_autonomy": node_data.get("ai_autonomy", ""),
            },
            "new_state": {
                "path": new_path if new_path else old_path,
                "domain": domain if domain else "UNASSIGNED",
                "domain_group": "",
            },
            "match_method": match_method,
            "changes_required": changes,
            "status": "pending",
        }

        if domain:
            domain_stats[domain] += 1
        else:
            unassigned_files.append(entry)
            stats["unassigned"] += 1

        if match_method == "multi_match_ambiguous":
            stats["ambiguous"] += 1

        entries.append(entry)

    print("\n[4/5] Generating migration registry...")
    print(f"  Total entries: {len(entries)}")
    print(f"  Non-migrable: {len(non_migrable)}")
    print(f"  Unassigned: {len(unassigned_files)}")
    print(f"  Ambiguous (resolved by scoring): {stats.get('ambiguous', 0)}")

    print("\n  Match method breakdown:")
    for method, count in sorted(match_method_stats.items(), key=lambda x: -x[1]):
        print(f"    {method}: {count}")

    print("\n  Domain distribution:")
    for domain, count in sorted(domain_stats.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count}")

    output_data = {
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "source": OLD_DEPGRAPH,
            "total_old_nodes": total,
            "total_entries": len(entries),
            "non_migrable_count": len(non_migrable),
            "unassigned_count": len(unassigned_files),
            "ambiguous_resolved_count": stats.get("ambiguous", 0),
            "match_method_stats": dict(match_method_stats),
            "domain_stats": dict(domain_stats),
        },
        "non_migrable_files": non_migrable,
        "unassigned_files": unassigned_files,
        "entries": entries,
    }

    tmp_path = OUTPUT + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, OUTPUT)
        print(f"\n[5/5] Written to {OUTPUT}")
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

    file_size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"  File size: {file_size_mb:.1f} MB")

    print("\n=== SUMMARY ===")
    print(f"  Old depgraph nodes: {total}")
    print(f"  Migration entries: {len(entries)}")
    print(f"  Non-migrable (data/docs/config): {len(non_migrable)}")
    print(f"  Unassigned (need ruling): {len(unassigned_files)}")
    print(f"  Ambiguous (resolved): {stats.get('ambiguous', 0)}")
    print(f"  Coverage: {(len(entries) - len(unassigned_files)) / len(entries) * 100:.1f}%")
    print(f"  Unassigned rate: {len(unassigned_files) / len(entries) * 100:.2f}%")


if __name__ == "__main__":
    main()
