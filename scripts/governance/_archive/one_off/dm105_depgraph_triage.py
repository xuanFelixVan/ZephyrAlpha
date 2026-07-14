#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.dm105_depgraph_triage
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
DM-105: depgraph 未分配节点三策略处理脚本
策略1: 归入(Assimilate) — 匹配已有 blueprint_id
策略2: 新建(Create New) — 标记为 MOD-NEW-XXX 待建蓝图
策略3: 废弃(Deprecate) — 标记为 DEPRECATE

[BLUEPRINT] DM-105 | data/asset_index/ | §depgraph-migration
[MODULE] scripts.governance.dm105_depgraph_triage
[INVARIANTS] 只修改 depgraph YAML; 不创建/删除磁盘文件; 原子写入
[MODIFY-GUARD] blueprint_id/domain_id/subdomain_id/decision/build_status/orphan_nodes/build_status_summary
[CONSUMERS] generate_project_depgraph.py; diagnose_depgraph.py
[STABILITY] volatile
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=成功; exit 1=加载失败; exit 2=验证失败
[TESTS] manual --dry-run
"""

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

PROJECT_ROOT = REPO_ROOT  # alias 真源
# 治本（2026-06-27）：删除 DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。
CSV_PATH = PROJECT_ROOT / "data/asset_index/module_domain_matching.csv"
BP_MAPPING_PATH = PROJECT_ROOT / "data/asset_index/blueprint-domain-mapping.yaml"


def load_csv_mapping(csv_path):
    """加载 CSV 映射: file_path -> {blueprint_id, domain_id, subdomain_id, confidence}"""
    mapping = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fp = row.get("file_path", "").strip()
            if not fp:
                continue
            mapping[fp] = {
                "blueprint_id": row.get("blueprint_id", "").strip(),
                "domain_id": row.get("domain_id", "").strip(),
                "subdomain_id": row.get("subdomain_id", "").strip(),
                "confidence": row.get("confidence", "").strip(),
                "match_method": row.get("match_method", "").strip(),
            }
    return mapping


def load_bp_mapping(yaml_path):
    """加载 blueprint-domain-mapping.yaml: blueprint_id -> {domain_id, subdomain_id}"""
    from ruamel.yaml import YAML

    yaml = YAML()
    yaml.preserve_quotes = True
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.load(f)
    mapping = {}
    mappings = data.get("mappings", {})
    if mappings is None:
        return mapping
    for _key, entry in mappings.items():
        bp_id = entry.get("blueprint_id", "")
        if bp_id:
            mapping[bp_id] = {
                "domain_id": entry.get("domain_id", ""),
                "subdomain_id": entry.get("subdomain_id", ""),
                "name": entry.get("name", ""),
                "ssot_path": entry.get("ssot_path", ""),
                "confidence": entry.get("confidence", ""),
            }
    return mapping


def load_depgraph(db_path):
    """加载 depgraph DB，返回与原 YAML 结构兼容的 dict"""
    conn = get_depgraph_pg_connection(autocommit=True)
    data = {"nodes": {}, "edges": [], "domains": {}, "metadata": {}}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = node.pop("node_id")
        node["type"] = node.pop("node_type", "")
        data["nodes"][nid] = node
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        edge["from"] = edge.pop("from_node_id", "")
        edge["to"] = edge.pop("to_node_id", "")
        data["edges"].append(edge)
    for row in conn.execute("SELECT * FROM domains"):
        domain = dict(row)
        did = domain.pop("domain_id")
        data["domains"][did] = domain
    conn.close()
    return data


def save_depgraph(data, db_path):
    """将修改后的 nodes 写回 depgraph DB"""
    conn = get_depgraph_pg_connection(autocommit=False)
    for nid, node in data.get("nodes", {}).items():
        row = dict(node)
        row["node_type"] = row.pop("type", "")
        sets = ", ".join(f"{k}=%s" for k in row if k != "node_id")
        vals = [v for k, v in row.items() if k != "node_id"]
        if sets:
            conn.execute(f"UPDATE nodes SET {sets} WHERE node_id=%s", vals + [nid])
    conn.commit()
    conn.close()


def file_exists_on_disk(path_str):
    """检查文件是否存在于磁盘"""
    full_path = PROJECT_ROOT / path_str
    return full_path.exists()


def path_to_blueprint_pattern(path_str):
    """从路径推导可能的 blueprint_id 模式匹配"""
    # src/zephyr/<pkg>/<subpkg>/... → 按包路径前缀匹配
    parts = path_str.split("/")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "zephyr":
        pkg = parts[2]
        subpkg = parts[3] if len(parts) > 3 else ""
        return pkg, subpkg
    if len(parts) >= 2 and parts[0] == "scripts":
        return "scripts", parts[1] if len(parts) > 1 else ""
    if len(parts) >= 2 and parts[0] == "tests":
        return "tests", ""
    if len(parts) >= 2 and parts[0] == "docs":
        return "docs", parts[1] if len(parts) > 1 else ""
    if len(parts) >= 2 and parts[0] == "data":
        return "data", parts[1] if len(parts) > 1 else ""
    return "", ""


# 包路径 → blueprint_id 的启发式映射
PKG_BLUEPRINT_HINTS = {
    "autonomy_perm": "MOD-INF-018",
    "budget-enforcer": "MOD-INF-024",
    "compliance": "MOD-INF-027",
    "data": "MOD-DATABASE",
    "drift-detector": "MOD-INF-023",
    "escalation-engine": "MOD-INF-022",
    "governance": "MOD-INF-005",
    "infrastructure": "MOD-INF-002",
    "integration": "MOD-INF-038",
    "observability": "MOD-FEEDBACK_LOOP",
    "orchestration": "MOD-CONTEXT_ENGINE",
    "reporting": "MOD-INF-026",
    "resilience": "MOD-INF-021",
    "security": "MOD-LLM_SECURITY",
    "shared": "MOD-INF-016",
    "testing": "MOD-INF-017",
    "portfolio": "MOD-NEW-PORTFOLIO",
    "signal_ashare": "ALPHA-SIGNAL-DOMAIN-001",
    "signal_gen": "ALPHA-SIGNAL-DOMAIN-001",
    "signal_quality": "ALPHA-SIGNAL-DOMAIN-001",
    "signal_strategy": "ALPHA-SIGNAL-DOMAIN-001",
    "signal_synth": "ALPHA-SIGNAL-DOMAIN-001",
    "trading": "MOD-NEW-TRADING",
    "research": "MOD-INF-011",
    "agent-spec": "MOD-INF-019",
    "autonomy_core": "MOD-INF-019",
}

# 测试文件名 → 被测模块 blueprint_id 的映射
TEST_BLUEPRINT_HINTS = {
    "test_auto_split": "MOD-TASK_SYSTEM",
    "test_boot_hooks_unlock": "MOD-INF-002",
    "test_bridges_contracts": "MOD-INF-016",
    "test_bridges_delegation_bridge": "MOD-INF-025",
    "test_bridges_tiered_storage_bridge": "MOD-DATABASE",
    "test_bridges_trust_bridge": "MOD-INF-018",
    "test_bridges_feedback_bridge": "MOD-FEEDBACK_LOOP",
    "test_event_store_stress": "MOD-INF-020",
    "test_mcp_task_claim": "MOD-TASK_SYSTEM",
    "test_staging_area": "MOD-INF-002",
    "_debug_counter": "MOD-TASK_SYSTEM",
    "_debug_race": "MOD-INF-002",
    "_debug_instrumented": "MOD-INF-002",
    "_minimal_race_test": "MOD-INF-002",
    "_stress_test_staging_concurrent": "MOD-INF-002",
}

# tests/unit/<subdir> → blueprint_id
TEST_UNIT_DIR_HINTS = {
    "agent-rbac": "MOD-INF-018",
    "budget-enforcer": "MOD-INF-024",
    "auto-fix-engine": "MOD-INF-030",
    "drift-detector": "MOD-INF-023",
    "escalation-engine": "MOD-INF-022",
    "feedback-loop": "MOD-FEEDBACK_LOOP",
    "governance": "MOD-INF-005",
    "rollback": "MOD-INF-021",
}

# 路径前缀 → (blueprint_id, domain_id, subdomain_id) 的精确映射
PATH_PREFIX_HINTS = {
    "src/zephyr/orchestration/agent_lifecycle/": ("MOD-INF-019", "D-ORCH", "D-ORCH-AGENT_LIFECYCLE"),
    "src/zephyr/orchestration/context_management/": ("MOD-CONTEXT_ENGINE", "D-ORCH", "D-ORCH-CONTEXT_MANAGEMENT"),
    "src/zephyr/orchestration/agent_communication/": ("MOD-INF-025", "D-ORCH", "D-ORCH-AGENT_COMMUNICATION"),
    "src/zephyr/governance/rule_enforcement/": ("MOD-GATE_ENGINE", "D-GOV", "D_GOV_RULE_ENFORCEMENT"),
    "data/asset_index/archive/": ("DEPRECATE", "", ""),
    "docs/03_modules/": ("MOD-INF-026", "D-OBS", "D-OBS-ASSET_INVENTORY"),
    "docs/01_policies_and_standards/": ("MOD-INF-005", "D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
    "docs/02_enterprise_architecture/": ("MOD-INF-026", "D-OBS", "D-OBS-ASSET_INVENTORY"),
    "scripts/governance/": ("MOD-INF-005", "D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
    "scripts/hooks/": ("MOD-INF-002", "D-INFRA", "D-INFRA-RUNTIME_INTEGRATION"),
}

# 精确文件路径 → (blueprint_id, domain_id, subdomain_id)
EXACT_FILE_HINTS = {
    "scripts/script_manifest.yaml": ("MOD-INF-005", "D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
    "docs/03_modules/module-registry.yaml": ("MOD-INF-026", "D-OBS", "D-OBS-ASSET_INVENTORY"),
    "docs/03_modules/blueprint_registry.yaml": ("MOD-INF-026", "D-OBS", "D-OBS-ASSET_INVENTORY"),
    "docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml": (
        "MOD-INF-005",
        "D-GOV",
        "D-GOV-SCRIPT_GOVERNANCE",
    ),
    "docs/01_policies_and_standards/_registry/catalogs/project-path-tree.yaml": (
        "MOD-INF-005",
        "D-GOV",
        "D-GOV-SCRIPT_GOVERNANCE",
    ),
    "docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json": (
        "MOD-INF-005",
        "D-GOV",
        "D-GOV-SCRIPT_GOVERNANCE",
    ),
    "docs/02_enterprise_architecture/migration-registry.yaml": ("MOD-INF-026", "D-OBS", "D-OBS-ASSET_INVENTORY"),
    "src/zephyr/shared/api/shared_quickref.yaml": ("MOD-INF-016", "D-INFRA", "D-INFRA-LIFECYCLE_MANAGEMENT"),
    "scripts/governance/test_concurrent_safety.ps1": ("MOD-INF-005", "D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
    "scripts/governance/d5_architecture/pre_commit_hook.ps1": ("MOD-INF-005", "D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
    "scripts/hooks/contract_fingerprint_hook.sh": ("MOD-INF-002", "D-INFRA", "D-INFRA-RUNTIME_INTEGRATION"),
    "scripts/hooks/git_secrets_setup.sh": ("MOD-INF-002", "D-INFRA", "D-INFRA-RUNTIME_INTEGRATION"),
}


def match_blueprint_for_path(path_str, csv_mapping, bp_mapping):
    """尝试为路径匹配 blueprint_id，返回 (blueprint_id, domain_id, subdomain_id, strategy, confidence)"""
    # 策略-1: 精确文件路径映射
    if path_str in EXACT_FILE_HINTS:
        bp_id, domain_id, subdomain_id = EXACT_FILE_HINTS[path_str]
        if bp_id in bp_mapping:
            bp_info = bp_mapping[bp_id]
            return (
                bp_id,
                bp_info.get("domain_id", domain_id),
                bp_info.get("subdomain_id", subdomain_id),
                "assimilate_exact_file",
                "high",
            )
        return bp_id, domain_id, subdomain_id, "assimilate_exact_file", "high"

    # 策略0: 路径前缀精确映射
    for prefix, (bp_id, domain_id, subdomain_id) in PATH_PREFIX_HINTS.items():
        if path_str.startswith(prefix):
            if bp_id == "DEPRECATE":
                return "", "", "", "deprecate_prefix", "high"
            if bp_id in bp_mapping:
                bp_info = bp_mapping[bp_id]
                return (
                    bp_id,
                    bp_info.get("domain_id", domain_id),
                    bp_info.get("subdomain_id", subdomain_id),
                    "assimilate_path_prefix",
                    "high",
                )
            return bp_id, domain_id, subdomain_id, "assimilate_path_prefix", "medium"

    # 策略1: CSV 精确匹配
    if path_str in csv_mapping:
        entry = csv_mapping[path_str]
        bp_id = entry.get("blueprint_id", "")
        if bp_id:
            return (
                bp_id,
                entry.get("domain_id", ""),
                entry.get("subdomain_id", ""),
                "assimilate_csv",
                entry.get("confidence", "high"),
            )

    # 策略1.5: 测试文件名匹配
    if path_str.startswith("tests/"):
        fname = Path(path_str).stem
        if fname in TEST_BLUEPRINT_HINTS:
            bp_id = TEST_BLUEPRINT_HINTS[fname]
            if bp_id in bp_mapping:
                bp_info = bp_mapping[bp_id]
                return (
                    bp_id,
                    bp_info.get("domain_id", ""),
                    bp_info.get("subdomain_id", ""),
                    "assimilate_test_name",
                    "medium",
                )
            return bp_id, "", "", "assimilate_test_name", "low"
        # tests/unit/<subdir>/ 匹配
        parts = path_str.split("/")
        if len(parts) >= 3 and parts[0] == "tests" and parts[1] == "unit":
            unit_dir = parts[2]
            if unit_dir in TEST_UNIT_DIR_HINTS:
                bp_id = TEST_UNIT_DIR_HINTS[unit_dir]
                if bp_id in bp_mapping:
                    bp_info = bp_mapping[bp_id]
                    return (
                        bp_id,
                        bp_info.get("domain_id", ""),
                        bp_info.get("subdomain_id", ""),
                        "assimilate_test_unit_dir",
                        "medium",
                    )
                return bp_id, "", "", "assimilate_test_unit_dir", "low"

    # 策略2: 包路径启发式匹配
    pkg, subpkg = path_to_blueprint_pattern(path_str)
    if pkg in PKG_BLUEPRINT_HINTS:
        bp_id = PKG_BLUEPRINT_HINTS[pkg]
        if bp_id in bp_mapping:
            bp_info = bp_mapping[bp_id]
            return (
                bp_id,
                bp_info.get("domain_id", ""),
                bp_info.get("subdomain_id", ""),
                "assimilate_heuristic",
                "medium",
            )
        return bp_id, "", "", "assimilate_heuristic", "low"

    # 策略3: 按子包名匹配 CSV 中的同目录文件
    if pkg and subpkg:
        prefix = f"src/zephyr/{pkg}/{subpkg}/"
        for csv_path, entry in csv_mapping.items():
            if csv_path.startswith(prefix) and entry.get("blueprint_id"):
                bp_id = entry["blueprint_id"]
                return (
                    bp_id,
                    entry.get("domain_id", ""),
                    entry.get("subdomain_id", ""),
                    "assimilate_dir_neighbor",
                    "medium",
                )

    return "", "", "", "unmatched", "none"


def should_deprecate(node_data, path_str):
    """判断节点是否应废弃"""
    # 1. 归档路径（无论是否在磁盘上）
    if path_str.startswith("data/asset_index/archive/"):
        return True, "archive_path"
    # 2. build_status=missing 且不在磁盘
    bs = node_data.get("build_status", "")
    if bs == "missing" and not file_exists_on_disk(path_str):
        return True, "missing_and_not_on_disk"
    # 3. design-only 且不在磁盘
    lifecycle = node_data.get("lifecycle", "")
    if lifecycle == "design" and not file_exists_on_disk(path_str):
        return True, "design_only_not_on_disk"
    # 4. decision 已标记为 DEPRECATE
    decision = node_data.get("decision", "")
    if decision == "DEPRECATE":
        return True, "already_marked_deprecate"
    # 5. debug/stress 测试文件（临时性质）
    fname = Path(path_str).stem
    if fname.startswith("_debug") or fname.startswith("_stress") or fname.startswith("_minimal"):
        return True, "debug_temp_test"
    return False, ""


def main():
    parser = argparse.ArgumentParser(description="DM-105 depgraph triage")
    parser.add_argument("--dry-run", action="store_true", help="只输出统计，不写入")
    args = parser.parse_args()

    print("=" * 60)
    print("DM-105: depgraph 未分配节点三策略处理")
    print("=" * 60)

    # 加载数据
    print("\n[1/6] 加载数据源...")
    try:
        csv_mapping = load_csv_mapping(CSV_PATH)
        print(f"  CSV 映射: {len(csv_mapping)} 条")
    except Exception as e:
        print(f"  CSV 加载失败: {e}")
        csv_mapping = {}

    try:
        bp_mapping = load_bp_mapping(BP_MAPPING_PATH)
        print(f"  Blueprint 映射: {len(bp_mapping)} 条")
    except Exception as e:
        print(f"  Blueprint 映射加载失败: {e}")
        bp_mapping = {}

    try:
        depgraph = load_depgraph(None)
        nodes = depgraph.get("nodes", {})
        if nodes is None:
            nodes = {}
        print(f"  Depgraph 节点: {len(nodes)} 个")
    except Exception as e:
        print(f"  Depgraph 加载失败: {e}")
        sys.exit(1)

    # 统计计数
    stats = Counter()
    assimilated_nodes = []
    new_blueprint_nodes = []
    deprecated_nodes = []
    still_unassigned = []

    # ==========================================
    # Step 1: 处理空 blueprint_id 节点
    # ==========================================
    print("\n[2/6] 分类空 blueprint_id 节点...")
    empty_bp_nodes = []
    for node_id, node_data in nodes.items():
        bp_id = node_data.get("blueprint_id", "")
        if bp_id is None:
            bp_id = ""
        if bp_id == "":
            empty_bp_nodes.append((node_id, node_data))

    print(f"  空 blueprint_id 节点: {len(empty_bp_nodes)} 个")

    for node_id, node_data in empty_bp_nodes:
        path_str = node_data.get("path", "")

        # 先检查是否应废弃
        should_dep, dep_reason = should_deprecate(node_data, path_str)
        if should_dep:
            deprecated_nodes.append((node_id, path_str, dep_reason))
            stats["deprecated"] += 1
            if not args.dry_run:
                node_data["decision"] = "DEPRECATE"
                node_data["build_status"] = "deprecated"
            continue

        # 尝试匹配 blueprint
        bp_id, domain_id, subdomain_id, strategy, confidence = match_blueprint_for_path(
            path_str, csv_mapping, bp_mapping
        )

        if bp_id and not bp_id.startswith("MOD-NEW-"):
            # 归入已有蓝图
            assimilated_nodes.append((node_id, path_str, bp_id, strategy, confidence))
            stats["assimilated"] += 1
            stats[f"assimilated_{strategy}"] += 1
            if not args.dry_run:
                node_data["blueprint_id"] = bp_id
                if domain_id:
                    node_data["domain_id"] = domain_id
                if subdomain_id:
                    node_data["subdomain_id"] = subdomain_id
                if not node_data.get("belongs_to"):
                    node_data["belongs_to"] = bp_id
        elif bp_id and bp_id.startswith("MOD-NEW-"):
            # 需要新建蓝图
            new_blueprint_nodes.append((node_id, path_str, bp_id))
            stats["new_blueprint"] += 1
            if not args.dry_run:
                node_data["blueprint_id"] = bp_id
                if not node_data.get("belongs_to"):
                    node_data["belongs_to"] = bp_id
        else:
            # 仍无法匹配
            still_unassigned.append((node_id, path_str))
            stats["still_unassigned"] += 1

    # ==========================================
    # Step 2: 处理 ghost 节点（不在磁盘上）
    # ==========================================
    print("\n[3/6] 处理 ghost 节点（不在磁盘上）...")
    ghost_count = 0
    ghost_deprecated = 0
    ghost_relocated = 0

    for node_id, node_data in nodes.items():
        path_str = node_data.get("path", "")
        if not path_str:
            continue
        if not file_exists_on_disk(path_str):
            ghost_count += 1
            # 归档路径 → 废弃
            if path_str.startswith("data/asset_index/archive/"):
                if not args.dry_run:
                    node_data["decision"] = "DEPRECATE"
                    node_data["build_status"] = "deprecated"
                ghost_deprecated += 1
                stats["ghost_archive_deprecated"] += 1
                continue
            # 测试文件不在磁盘 → 废弃
            if path_str.startswith("tests/") and node_data.get("type") == "test":
                if not args.dry_run:
                    node_data["decision"] = "DEPRECATE"
                    node_data["build_status"] = "deprecated"
                ghost_deprecated += 1
                stats["ghost_test_deprecated"] += 1
                continue
            # design_only 不在磁盘 → 废弃
            lifecycle = node_data.get("lifecycle", "")
            if lifecycle == "design":
                if not args.dry_run:
                    node_data["decision"] = "DEPRECATE"
                    node_data["build_status"] = "deprecated"
                ghost_deprecated += 1
                stats["ghost_design_deprecated"] += 1
                continue
            # build_status=missing 且不在磁盘 → 废弃
            bs = node_data.get("build_status", "")
            if bs == "missing":
                if not args.dry_run:
                    node_data["decision"] = "DEPRECATE"
                    node_data["build_status"] = "deprecated"
                ghost_deprecated += 1
                stats["ghost_missing_deprecated"] += 1
                continue
            # 其他 ghost 节点 — 尝试找重定位路径
            # 检查是否是已知的迁移模式
            operational_counterpart = node_data.get("operational_counterpart", "")
            if operational_counterpart and operational_counterpart in nodes:
                # 有 operational counterpart → 标记为 design 态
                if not args.dry_run:
                    node_data["decision"] = "KEEP"
                    node_data["lifecycle"] = "design"
                ghost_relocated += 1
                stats["ghost_has_counterpart"] += 1
                continue
            # 无法确定 → 保持原样但标记
            stats["ghost_unknown"] += 1

    print(f"  Ghost 节点总计: {ghost_count}")
    print(f"  已废弃: {ghost_deprecated}")
    print(f"  有 counterpart 保留: {ghost_relocated}")
    print(f"  未知状态: {stats['ghost_unknown']}")

    # ==========================================
    # Step 3: 处理 orphan_nodes 列表
    # ==========================================
    print("\n[4/6] 处理 orphan_nodes 列表...")
    orphan_list = depgraph.get("orphan_nodes", [])
    if orphan_list is None:
        orphan_list = []
    original_orphan_count = len(orphan_list)
    resolved_orphans = []
    remaining_orphans = []

    for orphan_id in orphan_list:
        if orphan_id not in nodes:
            # orphan 节点不在 nodes 中 → 移除
            resolved_orphans.append(orphan_id)
            stats["orphan_removed_not_in_nodes"] += 1
            continue

        node_data = nodes[orphan_id]
        bp_id = node_data.get("blueprint_id", "")
        if bp_id is None:
            bp_id = ""
        path_str = node_data.get("path", "")

        # 已有 blueprint_id → 不再是 orphan
        if bp_id:
            resolved_orphans.append(orphan_id)
            stats["orphan_resolved_has_blueprint"] += 1
            continue

        # 不在磁盘 → 废弃
        if not file_exists_on_disk(path_str):
            if not args.dry_run:
                node_data["decision"] = "DEPRECATE"
                node_data["build_status"] = "deprecated"
            resolved_orphans.append(orphan_id)
            stats["orphan_deprecated_not_on_disk"] += 1
            continue

        # 仍在磁盘且无 blueprint → 尝试匹配
        matched_bp, domain_id, subdomain_id, strategy, confidence = match_blueprint_for_path(
            path_str, csv_mapping, bp_mapping
        )
        if matched_bp:
            if not args.dry_run:
                node_data["blueprint_id"] = matched_bp
                if domain_id:
                    node_data["domain_id"] = domain_id
                if subdomain_id:
                    node_data["subdomain_id"] = subdomain_id
                if not node_data.get("belongs_to"):
                    node_data["belongs_to"] = matched_bp
            resolved_orphans.append(orphan_id)
            stats["orphan_assimilated"] += 1
            continue

        # 真正的 orphan — 保留
        remaining_orphans.append(orphan_id)
        stats["orphan_remaining"] += 1

    print(f"  原始 orphan: {original_orphan_count}")
    print(f"  已解决: {len(resolved_orphans)}")
    print(f"  剩余: {len(remaining_orphans)}")

    # ==========================================
    # Step 4: 更新 orphan_nodes 和 build_status_summary
    # ==========================================
    print("\n[5/6] 更新 depgraph 结构...")
    if not args.dry_run:
        # 更新 orphan_nodes
        depgraph["orphan_nodes"] = remaining_orphans

        # 更新 build_status_summary
        new_status_counts = Counter()
        for node_id, node_data in nodes.items():
            bs = node_data.get("build_status", "unknown")
            if bs is None:
                bs = "unknown"
            new_status_counts[bs] += 1

        bss = depgraph.get("build_status_summary", {})
        if bss is None:
            bss = {}
        by_status = bss.get("by_status", {})
        if by_status is None:
            by_status = {}
        for status_key in list(by_status.keys()):
            by_status[status_key] = new_status_counts.get(status_key, 0)
        # 添加新状态
        for status_key, count in new_status_counts.items():
            if status_key not in by_status:
                by_status[status_key] = count
        bss["by_status"] = by_status
        bss["total_nodes"] = len(nodes)
        bss["generated_at"] = datetime.now().isoformat()
        depgraph["build_status_summary"] = bss

        # 更新 graph_metrics
        gm = depgraph.get("graph_metrics", {})
        if gm is None:
            gm = {}
        gm["orphan_nodes_count"] = len(remaining_orphans)
        depgraph["graph_metrics"] = gm

        # 更新 metadata
        meta = depgraph.get("metadata", {})
        if meta is None:
            meta = {}
        meta["dm105_processed_at"] = datetime.now().isoformat()
        depgraph["metadata"] = meta

    # ==========================================
    # Step 5: 写入
    # ==========================================
    if not args.dry_run:
        print("  写入 depgraph...")
        save_depgraph(depgraph, None)
        print("  写入完成")
    else:
        print("  [DRY RUN] 跳过写入")

    # ==========================================
    # Step 6: 验证 + 报告
    # ==========================================
    print("\n[6/6] 验证与报告")
    print("=" * 60)

    # 验证: 重新加载检查
    if not args.dry_run:
        verify_graph = load_depgraph(None)
        verify_nodes = verify_graph.get("nodes", {})
        if verify_nodes is None:
            verify_nodes = {}
        empty_after = sum(
            1
            for nd in verify_nodes.values()
            if (nd.get("blueprint_id") or "") == ""
            and nd.get("lifecycle") != "design"
            and file_exists_on_disk(nd.get("path", ""))
        )
        deprecated_after = sum(1 for nd in verify_nodes.values() if nd.get("decision") == "DEPRECATE")
        print(f"  验证: 磁盘存在但空 blueprint_id 的节点: {empty_after}")
        print(f"  验证: 标记 DEPRECATE 的节点: {deprecated_after}")
    else:
        empty_after = "N/A (dry-run)"
        deprecated_after = "N/A (dry-run)"

    # 汇总报告
    print("\n" + "=" * 60)
    print("DM-105 处理结果汇总")
    print("=" * 60)
    print("\n--- 策略1: 归入 (Assimilate) ---")
    print(f"  总计归入: {stats['assimilated']}")
    print(f"    精确文件映射: {stats['assimilate_exact_file']}")
    print(f"    CSV 精确匹配: {stats['assimilated_assimilate_csv']}")
    print(f"    路径前缀匹配: {stats['assimilate_path_prefix']}")
    print(f"    测试文件名匹配: {stats['assimilate_test_name']}")
    print(f"    测试目录匹配: {stats['assimilate_test_unit_dir']}")
    print(f"    包路径启发式: {stats['assimilated_assimilate_heuristic']}")
    print(f"    目录邻居匹配: {stats['assimilated_assimilate_dir_neighbor']}")

    print("\n--- 策略2: 新建 (Create New) ---")
    print(f"  总计标记新蓝图: {stats['new_blueprint']}")
    # 按新蓝图 ID 分组
    new_bp_groups = Counter()
    for _, _, bp_id in new_blueprint_nodes:
        new_bp_groups[bp_id] += 1
    for bp_id, count in new_bp_groups.most_common():
        print(f"    {bp_id}: {count} 个节点")

    print("\n--- 策略3: 废弃 (Deprecate) ---")
    print(f"  空 blueprint_id 中废弃: {stats['deprecated']}")
    print(f"  Ghost 归档废弃: {stats['ghost_archive_deprecated']}")
    print(f"  Ghost 测试废弃: {stats['ghost_test_deprecated']}")
    print(f"  Ghost 设计态废弃: {stats['ghost_design_deprecated']}")
    print(f"  Ghost missing 废弃: {stats['ghost_missing_deprecated']}")
    print(f"  Ghost 有 counterpart 保留: {stats['ghost_has_counterpart']}")
    print(f"  Ghost 未知状态: {stats['ghost_unknown']}")
    total_deprecated = (
        stats["deprecated"]
        + stats["ghost_archive_deprecated"]
        + stats["ghost_test_deprecated"]
        + stats["ghost_design_deprecated"]
        + stats["ghost_missing_deprecated"]
    )
    print(f"  总计废弃: {total_deprecated}")

    print("\n--- Orphan 处理 ---")
    print(f"  已解决: {len(resolved_orphans)}")
    print(f"    不在 nodes 中移除: {stats['orphan_removed_not_in_nodes']}")
    print(f"    已有 blueprint 解决: {stats['orphan_resolved_has_blueprint']}")
    print(f"    不在磁盘废弃: {stats['orphan_deprecated_not_on_disk']}")
    print(f"    匹配蓝图解决: {stats['orphan_assimilated']}")
    print(f"  剩余真 orphan: {len(remaining_orphans)}")

    print("\n--- 仍无法分配 ---")
    print(f"  仍无 blueprint_id: {stats['still_unassigned']}")
    if still_unassigned:
        print("  前20个未分配节点:")
        for node_id, path_str in still_unassigned[:20]:
            print(f"    {path_str}")

    print("\n--- 验证结果 ---")
    print(f"  磁盘存在但空 blueprint_id: {empty_after}")
    print(f"  标记 DEPRECATE 总计: {deprecated_after}")

    # 输出归入详情（前30条）
    if assimilated_nodes:
        print("\n--- 归入详情（前30条）---")
        for node_id, path_str, bp_id, strategy, confidence in assimilated_nodes[:30]:
            print(f"  {path_str} → {bp_id} ({strategy}, {confidence})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
