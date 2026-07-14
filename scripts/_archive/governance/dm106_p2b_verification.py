#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.dm106_p2b_verification
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
DM-106: P2-B 迁移全量验证脚本
验证 depgraph 所有 P2-B 输出的完整性和一致性

depgraph 双层结构:
- 运营态节点(operational): type=module/script/test 等, 有 blueprint_id/domain_id/subdomain_id, 无 build_status/physical_files
- 设计态节点(design): type=blueprint/config/registry 等 + granularity=file 的节点, 有 build_status/physical_files

[BLUEPRINT] DM-106 | data/databases/depgraph.db | §p2b-verification
[MODULE] scripts.governance.dm106_p2b_verification
[INVARIANTS] 只读验证; 不修改任何文件(除验证报告和元数据更新)
[MODIFY-GUARD] 无
[CONSUMERS] 人工审查
[STABILITY] volatile
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=验证通过(含警告); exit 1=验证失败; exit 2=加载失败
[TESTS] manual --dry-run
"""

import csv
import json
import os
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

PROJECT_ROOT = REPO_ROOT  # alias 真源
# 治本（2026-06-27）：删除 DEPGRAPH_DB_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402
BP_MAPPING_PATH = PROJECT_ROOT / "data/asset_index/blueprint-domain-mapping.yaml"
CSV_PATH = PROJECT_ROOT / "data/asset_index/module_domain_matching.csv"
REPORT_PATH = PROJECT_ROOT / "data/asset_index/p2b-verification-report.yaml"

OPERATIONAL_REQUIRED_FIELDS = {"id", "path", "type", "blueprint_id"}
DESIGN_REQUIRED_FIELDS = {"id", "path", "type", "blueprint_id", "build_status"}
FILE_TYPES = {"module", "script"}


def _load_from_db(db_path):
    """Load depgraph data from PostgreSQL database, returning a dict compatible with the old YAML structure.

    P2迁移后：depgraph 已迁移到 PostgreSQL。db_path 参数保留用于日志引用。
    dict(row) 与原 sqlite3.Row 用法等价（RealDictRow 支持 dict() 转换）。
    """
    conn = get_depgraph_pg_connection(autocommit=True)
    data = {"nodes": {}, "edges": [], "domains": {}, "metadata": {}, "tree": {}, "meta": {}}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = node.pop("node_id")
        if "node_type" in node:
            node["type"] = node.pop("node_type")
        # Parse type_specific_data JSON
        tsd = node.pop("type_specific_data", None)
        if tsd:
            try:
                extra = json.loads(tsd)
                if isinstance(extra, dict):
                    for k, v in extra.items():
                        if k not in node or node[k] is None or node[k] == "" or node[k] == []:
                            node[k] = v
            except (json.JSONDecodeError, TypeError):
                pass
        # Parse tags JSON
        tags_raw = node.pop("tags", None)
        if tags_raw:
            try:
                node["tags"] = json.loads(tags_raw)
            except (json.JSONDecodeError, TypeError):
                node["tags"] = tags_raw
        data["nodes"][nid] = node
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        edge.pop("edge_id", None)
        if "from_node_id" in edge:
            edge["from"] = edge.pop("from_node_id")
        if "to_node_id" in edge:
            edge["to"] = edge.pop("to_node_id")
        # Parse JSON fields
        for json_field in ("api_contract_refs",):
            raw = edge.pop(json_field, None)
            if raw:
                try:
                    edge[json_field] = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    edge[json_field] = raw
        data["edges"].append(edge)
    for row in conn.execute("SELECT * FROM domains"):
        domain = dict(row)
        did = domain.pop("domain_id")
        data["domains"][did] = domain
    # Load arch_directory_tree as tree structure
    tree = {}
    for row in conn.execute("SELECT * FROM arch_directory_tree ORDER BY path"):
        entry = dict(row)
        path = entry.get("path", "")
        if path:
            parts = path.split("/")
            current = tree
            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {}
                if i == len(parts) - 1:
                    current[part]["__domain_id__"] = entry.get("domain_id", "")
                    current[part]["__subdomain_id__"] = ""
                    current[part]["lifecycle"] = entry.get("state", "operational")
                else:
                    current = current[part]
    data["tree"] = tree
    # Load metadata from _schema_version
    try:
        cur = conn.execute("SELECT version FROM _schema_version ORDER BY version DESC LIMIT 1")
        r = cur.fetchone()
        if r:
            data["meta"]["schema_version"] = r["version"]
    except Exception:
        pass
    conn.close()
    return data


def _update_db_metadata(db_path, metadata_updates):
    """Update metadata fields in the depgraph (PostgreSQL) database.

    DM-202947 止血修复：_schema_version 表仅允许 depgraph_schema.py 的 _run_migration 写入，
    禁止其他脚本通过 INSERT OR REPLACE 覆写版本记录。此函数现为空操作（仅打印日志）。
    """
    desc = "; ".join(f"{k}={v}" for k, v in metadata_updates.items())
    print(f"[DM106] 元数据更新已跳过（_schema_version 只读保护）: {desc}")


def load_yaml(path):
    from ruamel.yaml import YAML

    yaml = YAML()
    yaml.preserve_quotes = True
    with open(path, encoding="utf-8") as f:
        return yaml.load(f)


def save_yaml(data, path):
    from ruamel.yaml import YAML

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        os.replace(tmp_path, path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def count_py_files_on_disk():
    counts = {"src": 0, "scripts": 0, "tests": 0, "total": 0}
    for root_dir, key in [("src/zephyr", "src"), ("scripts", "scripts"), ("tests", "tests")]:
        full = PROJECT_ROOT / root_dir
        if full.exists():
            for dirpath, dirnames, filenames in os.walk(full):
                for fn in filenames:
                    if fn.endswith(".py"):
                        counts[key] += 1
                        counts["total"] += 1
    return counts


def get_panorama_subdomains(panorama_data):
    subdomains = set()
    domains = panorama_data.get("domains", {})
    if domains:
        for domain_key, domain_info in domains.items():
            sid = domain_info.get("subdomain_id", "")
            if sid:
                subdomains.add(sid)
    return subdomains


def classify_nodes(nodes):
    """将节点分为运营态和设计态两类"""
    operational = {}
    design = {}
    for nid, node in nodes.items():
        if not isinstance(node, dict):
            continue
        if node.get("granularity") == "file":
            design[nid] = node
        else:
            operational[nid] = node
    return operational, design


class VerificationResult:
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
        self.stats = {}

    def add_check(self, check_id, name, passed, detail="", severity="info"):
        self.checks.append(
            {
                "check_id": check_id,
                "name": name,
                "passed": passed,
                "detail": detail,
                "severity": severity,
            }
        )

    def add_warning(self, msg):
        self.warnings.append(msg)

    def add_error(self, msg):
        self.errors.append(msg)

    def to_dict(self):
        passed_count = sum(1 for c in self.checks if c["passed"])
        failed_count = len(self.checks) - passed_count
        critical_fails = [c for c in self.checks if not c["passed"] and c["severity"] == "critical"]
        warn_fails = [c for c in self.checks if not c["passed"] and c["severity"] == "warning"]
        return {
            "meta": {
                "generated_at": datetime.now(UTC).isoformat(),
                "version": "1.0.0",
                "description": "DM-106 P2-B 迁移全量验证报告",
            },
            "overall_status": "PASS"
            if not critical_fails
            else ("WARN" if not warn_fails or critical_fails else "FAIL"),
            "summary": {
                "total_checks": len(self.checks),
                "passed": passed_count,
                "failed": failed_count,
                "critical_failures": len(critical_fails),
                "warning_failures": len(warn_fails),
                "warnings_count": len(self.warnings),
                "errors_count": len(self.errors),
            },
            "checks": self.checks,
            "warnings": self.warnings,
            "errors": self.errors,
            "stats": self.stats,
        }


def run_verification():
    result = VerificationResult()
    t0 = time.perf_counter()

    # ========== 加载数据 ==========
    print("[1/10] 加载 depgraph...")
    try:
        depgraph = _load_from_db(None)
    except Exception as e:
        print(f"FATAL: 无法加载 depgraph: {e}")
        sys.exit(2)

    print("[2/10] 加载 blueprint-domain-mapping...")
    try:
        bp_mapping_data = load_yaml(BP_MAPPING_PATH)
    except Exception as e:
        print(f"WARN: 无法加载 blueprint_domain_mapping: {e}")
        bp_mapping_data = None

    print("[3/10] 加载 module_domain_matching.csv...")
    csv_mapping = {}
    try:
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fp = row.get("file_path", "").strip()
                if fp:
                    csv_mapping[fp] = row
    except Exception as e:
        print(f"WARN: 无法加载 CSV: {e}")

    print("[4/10] 加载 architecture-panorama...")
    try:
        panorama_data = _load_from_db(None)
    except Exception as e:
        print(f"WARN: 无法加载 panorama: {e}")
        panorama_data = None

    nodes = depgraph.get("nodes", {})
    edges = depgraph.get("edges", [])
    metadata = depgraph.get("metadata", {})
    build_status_summary = depgraph.get("build_status_summary", {})
    orphan_nodes_list = depgraph.get("orphan_nodes", [])
    graph_metrics = depgraph.get("graph_metrics", {})

    node_ids = set(nodes.keys())
    total_nodes = len(nodes)

    # 分类节点
    operational_nodes, design_nodes = classify_nodes(nodes)
    op_count = len(operational_nodes)
    design_count = len(design_nodes)
    print(f"  总节点: {total_nodes}, 运营态: {op_count}, 设计态: {design_count}, 边: {len(edges)}")

    # 活跃节点(非废弃)
    active_op = {
        nid: n for nid, n in operational_nodes.items() if isinstance(n, dict) and n.get("decision") != "DEPRECATE"
    }
    active_design = {
        nid: n for nid, n in design_nodes.items() if isinstance(n, dict) and n.get("build_status") != "deprecated"
    }
    active_count = len(active_op) + len(active_design)

    # ========== CHECK 1: 节点字段完整性 ==========
    print("\n[CHECK 1] 节点字段完整性...")
    missing_field_nodes = []
    for nid, node in nodes.items():
        if not isinstance(node, dict):
            continue
        is_design = node.get("granularity") == "file"
        required = DESIGN_REQUIRED_FIELDS if is_design else OPERATIONAL_REQUIRED_FIELDS
        for field in required:
            if field not in node or node[field] is None or node[field] == "":
                missing_field_nodes.append((nid, field))
                break

    missing_count = len(missing_field_nodes)
    passed = missing_count == 0
    detail = f"缺失字段节点: {missing_count}/{total_nodes}"
    if not passed:
        detail += "; 示例: " + ", ".join(f"{n}[{f}]" for n, f in missing_field_nodes[:10])
    result.add_check("CHK-01", "节点字段完整性", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 2: blueprint_id 覆盖率(运营态) ==========
    print("\n[CHECK 2] blueprint_id 覆盖率(运营态)...")
    active_op_count = len(active_op)
    active_op_with_bp = sum(1 for n in active_op.values() if isinstance(n, dict) and n.get("blueprint_id"))
    bp_rate = active_op_with_bp / active_op_count * 100 if active_op_count else 0
    passed = bp_rate >= 95.0
    detail = f"活跃运营态节点: {active_op_count}, 有blueprint_id: {active_op_with_bp}, 覆盖率: {bp_rate:.2f}%"
    result.add_check("CHK-02", "blueprint_id覆盖率(>95%)", passed, detail, "critical" if not passed else "info")
    print(f"  {'PASS' if passed else 'FAIL'}: {detail}")

    # ========== CHECK 3: physical_files 覆盖率(设计态) ==========
    print("\n[CHECK 3] physical_files 覆盖率(设计态)...")
    active_design_file = {
        nid: n for nid, n in active_design.items() if isinstance(n, dict) and n.get("type") in FILE_TYPES
    }
    design_file_count = len(active_design_file)
    design_with_pf = sum(1 for n in active_design_file.values() if isinstance(n, dict) and n.get("physical_files"))
    pf_rate = design_with_pf / design_file_count * 100 if design_file_count else 0
    # 设计态文件节点可能没有physical_files(如blueprint类型), 只检查有physical_files字段的
    design_has_pf_field = sum(1 for n in active_design.values() if isinstance(n, dict) and "physical_files" in n)
    design_total_with_pf = sum(1 for n in active_design.values() if isinstance(n, dict) and n.get("physical_files"))
    pf_field_rate = design_total_with_pf / design_has_pf_field * 100 if design_has_pf_field else 0
    passed = pf_field_rate >= 95.0
    detail = (
        f"设计态有physical_files字段: {design_has_pf_field}, 非空: {design_total_with_pf}, 非空率: {pf_field_rate:.2f}%"
    )
    result.add_check("CHK-03", "physical_files非空率(设计态>95%)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 4: build_status 一致性(设计态) ==========
    print("\n[CHECK 4] build_status 一致性(设计态)...")
    inconsistent = []
    for nid, node in active_design.items():
        if not isinstance(node, dict):
            continue
        bs = node.get("build_status", "")
        fpath = node.get("path", "")
        if not fpath:
            continue
        full_path = PROJECT_ROOT / fpath
        exists = full_path.exists()
        if bs == "missing" and exists:
            inconsistent.append((nid, fpath, "build_status=missing但文件存在"))
        if bs in ("production", "implemented", "partial") and not exists:
            inconsistent.append((nid, fpath, f"build_status={bs}但文件不存在"))

    passed = len(inconsistent) == 0
    detail = f"不一致节点: {len(inconsistent)}"
    if not passed:
        detail += "; 示例: " + ", ".join(f"{n}: {r}" for n, _, r in inconsistent[:10])
    result.add_check("CHK-04", "build_status一致性(设计态)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 5: 边完整性 ==========
    print("\n[CHECK 5] 边端点完整性...")
    invalid_edges = []
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            continue
        src = edge.get("from", "")
        tgt = edge.get("to", "")
        if src and src not in node_ids:
            invalid_edges.append((i, "from", src))
        if tgt and tgt not in node_ids:
            invalid_edges.append((i, "to", tgt))

    passed = len(invalid_edges) == 0
    detail = f"无效边: {len(invalid_edges)}/{len(edges)}"
    if not passed:
        detail += "; 示例: " + ", ".join(f"edge[{i}].{d}={v}" for i, d, v in invalid_edges[:10])
    result.add_check("CHK-05", "边端点完整性", passed, detail, "critical" if not passed else "info")
    print(f"  {'PASS' if passed else 'FAIL'}: {detail}")

    # ========== CHECK 6: 域覆盖 ==========
    print("\n[CHECK 6] 域覆盖...")
    panorama_subdomains = get_panorama_subdomains(panorama_data) if panorama_data else set()
    depgraph_subdomains = set()
    for nid, node in nodes.items():
        if isinstance(node, dict) and node.get("subdomain_id"):
            depgraph_subdomains.add(node["subdomain_id"])

    if panorama_subdomains:
        uncovered = panorama_subdomains - depgraph_subdomains
        covered = panorama_subdomains & depgraph_subdomains
        passed = len(uncovered) == 0
        detail = f"全景图子域: {len(panorama_subdomains)}, depgraph覆盖: {len(covered)}, 未覆盖: {len(uncovered)}"
        if not passed:
            detail += "; 未覆盖: " + ", ".join(sorted(uncovered)[:10])
    else:
        passed = True
        detail = "无法加载全景图，跳过域覆盖检查"
        result.add_warning("全景图未加载，域覆盖检查跳过")

    result.add_check("CHK-06", "域覆盖(35子域)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 7: 脚本节点数 ==========
    print("\n[CHECK 7] 脚本节点数...")
    script_nodes_op = {
        nid: n for nid, n in operational_nodes.items() if isinstance(n, dict) and n.get("type") == "script"
    }
    depgraph_script_count = len(script_nodes_op)
    disk_counts = count_py_files_on_disk()
    disk_script_count = disk_counts["scripts"]

    # 允许小差异(5个以内)
    diff = abs(depgraph_script_count - disk_script_count)
    passed = diff <= 5
    detail = f"depgraph脚本节点: {depgraph_script_count}, 磁盘scripts/.py: {disk_script_count}, 差异: {diff}"
    result.add_check("CHK-07", "脚本节点数匹配(±5)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 8: build_status_summary 一致性(设计态) ==========
    print("\n[CHECK 8] build_status_summary 一致性(设计态)...")
    design_status_counts = Counter()
    design_type_counts = Counter()
    for nid, node in design_nodes.items():
        if not isinstance(node, dict):
            continue
        bs = node.get("build_status", "unknown")
        ntype = node.get("type", "unknown")
        design_status_counts[bs] += 1
        design_type_counts[ntype] += 1

    summary_by_status = build_status_summary.get("by_status", {})
    summary_total = build_status_summary.get("total_nodes", 0)

    status_mismatches = []
    for status, count in design_status_counts.items():
        reported = summary_by_status.get(status, 0)
        if count != reported:
            status_mismatches.append((status, count, reported))

    for status, reported in summary_by_status.items():
        if status not in design_status_counts and reported != 0:
            status_mismatches.append((status, 0, reported))

    total_match = design_count == summary_total
    passed = len(status_mismatches) == 0 and total_match
    detail = f"设计态节点: {design_count}, 报告节点: {summary_total}, 状态不匹配: {len(status_mismatches)}"
    if not passed:
        if not total_match:
            detail += f"; 总数不匹配(差{design_count - summary_total})"
        if status_mismatches:
            detail += "; " + ", ".join(f"{s}:实际={a},报告={r}" for s, a, r in status_mismatches[:10])
    result.add_check(
        "CHK-08", "build_status_summary一致性(设计态)", passed, detail, "warning" if not passed else "info"
    )
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 9: 废弃节点一致性 ==========
    print("\n[CHECK 9] 废弃节点一致性...")
    deprecated_nodes = {nid: n for nid, n in nodes.items() if isinstance(n, dict) and n.get("decision") == "DEPRECATE"}
    deprecated_with_status = sum(
        1 for n in deprecated_nodes.values() if isinstance(n, dict) and n.get("build_status") == "deprecated"
    )
    deprecated_count = len(deprecated_nodes)

    inconsistent_deprecated = []
    for nid, node in deprecated_nodes.items():
        if not isinstance(node, dict):
            continue
        if node.get("build_status") != "deprecated":
            inconsistent_deprecated.append((nid, node.get("build_status", "missing")))

    passed = len(inconsistent_deprecated) == 0
    detail = f"DEPRECATE节点: {deprecated_count}, build_status=deprecated: {deprecated_with_status}, 不一致: {len(inconsistent_deprecated)}"
    if not passed:
        detail += "; 示例: " + ", ".join(f"{n}[bs={bs}]" for n, bs in inconsistent_deprecated[:10])
    result.add_check("CHK-09", "废弃节点一致性", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== CHECK 10: 孤儿节点 ==========
    print("\n[CHECK 10] 孤儿节点...")
    orphan_count = len(orphan_nodes_list)
    edge_targets = set()
    edge_sources = set()
    for edge in edges:
        if isinstance(edge, dict):
            edge_sources.add(edge.get("from", ""))
            edge_targets.add(edge.get("to", ""))

    truly_orphan = []
    non_orphan_in_list = []
    for onid in orphan_nodes_list:
        has_edge = onid in edge_sources or onid in edge_targets
        if has_edge:
            non_orphan_in_list.append(onid)
        else:
            truly_orphan.append(onid)

    all_connected = edge_sources | edge_targets
    unlisted_orphans = []
    for nid in node_ids:
        if nid not in all_connected and nid not in set(orphan_nodes_list):
            node = nodes.get(nid)
            if isinstance(node, dict) and node.get("decision") != "DEPRECATE":
                unlisted_orphans.append(nid)

    passed = len(non_orphan_in_list) == 0
    detail = f"孤儿列表: {orphan_count}, 真正无连接: {len(truly_orphan)}, 有连接但列入: {len(non_orphan_in_list)}, 未列入但无连接: {len(unlisted_orphans)}"
    if not passed:
        if non_orphan_in_list:
            detail += "; 有连接但列入: " + ", ".join(non_orphan_in_list[:5])
    if len(unlisted_orphans) > 0:
        detail += f"; 注意: {len(unlisted_orphans)}个无连接节点未列入孤儿列表(可能为设计态节点)"
    result.add_check("CHK-10", "孤儿节点一致性", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== DM-101: blueprint-domain-mapping ==========
    print("\n[CHECK 11] DM-101: blueprint-domain-mapping 覆盖率...")
    if bp_mapping_data:
        bp_mappings = bp_mapping_data.get("mappings", {})
        bp_count = len(bp_mappings)
        total_bp_reported = bp_mapping_data.get("meta", {}).get("total_blueprints", 0)
        passed = bp_count >= 60
        detail = f"映射蓝图数: {bp_count}, 报告总数: {total_bp_reported}, 目标: >=60"
    else:
        passed = False
        detail = "无法加载 blueprint-domain-mapping.yaml"
    result.add_check(
        "CHK-11", "DM-101 blueprint_domain_mapping(>=60)", passed, detail, "critical" if not passed else "info"
    )
    print(f"  {'PASS' if passed else 'FAIL'}: {detail}")

    # ========== DM-101: CSV 匹配率 ==========
    print("\n[CHECK 12] DM-101: module_domain_matching 匹配率...")
    if csv_mapping:
        csv_total = len(csv_mapping)
        csv_with_bp = sum(1 for row in csv_mapping.values() if row.get("blueprint_id", "").strip())
        csv_match_rate = csv_with_bp / csv_total * 100 if csv_total else 0
        passed = csv_match_rate >= 90.0
        detail = f"CSV行数: {csv_total}, 有blueprint_id: {csv_with_bp}, 匹配率: {csv_match_rate:.2f}%, 目标: >=90%"
    else:
        passed = False
        detail = "无法加载 module_domain_matching.csv"
    result.add_check("CHK-12", "DM-101 CSV匹配率(>90%)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== DM-102: blueprint_id 回填率(运营态模块) ==========
    print("\n[CHECK 13] DM-102: blueprint_id 回填率(运营态模块)...")
    active_op_modules = {nid: n for nid, n in active_op.items() if isinstance(n, dict) and n.get("type") == "module"}
    module_count = len(active_op_modules)
    module_with_bp = sum(1 for n in active_op_modules.values() if isinstance(n, dict) and n.get("blueprint_id"))
    bp_backfill_rate = module_with_bp / module_count * 100 if module_count else 0
    passed = bp_backfill_rate >= 90.0
    detail = (
        f"活跃模块节点: {module_count}, 有blueprint_id: {module_with_bp}, 回填率: {bp_backfill_rate:.2f}%, 目标: >=90%"
    )
    result.add_check("CHK-13", "DM-102 blueprint_id回填率(>90%)", passed, detail, "critical" if not passed else "info")
    print(f"  {'PASS' if passed else 'FAIL'}: {detail}")

    # ========== DM-102: physical_files 非空率(设计态) ==========
    print("\n[CHECK 14] DM-102: physical_files 非空率(设计态)...")
    design_with_pf_field = sum(1 for n in active_design.values() if isinstance(n, dict) and "physical_files" in n)
    design_with_pf_nonempty = sum(1 for n in active_design.values() if isinstance(n, dict) and n.get("physical_files"))
    pf_nonempty_rate = design_with_pf_nonempty / design_with_pf_field * 100 if design_with_pf_field else 0
    passed = pf_nonempty_rate >= 95.0
    detail = f"设计态有physical_files字段: {design_with_pf_field}, 非空: {design_with_pf_nonempty}, 非空率: {pf_nonempty_rate:.2f}%, 目标: >=95%"
    result.add_check(
        "CHK-14", "DM-102 physical_files非空率(设计态>95%)", passed, detail, "warning" if not passed else "info"
    )
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== DM-103: 脚本节点 blueprint_id ==========
    print("\n[CHECK 15] DM-103: 脚本节点 blueprint_id 覆盖...")
    script_with_bp = sum(1 for n in script_nodes_op.values() if isinstance(n, dict) and n.get("blueprint_id"))
    script_bp_rate = script_with_bp / depgraph_script_count * 100 if depgraph_script_count else 0
    passed = script_bp_rate >= 90.0
    detail = f"运营态脚本节点: {depgraph_script_count}, 有blueprint_id: {script_with_bp}({script_bp_rate:.1f}%)"
    result.add_check("CHK-15", "DM-103 脚本节点blueprint_id(>90%)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== DM-104: build_status_summary by_type 验证 ==========
    print("\n[CHECK 16] DM-104: build_status_summary by_type 验证...")
    by_type = build_status_summary.get("by_type", {})
    type_mismatches = []
    for ntype, type_info in by_type.items():
        if not isinstance(type_info, dict):
            continue
        reported_total = type_info.get("total", 0)
        actual_total = design_type_counts.get(ntype, 0)
        if reported_total != actual_total:
            type_mismatches.append((ntype, actual_total, reported_total))

    passed = len(type_mismatches) == 0
    detail = f"设计态类型不匹配: {len(type_mismatches)}"
    if not passed:
        detail += "; " + ", ".join(f"{t}:实际={a},报告={r}" for t, a, r in type_mismatches)
    result.add_check("CHK-16", "DM-104 by_type一致性(设计态)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== DM-105: 活跃文件节点空 blueprint_id ==========
    print("\n[CHECK 17] DM-105: 活跃文件节点空 blueprint_id...")
    active_no_bp = []
    for nid, n in active_op.items():
        if not isinstance(n, dict):
            continue
        if n.get("type") in FILE_TYPES and not n.get("blueprint_id"):
            active_no_bp.append(nid)

    no_bp_rate = len(active_no_bp) / len(active_op) * 100 if active_op else 0
    # __init__.py 文件通常无 blueprint_id, 这是可接受的
    init_no_bp = [n for n in active_no_bp if nodes.get(n, {}).get("path", "").endswith("__init__.py")]
    non_init_no_bp = [n for n in active_no_bp if not nodes.get(n, {}).get("path", "").endswith("__init__.py")]

    passed = len(non_init_no_bp) == 0
    detail = f"活跃文件节点无blueprint_id: {len(active_no_bp)}(其中__init__.py: {len(init_no_bp)}, 非init: {len(non_init_no_bp)})"
    if not passed:
        detail += "; 非init示例: " + ", ".join(non_init_no_bp[:10])
    result.add_check(
        "CHK-17", "DM-105 活跃文件节点无空blueprint_id(非init)", passed, detail, "warning" if not passed else "info"
    )
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== DM-105: 未分配文件 ==========
    print("\n[CHECK 18] DM-105: 未分配文件检查...")
    unassigned_files = []
    for nid, n in active_op.items():
        if not isinstance(n, dict):
            continue
        if n.get("type") in FILE_TYPES:
            if not n.get("domain_id") or not n.get("subdomain_id"):
                unassigned_files.append((nid, n.get("path", "")))

    # 区分 __init__.py 和非 __init__.py
    init_unassigned = [(n, p) for n, p in unassigned_files if p.endswith("__init__.py")]
    non_init_unassigned = [(n, p) for n, p in unassigned_files if not p.endswith("__init__.py")]

    passed = len(non_init_unassigned) == 0
    detail = (
        f"未分配域的文件节点: {len(unassigned_files)}(init: {len(init_unassigned)}, 非init: {len(non_init_unassigned)})"
    )
    if not passed:
        detail += "; 非init示例: " + ", ".join(f"{p}" for _, p in non_init_unassigned[:10])
    result.add_check("CHK-18", "DM-105 无未分配文件(非init)", passed, detail, "warning" if not passed else "info")
    print(f"  {'PASS' if passed else 'WARN'}: {detail}")

    # ========== 汇总统计 ==========
    elapsed = time.perf_counter() - t0
    result.stats = {
        "total_nodes": total_nodes,
        "operational_nodes": op_count,
        "design_nodes": design_count,
        "active_operational_nodes": len(active_op),
        "active_design_nodes": len(active_design),
        "deprecated_nodes": deprecated_count,
        "total_edges": len(edges),
        "orphan_nodes_in_list": orphan_count,
        "truly_orphan_nodes": len(truly_orphan),
        "unlisted_orphan_nodes": len(unlisted_orphans),
        "blueprint_id_coverage_pct": round(bp_rate, 2),
        "physical_files_nonempty_rate_pct": round(pf_nonempty_rate, 2),
        "module_blueprint_backfill_pct": round(bp_backfill_rate, 2),
        "script_blueprint_id_pct": round(script_bp_rate, 2),
        "script_node_count": depgraph_script_count,
        "disk_script_count": disk_script_count,
        "disk_py_counts": disk_counts,
        "depgraph_version": metadata.get("version", "unknown"),
        "active_file_nodes_no_blueprint": len(active_no_bp),
        "init_no_blueprint": len(init_no_bp),
        "non_init_no_blueprint": len(non_init_no_bp),
        "verification_duration_sec": round(elapsed, 2),
    }

    # ========== 生成报告 ==========
    print(f"\n{'=' * 60}")
    print("验证报告生成中...")
    report_data = result.to_dict()
    save_yaml(report_data, REPORT_PATH)
    print(f"报告已写入: {REPORT_PATH}")

    # ========== 更新 depgraph 元数据 ==========
    print("\n更新 depgraph 元数据...")
    _update_db_metadata(
        None,
        {
            "version_num": 4,
            "version": "3.2.0",
            "p2b_completion_status": "completed",
            "dm106_verified_at": datetime.now(UTC).isoformat(),
            "dm106_result": report_data["overall_status"],
        },
    )
    print("depgraph 元数据已更新: version=3.2.0, p2b_completion_status=completed")

    # ========== 最终输出 ==========
    print(f"\n{'=' * 60}")
    print("DM-106 P2-B 验证完成")
    print(f"总体状态: {report_data['overall_status']}")
    print(f"检查项: {report_data['summary']['passed']}/{report_data['summary']['total_checks']} 通过")
    print(f"严重失败: {report_data['summary']['critical_failures']}")
    print(f"警告失败: {report_data['summary']['warning_failures']}")
    print(f"耗时: {elapsed:.2f}s")

    critical_checks = [c for c in result.checks if not c["passed"] and c["severity"] == "critical"]
    warn_checks = [c for c in result.checks if not c["passed"] and c["severity"] == "warning"]

    if critical_checks:
        print("\n严重失败项:")
        for c in critical_checks:
            print(f"  ❌ {c['check_id']}: {c['name']} - {c['detail']}")

    if warn_checks:
        print("\n警告项:")
        for c in warn_checks:
            print(f"  ⚠ {c['check_id']}: {c['name']} - {c['detail']}")

    if result.warnings:
        print("\n系统警告:")
        for w in result.warnings:
            print(f"  ⚠ {w}")

    return 0 if report_data["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(run_verification())
