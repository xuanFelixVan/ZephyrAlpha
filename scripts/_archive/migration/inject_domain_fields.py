import yaml
import os
import time

OLD_DEPGRAPH = "data/databases/depgraph.db"
REGISTRY = "data/asset_index/migration-registry.yaml"
BACKUP = "data/asset_index/project-entity-depgraph-v2-backup.yaml"
OUTPUT = "data/databases/depgraph.db"

DOMAIN_DIR_MAP = {
    "autonomy_core": "D-AUTONOMY-CORE", "autonomy_perm": "D-AUTONOMY-PERM",
    "infra_runtime": "D-INFRA-RUNTIME", "infra_ops": "D-INFRA-OPS",
    "security": "D-SECURITY", "integration": "D-INTEGRATION",
    "frontend": "D-FRONTEND", "governance": "D-GOVERNANCE",
    "ops": "D-OPS", "data": "D-DATA", "alt_data": "D-ALT-DATA",
    "data_eng": "D-DATA-ENG", "ml_train": "D-ML-TRAIN",
    "ml_serve": "D-ML-SERVE", "cross_asset": "D-CROSS-ASSET",
    "compliance": "D-COMPLIANCE", "knowledge": "D-KNOWLEDGE",
    "factor": "D-FACTOR", "signal": "D-SIGNAL",
    "pf_core": "D-PF-CORE", "pf_alloc": "D-PF-ALLOC",
    "sell_decision": "D-SELL-DECISION", "position": "D-POSITION",
    "ex_core": "D-EX-CORE", "ex_sor": "D-EX-SOR",
    "risk": "D-RISK", "reporting": "D-REPORTING",
    "trading": "D-TRADING", "simulation": "D-SIMULATION",
    "research": "D-RESEARCH",
}

OLD_DIR_TO_DOMAIN = {
    "agent-rbac": "D-AUTONOMY-CORE", "autopilot": "D-AUTONOMY-CORE",
    "orchestrator": "D-AUTONOMY-CORE", "rollback": "D-AUTONOMY-CORE",
    "gates": "D-AUTONOMY-CORE", "pipeline": "D-AUTONOMY-CORE",
    "feedback-loop": "D-AUTONOMY-CORE", "runtime": "D-AUTONOMY-CORE",
    "core": "D-AUTONOMY-CORE", "db": "D-AUTONOMY-CORE",
    "llm-security": "D-SECURITY", "integration": "D-INTEGRATION",
    "governance": "D-GOVERNANCE", "kb": "D-KNOWLEDGE",
    "vector-memory": "D-KNOWLEDGE", "system-telemetry": "D-OPS",
    "escalation-engine": "D-AUTONOMY-CORE", "budget-enforcer": "D-AUTONOMY-CORE",
    "capacity_calibrator": "D-OPS", "alert_manager": "D-OPS",
    "shared": "D-INFRA-RUNTIME", "factor": "D-FACTOR",
    "signal": "D-SIGNAL", "risk": "D-RISK", "portfolio": "D-PF-CORE",
    "execution": "D-EX-CORE", "trading": "D-TRADING",
    "compliance": "D-COMPLIANCE", "ml": "D-ML-TRAIN",
    "data": "D-DATA", "research": "D-RESEARCH",
    "reporting": "D-REPORTING", "simulation": "D-SIMULATION",
    "position": "D-POSITION", "alt_data": "D-ALT-DATA",
    "cross_asset": "D-CROSS-ASSET", "data_eng": "D-DATA-ENG",
    "ml_serve": "D-ML-SERVE", "pf_alloc": "D-PF-ALLOC",
    "sell_decision": "D-SELL-DECISION", "ex_sor": "D-EX-SOR",
    "ex_core": "D-EX-CORE", "frontend": "D-FRONTEND",
    "infra_runtime": "D-INFRA-RUNTIME", "infra_ops": "D-INFRA-OPS",
    "autonomy_perm": "D-AUTONOMY-PERM", "autonomy_core": "D-AUTONOMY-CORE",
    "security": "D-SECURITY", "ops": "D-OPS", "knowledge": "D-KNOWLEDGE",
    "context-engine": "D-AUTONOMY-CORE", "health-monitor": "D-OPS",
    "trading-contracts": "D-TRADING", "semantic-auditor": "D-GOVERNANCE",
    "mcp": "D-INTEGRATION", "agent-spec": "D-AUTONOMY-CORE",
    "audit-orchestrator": "D-GOVERNANCE", "red-blue-validator": "D-SECURITY",
}

OLD_LAYER_TO_DOMAIN = {
    "l00": "D-DATA", "l01": "D-INFRA-RUNTIME", "l02": "D-FACTOR",
    "l03": "D-SIGNAL", "l04": "D-RISK", "l05": "D-PF-CORE",
    "l06": "D-EX-CORE", "l07": "D-REPORTING", "l08": "D-FRONTEND",
    "l09": "D-RESEARCH", "l10": "D-COMPLIANCE", "l11": "D-ML-TRAIN",
    "l12": "D-SIMULATION", "l13": "D-SIMULATION",
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
        return "D-GOVERNANCE"
    if path.startswith("scripts/ops/"):
        return "D-OPS"
    if path.startswith("scripts/security/"):
        return "D-SECURITY"
    if path.startswith("scripts/"):
        return "D-OPS"
    return ""

def main():
    print("=== STEP 4: Inject domain fields into depgraph ===\n")

    print("[1/4] Loading migration registry...")
    t0 = time.perf_counter()
    with open(REGISTRY, "r", encoding="utf-8") as f:
        reg_data = yaml.safe_load(f)
    migration_registry = {}
    for entry in reg_data.get("entries", []):
        old_path = entry.get("old_state", {}).get("path", "")
        domain = entry.get("new_state", {}).get("domain", "")
        if old_path and domain and domain != "UNASSIGNED":
            migration_registry[old_path] = domain
    print(f"  Migration registry: {len(migration_registry)} path-to-domain mappings ({time.perf_counter()-t0:.2f}s)")

    print("\n[2/4] Loading old depgraph...")
    t0 = time.perf_counter()
    with open(OLD_DEPGRAPH, "r", encoding="utf-8") as f:
        depgraph = yaml.safe_load(f)
    nodes = depgraph.get("nodes", {})
    print(f"  Old depgraph: {len(nodes)} nodes ({time.perf_counter()-t0:.2f}s)")

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

    print(f"  Injected domain fields in {time.perf_counter()-t0:.2f}s")
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
        print(f"  Written to {OUTPUT} ({time.perf_counter()-t0:.2f}s)")
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

    file_size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"  File size: {file_size_mb:.1f} MB")

    print(f"\n=== SUMMARY ===")
    print(f"  Total nodes: {len(nodes)}")
    print(f"  With domain: {len(nodes) - no_domain} ({(len(nodes)-no_domain)/len(nodes)*100:.1f}%)")
    print(f"  Without domain: {no_domain} ({no_domain/len(nodes)*100:.1f}%)")
    print(f"  Domain count: {len(domain_stats)}")
    print(f"\n  Domain distribution:")
    for domain, count in sorted(domain_stats.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count}")

if __name__ == "__main__":
    main()
