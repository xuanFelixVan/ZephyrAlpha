# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.extract_depgraph
# [DOMAIN] D_GOVERNANCE
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
[BLUEPRINT] | scripts/governance/extract_depgraph.py | §1
[MODULE] scripts.governance.extract_depgraph
[INVARIANTS] 禁止AI直接Read 157MB depgraph文件；提取输出必须可被AI安全消费
[MODIFY-GUARD] project_rules.md(RULE-SIXTEEN); scripts/governance/apply_depgraph.py
[CONSUMERS] 所有需要读取depgraph的AI session
[STABILITY] stable
[SAFETY] H
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 文件不存在→exit 1; YAML解析失败→exit 2; 无效参数→exit 3
[TESTS] 无

depgraph 巨型文件按需提取工具（RULE-SIXTEEN 强制配套）

禁止 AI 直接 Read 157MB depgraph → OOM 崩溃。
替代方案：用本脚本提取子集，AI 只读提取结果。

用法:
  python scripts/governance/extract_depgraph.py --summary          # 域摘要（域数+模块数+production_nodes）
  python scripts/governance/extract_depgraph.py --domains D_FACTOR,D_RISK  # 指定域
  python scripts/governance/extract_depgraph.py --modules D-FACTOR-01,D-RISK-03  # 指定模块
  python scripts/governance/extract_depgraph.py --top               # 顶级元数据（不含modules/nodes/edges）
  python scripts/governance/extract_depgraph.py --paths             # 所有physical_files按域分组
  python scripts/governance/extract_depgraph.py --stats             # 文件大小/行数统计
  python scripts/governance/extract_depgraph.py --output result.json  # 输出到文件（JSON格式）
  python scripts/governance/extract_depgraph.py --summary            # 摘要模式

P2 迁移后（2026-06-27 治本）：
  depgraph 已迁至 PostgreSQL，无文件路径概念。
  原 DB 新鲜度检查（基于 SQLite 文件 mtime）已删除，PG 模式下用 _schema_version 判断版本。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: depgraph 巨型文件按需提取工具（RULE-SIXTEEN 强制配套）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path


class _CustomEncoder(json.JSONEncoder):
    """Handle non-JSON-serializable types found in depgraph."""

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)


from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 治本（2026-06-27）：删除 DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()。

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
from _shared.constants import get_depgraph_pg_connection  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT


def _load_depgraph_from_db(db_path: Path | None = None) -> dict:
    """从 PostgreSQL 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。

    P2迁移后：depgraph 已迁移到 PostgreSQL。db_path 参数保留用于日志引用（治本2026-06-27：默认 None）。
    """
    conn = get_depgraph_pg_connection(autocommit=True)
    data: dict = {"nodes": {}, "edges": [], "domains": {}, "metadata": {}}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = node.pop("node_id")
        if "node_type" in node:
            node["type"] = node.pop("node_type")
        data["nodes"][nid] = node
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        if "from_node_id" in edge:
            edge["from"] = edge.pop("from_node_id")
        if "to_node_id" in edge:
            edge["to"] = edge.pop("to_node_id")
        data["edges"].append(edge)
    for row in conn.execute("SELECT * FROM domains"):
        domain = dict(row)
        did = domain.pop("domain_id")
        data["domains"][did] = domain
    conn.close()
    return data


def _load_depgraph() -> dict:
    """加载 depgraph（内部使用，不暴露给 AI）。"""
    # 治本（2026-06-27）：删除 if not DEPGRAPH_PATH.exists(): sys.exit(1) 守卫（latent bug）。
    # PG 模式下文件路径无意义，直接查询 PG；连接失败时 fail-loud 抛异常。
    try:
        return _load_depgraph_from_db()
    except Exception as e:
        print(f"ERROR: Failed to load depgraph from PostgreSQL: {e}", file=sys.stderr)
        sys.exit(2)


def _write_output(data: dict | list, output_path: str | None) -> None:
    """原子写入输出（RULE-ONE）。"""
    content = json.dumps(data, ensure_ascii=False, indent=2, cls=_CustomEncoder)
    if output_path:
        if atomic_write_safe(output_path, content):
            print(f"Output written to: {output_path}", file=sys.stderr)
    else:
        print(content)


def _build_modules_view(dep: dict) -> dict:
    """从 domains + nodes 构建兼容旧接口的 modules dict。

    DB 读取后结构：domains(dict, key=domain_id) + nodes(dict)。
    本函数将其转换为 modules 视图，
    使 cmd_summary / cmd_domains / cmd_modules / cmd_paths 无需改动。
    """
    nodes = dep.get("nodes", {})
    domains_dict = dep.get("domains", {})

    # 按 domain_id 分组 nodes
    domain_nodes: dict[str, list] = {}
    for _node_id, node in nodes.items():
        did = node.get("domain_id", "UNKNOWN")
        domain_nodes.setdefault(did, []).append(node)

    modules: dict[str, dict] = {}
    for did, fd in domains_dict.items():
        sid = fd.get("subdomain_id", did)
        items = domain_nodes.get(did, [])
        # 也按 subdomain_id 细分
        sub_items = [n for n in items if n.get("subdomain_id", n.get("domain_id")) == sid]
        # 如果 subdomain 细分后为空，使用整个 domain 的 items
        if not sub_items:
            sub_items = items
        key = did  # 用 domain_id 作为 key
        if key not in modules:
            modules[key] = {
                "domain_name": fd.get("domain_name", ""),
                "domain_short": did,
                "items": [],
            }
        for n in sub_items:
            modules[key]["items"].append(
                {
                    "module_id": n.get("belongs_to") or n.get("blueprint_id", ""),
                    "name": n.get("path", "").split("/")[-1] if n.get("path") else "",
                    "path": n.get("path", ""),
                    "physical_files": [n.get("path", "")] if n.get("path") else [],
                    "build_status": n.get("build_status", "unknown"),
                    "blueprint_status": n.get("blueprint_id", "unknown"),
                }
            )
    return modules


def _count_production_nodes_per_domain(dep: dict) -> dict[str, int]:
    """统计每个域的 production 节点数（ARCH-CAP-001 模块定义口径）。

    production 节点 = design_maturity='production' 的真实代码文件。
    design/prototype 节点不计入模块容量（trae_055 ARCH-CAP-001）。
    """
    counts: dict[str, int] = {}
    for _node_id, node in dep.get("nodes", {}).items():
        if node.get("design_maturity") == "production":
            did = node.get("domain_id", "UNKNOWN")
            counts[did] = counts.get(did, 0) + 1
    return counts


def cmd_summary(dep: dict, output: str | None) -> None:
    """域摘要：域名称 + 模块数 + production_nodes + 路径前缀。

    ARCH-CAP-001 要求按 production 节点口径统计模块数。
    production_nodes = design_maturity='production' 的节点数（真实代码文件）。
    module_count = 全节点数（含 design+prototype，向后兼容保留）。
    """
    modules = _build_modules_view(dep)
    production_counts = _count_production_nodes_per_domain(dep)
    result = {
        "total_domains": len(modules),
        "total_modules": 0,
        "total_production_nodes": 0,
        "domains": [],
    }
    for domain_name, domain_data in modules.items():
        items = domain_data.get("items", [])
        count = len(items)
        result["total_modules"] += count
        prod_count = production_counts.get(domain_name, 0)
        result["total_production_nodes"] += prod_count
        paths = list(set(item.get("path", "") for item in items if item.get("path")))
        result["domains"].append(
            {
                "domain": domain_name,
                "domain_name": domain_data.get("domain_name", ""),
                "module_count": count,
                "production_nodes": prod_count,
                "paths": sorted(paths)[:10],
            }
        )
    _write_output(result, output)


def cmd_domains(dep: dict, domain_names: list[str], output: str | None) -> None:
    """提取指定域的完整模块数据。"""
    modules = _build_modules_view(dep)
    result = {}
    for domain_name in domain_names:
        if domain_name not in modules:
            print(f"WARNING: Domain '{domain_name}' not found in depgraph", file=sys.stderr)
            continue
        domain_data = modules[domain_name]
        result[domain_name] = {
            "domain_name": domain_data.get("domain_name", ""),
            "domain_short": domain_data.get("domain_short", ""),
            "module_count": len(domain_data.get("items", [])),
            "items": domain_data.get("items", []),
        }
    _write_output(result, output)


def cmd_modules(dep: dict, module_ids: list[str], output: str | None) -> None:
    """提取指定 module_id 的完整数据（含该模块下所有文件节点）。

    修复: 原实现找到首个匹配就 break，只返回 1 个文件。
    现在: 收集所有匹配的文件节点，返回完整文件列表。
    """
    modules = _build_modules_view(dep)
    result = {}
    for module_id in module_ids:
        found_items = []
        for domain_name, domain_data in modules.items():
            for item in domain_data.get("items", []):
                if item.get("module_id") == module_id:
                    found_items.append(item)
        if found_items:
            result[module_id] = {
                "module_id": module_id,
                "file_count": len(found_items),
                "files": found_items,
            }
        else:
            print(f"WARNING: Module '{module_id}' not found in depgraph", file=sys.stderr)
    _write_output(result, output)


def cmd_top(dep: dict, output: str | None) -> None:
    """顶级元数据：不含 modules/nodes/edges 等重量级数据。"""
    heavy_keys = {
        "modules",
        "nodes",
        "edges",
        "module_edges",
        "domain_edges",
        "adjacency_forward",
        "adjacency_reverse",
        "file_index",
        "module_index",
        "most_depended_upon",
        "orphan_nodes",
        "gated_modules",
    }
    result = {k: v for k, v in dep.items() if k not in heavy_keys}
    _write_output(result, output)


def cmd_paths(dep: dict, output: str | None, domain_filter: list[str] | None = None) -> None:
    """所有 physical_files 按域分组。可选 domain_filter 限制域。"""
    modules = _build_modules_view(dep)
    result = {}
    total_files = 0
    for domain_name, domain_data in modules.items():
        if domain_filter and domain_name not in domain_filter:
            continue
        domain_files = []
        for item in domain_data.get("items", []):
            for pf in item.get("physical_files", []):
                domain_files.append(
                    {
                        "module_id": item.get("module_id", ""),
                        "module_name": item.get("name", ""),
                        "path": pf,
                        "build_status": item.get("build_status", "unknown"),
                        "blueprint_status": item.get("blueprint_status", "unknown"),
                    }
                )
        result[domain_name] = {
            "file_count": len(domain_files),
            "files": domain_files,
        }
        total_files += len(domain_files)
    result["_total_files"] = total_files
    _write_output(result, output)


def cmd_stats(dep_path: Path, output: str | None) -> None:
    """数据库统计（P2迁移后：depgraph 已迁至 PostgreSQL，size 来自 pg_database_size）。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    size_bytes = conn.execute("SELECT pg_database_size(current_database()) AS sz").fetchone()["sz"]
    node_count = conn.execute("SELECT COUNT(*) AS cnt FROM nodes").fetchone()["cnt"]
    edge_count = conn.execute("SELECT COUNT(*) AS cnt FROM edges").fetchone()["cnt"]
    domain_count = conn.execute("SELECT COUNT(*) AS cnt FROM domains").fetchone()["cnt"]
    conn.close()
    result = {
        "path": str(dep_path),
        "size_mb": round(size_bytes / 1024 / 1024, 1),
        "size_bytes": size_bytes,
        "node_count": node_count,
        "edge_count": edge_count,
        "domain_count": domain_count,
        "estimated_tokens": size_bytes // 3,
    }
    _write_output(result, output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="depgraph 按需提取工具（禁止AI直接Read 157MB文件）",
        epilog="""场景速查：
  模块属于哪个域           → --paths（按域分组列出所有文件路径）
  域有哪些模块             → --domains D-XXX
  模块的物理路径           → --modules MOD-XXX
  项目全景摘要             → --summary
  文件大小/行数统计        → --stats

See .trae/rules/project_rules.md RULE-SIXTEEN for the full protocol.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--summary", action="store_true", help="域摘要（域数+模块数+production_nodes+路径前缀）")
    parser.add_argument("--domains", type=str, help="指定域（逗号分隔），如 D_FACTOR,D_RISK")
    parser.add_argument("--modules", type=str, help="指定 module_id（逗号分隔），如 D-FACTOR-01")
    parser.add_argument("--top", action="store_true", help="顶级元数据（不含 modules/nodes/edges）")
    parser.add_argument("--paths", action="store_true", help="所有 physical_files 按域分组")
    parser.add_argument("--stats", action="store_true", help="文件大小/行数统计")
    parser.add_argument("--output", type=str, help="输出到 JSON 文件（默认 stdout）")
    args = parser.parse_args()

    # 至少选一个模式
    if not any([args.summary, args.domains, args.modules, args.top, args.paths, args.stats]):
        parser.print_help()
        print("\nERROR: Must specify at least one extraction mode.", file=sys.stderr)
        sys.exit(3)

    if args.stats:
        cmd_stats(None, args.output)
        return

    dep = _load_depgraph()

    domain_filter = [d.strip() for d in args.domains.split(",")] if args.domains else None

    if args.summary:
        cmd_summary(dep, args.output)
    if args.domains:
        cmd_domains(dep, domain_filter, args.output)
    if args.modules:
        cmd_modules(dep, [m.strip() for m in args.modules.split(",")], args.output)
    if args.top:
        cmd_top(dep, args.output)
    if args.paths:
        cmd_paths(dep, args.output, domain_filter)


if __name__ == "__main__":
    main()
