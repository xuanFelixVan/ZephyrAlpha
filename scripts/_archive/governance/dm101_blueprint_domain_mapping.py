"""
DM-101: 构建 blueprint_id → domain 映射表 + CSV 模块匹配文件
读取 panorama + blueprint-registry + depgraph，输出两个文件到 data/asset_index/
"""

import csv
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml

BASE = r"D:\ZephyrAlpha"
PANORAMA_PATH = os.path.join(BASE, "data", "databases", "depgraph.db")
BLUEPRINT_REGISTRY_PATH = os.path.join(BASE, "docs", "03_modules", "blueprint_registry.yaml")
DEPGRAPH_PATH = os.path.join(BASE, "data", "databases", "depgraph.db")
ZEPHYR_SRC = os.path.join(BASE, "src", "zephyr")
OUTPUT_YAML = os.path.join(BASE, "data", "asset_index", "blueprint-domain-mapping.yaml")
OUTPUT_CSV = os.path.join(BASE, "data", "asset_index", "module_domain_matching.csv")

# functional_domain → (parent_domain, domain_id, subdomain_id) 映射
# 用于不在 panorama 中的业务层蓝图
FUNC_DOMAIN_MAP = {
    "data": ("data", "D-DATA", "D-DATA-CAPACITY_ASSURANCE"),
    "intelligence": ("intelligence", "D-INTEL", "D-INTEL-MODEL_PROFILING"),
    "research": ("intelligence", "D-INTEL", "D-INTEL-MODEL_EVALUATION"),
    "governance": ("governance", "D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
    "infra": ("infrastructure", "D-INFRA", "D-INFRA-SHARED_SERVICES"),
    "execution": ("orchestration", "D-ORCH", "D-ORCH-PIPELINE_ROUTING"),
    "operations": ("observability", "D-OBS", "D-OBS-FEEDBACK_LOOP"),
    "safety_escalation": ("resilience", "D-RES", "D-RES-ESCALATION"),
    "infrastructure": ("infrastructure", "D-INFRA", "D-INFRA-SHARED_SERVICES"),
    "system": ("orchestration", "D-ORCH", "D-ORCH-RUNTIME_CORE"),
    "alpha_signal": ("intelligence", "D-INTEL", "D-INTEL-MODEL_PROFILING"),
    "ml_experiment": ("intelligence", "D-INTEL", "D-INTEL-MODEL_EVALUATION"),
    "risk": ("resilience", "D-RES", "D-RES-BUDGET_ENFORCEMENT"),
    "portfolio": ("orchestration", "D-ORCH", "D-ORCH-PIPELINE_ROUTING"),
    "analytics": ("observability", "D-OBS", "D-OBS-TELEMETRY"),
    "interface": ("infrastructure", "D-INFRA", "D-INFRA-SHARED_SERVICES"),
    "compliance": ("governance", "D-GOV", "D-GOV-RULE_ENFORCEMENT"),
}

# 业务层蓝图专用子域映射（MOD-L00 ~ MOD-L13）
BUSINESS_LAYER_SUBDOMAINS = {
    "MOD-L00-001": ("data", "D-DATA", "D-DATA-CAPACITY_ASSURANCE", "src/zephyr/data/datasource/"),
    "MOD-L02-001": ("intelligence", "D-INTEL", "D-INTEL-MODEL_PROFILING", "src/zephyr/factor/"),
    "MOD-L03-001": ("intelligence", "D-INTEL", "D-INTEL-MODEL_EVALUATION", "src/zephyr/signal/"),
    "MOD-L04-001": ("resilience", "D-RES", "D-RES-BUDGET_ENFORCEMENT", "src/zephyr/risk/"),
    "MOD-L05-001": ("orchestration", "D-ORCH", "D-ORCH-PIPELINE_ROUTING", "src/zephyr/portfolio/"),
    "MOD-L06-001": ("orchestration", "D-ORCH", "D-ORCH-PIPELINE_ROUTING", "src/zephyr/execution/"),
    "MOD-L07-001": ("observability", "D-OBS", "D-OBS-TELEMETRY", "src/zephyr/analytics/"),
    "MOD-L08-001": ("infrastructure", "D-INFRA", "D-INFRA-SHARED_SERVICES", "src/zephyr/frontend/"),
    "MOD-L09-001": ("intelligence", "D-INTEL", "D-INTEL-MODEL_EVALUATION", "src/zephyr/research/"),
    "MOD-L10-001": ("governance", "D-GOV", "D-GOV-RULE_ENFORCEMENT", "src/zephyr/governance/"),
    "MOD-L11-001": ("intelligence", "D-INTEL", "D-INTEL-MODEL_EVALUATION", "src/zephyr/ml_train/"),
    "MOD-L13-001": ("intelligence", "D-INTEL", "D-INTEL-MODEL_EVALUATION", "src/zephyr/simulation/"),
}


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_panorama_mapping(panorama):
    """从 panorama 的 domains 段提取 ssot_module → subdomain 映射"""
    mapping = {}
    domains = panorama.get("domains", {})
    for subdomain_name, info in domains.items():
        ssot_module = info.get("ssot_module", "")
        mapping[ssot_module] = {
            "parent_domain": info["parent_domain"],
            "domain_id": info["domain_id"],
            "subdomain_id": info["subdomain_id"],
            "subdomain_name": subdomain_name,
            "ssot_path": info.get("ssot_path", ""),
        }
    return mapping


def make_key(module_id, name):
    """生成唯一键，处理重复 module_id（MOD-INF-015/024/030）"""
    return f"{module_id}::{name}" if name else module_id


def build_blueprint_domain_mapping(blueprint_registry, panorama_mapping):
    """构建完整的 blueprint_id → domain 映射，支持重复 module_id"""
    result = {}
    blueprints = blueprint_registry.get("blueprints", [])

    for bp in blueprints:
        module_id = bp.get("module_id", "")
        name = bp.get("name", "")
        func_domain = bp.get("functional_domain", "")
        file_path = bp.get("file_path", "")
        key = make_key(module_id, name)

        entry = {
            "blueprint_id": module_id,
            "name": name,
            "title": bp.get("title", ""),
            "layer": bp.get("layer", ""),
            "functional_domain": func_domain,
            "file_path": file_path,
        }

        # 1. 先查 panorama 映射（ssot_module 匹配）
        if module_id in panorama_mapping:
            pinfo = panorama_mapping[module_id]
            entry.update(
                {
                    "parent_domain": pinfo["parent_domain"],
                    "domain_id": pinfo["domain_id"],
                    "subdomain_id": pinfo["subdomain_id"],
                    "subdomain_name": pinfo["subdomain_name"],
                    "ssot_path": pinfo["ssot_path"],
                    "match_method": "panorama_ssot_module",
                    "confidence": "high",
                }
            )
            result[key] = entry
            continue

        # 2. 业务层蓝图专用映射
        if module_id in BUSINESS_LAYER_SUBDOMAINS:
            parent, did, sid, spath = BUSINESS_LAYER_SUBDOMAINS[module_id]
            entry.update(
                {
                    "parent_domain": parent,
                    "domain_id": did,
                    "subdomain_id": sid,
                    "subdomain_name": sid.split("-", 2)[-1].lower(),
                    "ssot_path": spath,
                    "match_method": "business_layer_mapping",
                    "confidence": "high",
                }
            )
            result[key] = entry
            continue

        # 3. 通过 functional_domain 映射
        if func_domain and func_domain in FUNC_DOMAIN_MAP:
            parent, did, sid = FUNC_DOMAIN_MAP[func_domain]
            entry.update(
                {
                    "parent_domain": parent,
                    "domain_id": did,
                    "subdomain_id": sid,
                    "subdomain_name": sid.split("-", 2)[-1].lower(),
                    "ssot_path": "",
                    "match_method": "functional_domain_fallback",
                    "confidence": "medium",
                }
            )
            result[key] = entry
            continue

        # 4. 无法映射 → 标记为孤儿
        entry.update(
            {
                "parent_domain": "unmapped",
                "domain_id": "D-UNMAPPED",
                "subdomain_id": "D-UNMAPPED-UNKNOWN",
                "subdomain_name": "unmapped",
                "ssot_path": "",
                "match_method": "no_match",
                "confidence": "low",
            }
        )
        result[key] = entry

    return result


def build_depgraph_blueprint_index(depgraph):
    """从 depgraph 节点构建 file_path → blueprint_id 索引"""
    index = {}
    nodes = depgraph.get("nodes", {})
    for node_id, node_info in nodes.items():
        path = node_info.get("path", "")
        bp_id = node_info.get("blueprint_id", "")
        if path and bp_id:
            index[path] = bp_id
    return index


def build_depgraph_domain_index(depgraph):
    """从 depgraph 节点构建 file_path → (domain_id, subdomain_id) 索引"""
    index = {}
    nodes = depgraph.get("nodes", {})
    for node_id, node_info in nodes.items():
        path = node_info.get("path", "")
        did = node_info.get("domain_id", "")
        sid = node_info.get("subdomain_id", "")
        if path:
            index[path] = (did, sid)
    return index


def scan_zephyr_files():
    """扫描 src/zephyr/ 下所有 .py 文件"""
    py_files = []
    for root, dirs, files in os.walk(ZEPHYR_SRC):
        for f in files:
            if f.endswith(".py"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, BASE).replace("\\", "/")
                py_files.append(rel)
    return py_files


def match_file_to_domain(rel_path, bp_index, domain_index, bp_domain_map, panorama_mapping):
    """匹配单个文件到域，返回 (file_path, module_id, blueprint_id, domain_id, subdomain_id, match_method, confidence)"""
    # 方法1: depgraph 直接匹配
    if rel_path in bp_index:
        bp_id = bp_index[rel_path]
        did, sid = domain_index.get(rel_path, ("", ""))
        # 在 bp_domain_map 中查找匹配的 blueprint_id
        matched_entry = None
        for key, info in bp_domain_map.items():
            if info["blueprint_id"] == bp_id:
                matched_entry = info
                break
        if matched_entry:
            return (
                rel_path,
                "",
                bp_id,
                matched_entry["domain_id"],
                matched_entry["subdomain_id"],
                "depgraph_blueprint",
                "high",
            )
        if did:
            return (rel_path, "", bp_id, did, sid, "depgraph_domain", "high")

    # 方法2: ssot_path 前缀匹配
    for ssot_mod, pinfo in panorama_mapping.items():
        ssot_path = pinfo["ssot_path"]
        if ssot_path and rel_path.startswith(ssot_path):
            return (rel_path, "", ssot_mod, pinfo["domain_id"], pinfo["subdomain_id"], "ssot_path_prefix", "high")

    # 方法3: 包路径匹配 (src/zephyr/{package}/...)
    parts = rel_path.split("/")
    if len(parts) >= 3:
        package = parts[2]  # src/zephyr/{package}/...
        pkg_to_domain = {
            "governance": ("D-GOV", "D-GOV-SCRIPT_GOVERNANCE"),
            "infra_ops": ("D-INFRA", "D-INFRA-RUNTIME_INTEGRATION"),
            "shared": ("D-INFRA", "D-INFRA-SHARED_SERVICES"),
            "security": ("D-SEC", "D-SEC-LLM_DEFENSE"),
            "data": ("D-DATA", "D-DATA-KNOWLEDGE_MANAGEMENT"),
            "agent-spec": ("D-ORCH", "D-ORCH-AGENT_LIFECYCLE"),
            "research": ("D-INTEL", "D-INTEL-MODEL_EVALUATION"),
            "budget-enforcer": ("D-RES", "D-RES-BUDGET_ENFORCEMENT"),
            "escalation-engine": ("D-RES", "D-RES-ESCALATION"),
            "core": ("D-INFRA", "D-INFRA-TASK_MANAGEMENT"),
            "pipeline": ("D-ORCH", "D-ORCH-PIPELINE_ROUTING"),
            "gates": ("D-GOV", "D-GOV-RULE_ENFORCEMENT"),
            "runtime": ("D-INFRA", "D-INFRA-RUNTIME_INTEGRATION"),
            "mcp": ("D-INFRA", "D-INFRA-MCP_SERVERS"),
            "knowledge_base": ("D-DATA", "D-DATA-KNOWLEDGE_MANAGEMENT"),
            "autonomy_perm": ("D-SEC", "D-SEC-ACCESS_CONTROL"),
            "factor": ("D-INTEL", "D-INTEL-MODEL_PROFILING"),
            "signal": ("D-INTEL", "D-INTEL-MODEL_EVALUATION"),
            "risk": ("D-RES", "D-RES-BUDGET_ENFORCEMENT"),
            "portfolio": ("D-ORCH", "D-ORCH-PIPELINE_ROUTING"),
            "execution": ("D-ORCH", "D-ORCH-PIPELINE_ROUTING"),
            "analytics": ("D-OBS", "D-OBS-TELEMETRY"),
            "frontend": ("D-INFRA", "D-INFRA-SHARED_SERVICES"),
            "compliance": ("D-GOV", "D-GOV-RULE_ENFORCEMENT"),
            "ml_train": ("D-INTEL", "D-INTEL-MODEL_EVALUATION"),
            "simulation": ("D-INTEL", "D-INTEL-MODEL_EVALUATION"),
            "datasource": ("D-DATA", "D-DATA-CAPACITY_ASSURANCE"),
        }
        if package in pkg_to_domain:
            did, sid = pkg_to_domain[package]
            return (rel_path, "", "", did, sid, "package_prefix", "medium")

    # 方法4: depgraph domain 索引兜底
    if rel_path in domain_index:
        did, sid = domain_index[rel_path]
        if did:
            return (rel_path, "", "", did, sid, "depgraph_domain_fallback", "medium")

    # 未匹配
    return (rel_path, "", "", "D-UNMAPPED", "D-UNMAPPED-UNKNOWN", "no_match", "low")


def main():
    print("[1/5] 加载 panorama...")
    panorama = load_yaml(PANORAMA_PATH)
    panorama_mapping = build_panorama_mapping(panorama)
    print(f"  panorama 子域数: {len(panorama_mapping)}")

    print("[2/5] 加载 blueprint-registry...")
    bp_registry = load_yaml(BLUEPRINT_REGISTRY_PATH)
    bp_domain_map = build_blueprint_domain_mapping(bp_registry, panorama_mapping)
    print(f"  蓝图映射数: {len(bp_domain_map)}")

    # 统计映射质量
    by_method = defaultdict(int)
    by_confidence = defaultdict(int)
    for info in bp_domain_map.values():
        by_method[info["match_method"]] += 1
        by_confidence[info["confidence"]] += 1
    print(f"  映射方法分布: {dict(by_method)}")
    print(f"  置信度分布: {dict(by_confidence)}")

    # 检查孤儿
    orphans = [info for info in bp_domain_map.values() if info["match_method"] == "no_match"]
    if orphans:
        print(f"  ⚠ 未映射蓝图: {len(orphans)}")
        for o in orphans:
            print(f"    - {o['blueprint_id']} ({o['name']}) func_domain={o['functional_domain']}")

    print("[3/5] 加载 depgraph...")
    depgraph = load_yaml(DEPGRAPH_PATH)
    bp_index = build_depgraph_blueprint_index(depgraph)
    domain_index = build_depgraph_domain_index(depgraph)
    print(f"  depgraph 文件→蓝图索引: {len(bp_index)}")
    print(f"  depgraph 文件→域索引: {len(domain_index)}")

    print("[4/5] 扫描 src/zephyr/ 并匹配域...")
    py_files = scan_zephyr_files()
    print(f"  Python 文件总数: {len(py_files)}")

    csv_rows = []
    match_stats = defaultdict(int)
    confidence_stats = defaultdict(int)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(match_file_to_domain, f, bp_index, domain_index, bp_domain_map, panorama_mapping): f
            for f in py_files
        }
        for future in as_completed(futures):
            row = future.result()
            csv_rows.append(row)
            match_stats[row[5]] += 1
            confidence_stats[row[6]] += 1

    print(f"  匹配方法分布: {dict(match_stats)}")
    print(f"  置信度分布: {dict(confidence_stats)}")

    matched = sum(1 for r in csv_rows if r[5] != "no_match")
    total = len(csv_rows)
    rate = matched / total * 100 if total else 0
    print(f"  匹配率: {matched}/{total} = {rate:.1f}%")

    # 写输出 YAML
    print("[5/5] 写入输出文件...")
    yaml_data = {
        "meta": {
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "blueprint_id → domain 完整映射表",
            "source_files": [
                "data/databases/depgraph.db",
                "docs/03_modules/blueprint_registry.yaml",
            ],
            "total_blueprints": len(bp_domain_map),
            "total_subdomains": len(panorama_mapping),
            "match_method_summary": dict(by_method),
            "confidence_summary": dict(by_confidence),
        },
        "mappings": bp_domain_map,
    }

    tmp_yaml = OUTPUT_YAML + f".{os.getpid()}.tmp"
    with open(tmp_yaml, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    os.replace(tmp_yaml, OUTPUT_YAML)
    print(f"  ✓ {OUTPUT_YAML}")

    # 写输出 CSV
    csv_rows.sort(key=lambda r: r[0])
    tmp_csv = OUTPUT_CSV + f".{os.getpid()}.tmp"
    with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["file_path", "module_id", "blueprint_id", "domain_id", "subdomain_id", "match_method", "confidence"]
        )
        writer.writerows(csv_rows)
    os.replace(tmp_csv, OUTPUT_CSV)
    print(f"  ✓ {OUTPUT_CSV}")

    # 验证报告
    print("\n=== 验证报告 ===")
    bp_count_in_registry = len(bp_registry.get("blueprints", []))
    bp_ids_in_mapping = set(info["blueprint_id"] for info in bp_domain_map.values())
    bp_unique_in_registry = {bp.get("module_id") for bp in bp_registry.get("blueprints", [])}
    missing = bp_unique_in_registry - bp_ids_in_mapping
    if missing:
        print(f"❌ 蓝图注册表中有 {len(missing)} 个 module_id 未在映射表中: {missing}")
    else:
        print(f"✅ 蓝图注册表 {bp_count_in_registry} 条记录（{len(bp_unique_in_registry)} 唯一 module_id）全部覆盖")
    print(f"   映射表条目数: {len(bp_domain_map)}（含重复 module_id 的不同蓝图）")

    unmapped_files = [r for r in csv_rows if r[5] == "no_match"]
    if unmapped_files:
        print(f"⚠ 未匹配文件: {len(unmapped_files)}/{total} ({len(unmapped_files) / total * 100:.1f}%)")
        # 按目录分组报告
        by_dir = defaultdict(list)
        for r in unmapped_files:
            parts = r[0].split("/")
            key = "/".join(parts[:4]) if len(parts) >= 4 else r[0]
            by_dir[key].append(r[0])
        for d, files in sorted(by_dir.items(), key=lambda x: -len(x[1])):
            print(f"    {d}: {len(files)} 个文件")
    else:
        print(f"✅ 所有 {total} 个文件均已匹配")

    if rate >= 90:
        print(f"✅ 匹配率 {rate:.1f}% ≥ 90%")
    else:
        print(f"❌ 匹配率 {rate:.1f}% < 90%")

    return 0 if rate >= 90 else 1


if __name__ == "__main__":
    sys.exit(main())
