# [BLUEPRINT] MOD-INF-037 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [DEPRECATED] 本脚本连字符命名（D-DATA/D-SIGNAL/D-RESEARCH/D-INFRA-RUNTIME 等）是历史 bug。
# 正确命名约定见 docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml v1.0.0
# （统一为下划线 D_XXX 格式）。本脚本保留在 _archive/migration/ 仅供历史参考，禁止用于生产。
# [A_module] module_id=MOD-GOV-inject_domain_fields | layer=script | stability=deprecated | safety=L | ai_autonomy=human_gated
# [TTL] permanent
import os
import time

import yaml

OLD_DEPGRAPH = "data/databases/depgraph.db"
REGISTRY = "data/asset_index/migration-registry.yaml"
BACKUP = "data/asset_index/project-entity-depgraph-v2-backup.yaml"
OUTPUT = "data/databases/depgraph.db"

DOMAIN_DIR_MAP = {
    "autonomy_core": "D_AUTONOMY_CORE",
    "autonomy_perm": "D_AUTONOMY_PERM",
    "infra_runtime": "D-INFRA-RUNTIME",
    "infra_ops": "D-INFRA-OPS",
    "security": "D_SECURITY",
    "integration": "D_INTEGRATION",
    "frontend": "D_FRONTEND",
    "governance": "D_GOVERNANCE",
    "ops": "D_OPS",
    "data": "D-DATA",
    "alt_data": "D-ALT-DATA",
    "data_eng": "D-DATA-ENG",
    "ml_train": "D_ML_TRAIN",
    "ml_serve": "D_ML_SERVE",
    "cross_asset": "D_CROSS_ASSET",
    "compliance": "D_COMPLIANCE",
    "knowledge": "D_KNOWLEDGE",
    "factor": "D_FACTOR",
    "signal": "D-SIGNAL",
    "pf_core": "D_PF_CORE",
    "pf_alloc": "D_PF_ALLOC",
    "sell_decision": "D_SELL_DECISION",
    "position": "D_POSITION",
    "ex_core": "D_EX_CORE",
    "ex_sor": "D_EX_SOR",
    "risk": "D_RISK",
    "reporting": "D_REPORTING",
    "trading": "D_TRADING",
    "simulation": "D_SIMULATION",
    "research": "D-RESEARCH",
}

OLD_DIR_TO_DOMAIN = {
    "agent-rbac": "D_AUTONOMY_CORE",
    "autopilot": "D_AUTONOMY_CORE",
    "orchestrator": "D_AUTONOMY_CORE",
    "rollback": "D_AUTONOMY_CORE",
    "gates": "D_AUTONOMY_CORE",
    "pipeline": "D_AUTONOMY_CORE",
    "feedback-loop": "D_AUTONOMY_CORE",
    "runtime": "D_AUTONOMY_CORE",
    "core": "D_AUTONOMY_CORE",
    "db": "D_AUTONOMY_CORE",
    "llm-security": "D_SECURITY",
    "integration": "D_INTEGRATION",
    "governance": "D_GOVERNANCE",
    "kb": "D_KNOWLEDGE",
    "vector-memory": "D_KNOWLEDGE",
    "system-telemetry": "D_OPS",
    "escalation-engine": "D_AUTONOMY_CORE",
    "budget-enforcer": "D_AUTONOMY_CORE",
    "capacity_calibrator": "D_OPS",
    "alert_manager": "D_OPS",
    "shared": "D-INFRA-RUNTIME",
    "factor": "D_FACTOR",
    "signal": "D-SIGNAL",
    "risk": "D_RISK",
    "portfolio": "D_PF_CORE",
    "execution": "D_EX_CORE",
    "trading": "D_TRADING",
    "compliance": "D_COMPLIANCE",
    "ml": "D_ML_TRAIN",
    "data": "D-DATA",
    "research": "D-RESEARCH",
    "reporting": "D_REPORTING",
    "simulation": "D_SIMULATION",
    "position": "D_POSITION",
    "alt_data": "D-ALT-DATA",
    "cross_asset": "D_CROSS_ASSET",
    "data_eng": "D-DATA-ENG",
    "ml_serve": "D_ML_SERVE",
    "pf_alloc": "D_PF_ALLOC",
    "sell_decision": "D_SELL_DECISION",
    "ex_sor": "D_EX_SOR",
    "ex_core": "D_EX_CORE",
    "frontend": "D_FRONTEND",
    "infra_runtime": "D-INFRA-RUNTIME",
    "infra_ops": "D-INFRA-OPS",
    "autonomy_perm": "D_AUTONOMY_PERM",
    "autonomy_core": "D_AUTONOMY_CORE",
    "security": "D_SECURITY",
    "ops": "D_OPS",
    "knowledge": "D_KNOWLEDGE",
    "context-engine": "D_AUTONOMY_CORE",
    "health-monitor": "D_OPS",
    "trading-contracts": "D_TRADING",
    "semantic-auditor": "D_GOVERNANCE",
    "mcp": "D_INTEGRATION",
    "agent-spec": "D_AUTONOMY_CORE",
    "audit-orchestrator": "D_GOVERNANCE",
    "red-blue-validator": "D_SECURITY",
}

OLD_LAYER_TO_DOMAIN = {
    "l00": "D-DATA",
    "l01": "D-INFRA-RUNTIME",
    "l02": "D_FACTOR",
    "l03": "D-SIGNAL",
    "l04": "D_RISK",
    "l05": "D_PF_CORE",
    "l06": "D_EX_CORE",
    "l07": "D_REPORTING",
    "l08": "D_FRONTEND",
    "l09": "D-RESEARCH",
    "l10": "D_COMPLIANCE",
    "l11": "D_ML_TRAIN",
    "l12": "D_SIMULATION",
    "l13": "D_SIMULATION",
}


def infer_domain(path, migration_registry):
    if path in migration_registry:
        return migration_registry[path]
    if path.startswith("src/zephyr/"):
        parts = path.replace("src/zephyr/", "").split("/")
        if parts:
            top_dir = parts[0]
            if top_dir in DOMAIN_DIR_MAP:
                return DOMAIN_DIR_MAP[top_dir]
            if top_dir in OLD_DIR_TO_DOMAIN:
                return OLD_DIR_TO_DOMAIN[top_dir]
        for key, domain in OLD_LAYER_TO_DOMAIN.items():
            if f"/{key}_" in path.lower() or f"/{key}/" in path.lower():
                return domain
    if path.startswith("scripts/governance/"):
        return "D_GOVERNANCE"
    if path.startswith("scripts/ops/"):
        return "D_OPS"
    if path.startswith("scripts/security/"):
        return "D_SECURITY"
    if path.startswith("scripts/"):
        return "D_OPS"
    return ""


def main():
    print("=== STEP 4: Inject domain fields into depgraph ===\n")

    print("[1/4] Loading migration registry...")
    t0 = time.perf_counter()
    with open(REGISTRY, encoding="utf-8") as f:
        reg_data = yaml.safe_load(f)
    migration_registry = {}
    for entry in reg_data.get("entries", []):
        old_path = entry.get("old_state", {}).get("path", "")
        domain = entry.get("new_state", {}).get("domain", "")
        if old_path and domain and domain != "UNASSIGNED":
            migration_registry[old_path] = domain
    print(f"  Migration registry: {len(migration_registry)} path-to-domain mappings ({time.perf_counter() - t0:.2f}s)")

    print("\n[2/4] Loading old depgraph...")
    t0 = time.perf_counter()
    with open(OLD_DEPGRAPH, encoding="utf-8") as f:
        depgraph = yaml.safe_load(f)
    nodes = depgraph.get("nodes", {})
    print(f"  Old depgraph: {len(nodes)} nodes ({time.perf_counter() - t0:.2f}s)")

    print("\n[3/4] Injecting domain fields...")
    t0 = time.perf_counter()
    domain_stats = {}
    no_domain = 0
    for node_id, node_data in nodes.items():
        path = node_data.get("path", "")
        domain = infer_domain(path, migration_registry)
        node_data["domain"] = domain
        if domain:
            domain_stats[domain] = domain_stats.get(domain, 0) + 1
        else:
            no_domain += 1

    print(f"  Injected domain fields in {time.perf_counter() - t0:.2f}s")
    print(f"  With domain: {len(nodes) - no_domain}")
    print(f"  Without domain: {no_domain}")
    print(f"  Domain count: {len(domain_stats)}")

    depgraph["metadata"]["version"] = "3.0.0"
    depgraph["metadata"]["domain_mode"] = "v3"
    depgraph["metadata"]["nodes_by_domain"] = dict(sorted(domain_stats.items()))
    depgraph["metadata"]["domain_count"] = len(domain_stats)

    print("\n[4/4] Writing updated depgraph...")
    t0 = time.perf_counter()
    tmp_path = OUTPUT + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(depgraph, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, OUTPUT)
        print(f"  Written to {OUTPUT} ({time.perf_counter() - t0:.2f}s)")
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

    file_size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"  File size: {file_size_mb:.1f} MB")

    print("\n=== SUMMARY ===")
    print(f"  Total nodes: {len(nodes)}")
    print(f"  With domain: {len(nodes) - no_domain} ({(len(nodes) - no_domain) / len(nodes) * 100:.1f}%)")
    print(f"  Without domain: {no_domain} ({no_domain / len(nodes) * 100:.1f}%)")
    print(f"  Domain count: {len(domain_stats)}")
    print("\n  Domain distribution:")
    for domain, count in sorted(domain_stats.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count}")


if __name__ == "__main__":
    main()
