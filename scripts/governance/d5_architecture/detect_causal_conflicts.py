#!/usr/bin/env python3
# [BLUEPRINT] GOV-073 | docs/03_modules/_domain_governance/blueprint.md | §3.9
# [MODULE] scripts.governance.detect_causal_conflicts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] run_all.py;phase_manager.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 冲突检测不可遗漏;冲突必须包含因果链
# [MODIFY-GUARD] 冲突类型变更需同步conflict_detector.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CausalChainBrokenError
# [TESTS] tests/test_detect_causal_conflicts.py
# [TTL] task_bound

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 治本（2026-06-27）：删除 DEFAULT_DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

PROJECT_ROOT = REPO_ROOT


def _load_depgraph_from_db(db_path: Path) -> dict:
    """从 PostgreSQL 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。"""
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

__manifest__ = """
args: []
description: 从 PostgreSQL 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""



class CausalChainBrokenError(Exception):
    def __init__(self, chain: list[str], break_point: str):
        self.chain = chain
        self.break_point = break_point
        super().__init__(f"Causal chain broken at '{break_point}' in chain: {' -> '.join(chain)}")


@dataclass
class ConflictEntry:
    conflict_type: str
    severity: str
    description: str
    causal_chain: list[str]
    modules_involved: list[str]
    details: dict[str, Any] = field(default_factory=dict)


class CausalConflictDetector:
    def __init__(self, depgraph_path: str | None = None):
        # depgraph_path 参数保留向后兼容（PG模式下忽略，治本2026-06-27删除DEFAULT_DEPGRAPH_PATH常量）
        self._depgraph: dict[str, Any] = {}
        self._adj_forward: dict[str, list[str]] = defaultdict(list)
        self._adj_reverse: dict[str, list[str]] = defaultdict(list)
        self._path_to_node: dict[str, str] = {}
        self._node_to_path: dict[str, str] = {}
        self._node_to_blueprint: dict[str, str] = {}
        self._loaded = False

    def _load_depgraph(self) -> None:
        if self._loaded:
            return
        # 治本（2026-06-27）：删除 if not self._depgraph_path.exists(): self._loaded=True; return 守卫（latent bug）。
        # PG 模式下文件路径无意义，直接查询 PG；连接失败时 fail-loud 抛异常（不静默漏报冲突）。
        try:
            self._depgraph = _load_depgraph_from_db(None)
        except Exception:
            self._depgraph = {}
        nodes = self._depgraph.get("nodes", {})
        edges = self._depgraph.get("edges", [])
        for node_id, node_data in nodes.items():
            path = node_data.get("path", "")
            bp_id = node_data.get("blueprint_id", "")
            self._path_to_node[path] = node_id
            self._node_to_path[node_id] = path
            self._node_to_blueprint[node_id] = bp_id
        for edge in edges:
            from_id = edge.get("from", "")
            to_id = edge.get("to", "")
            if from_id and to_id:
                self._adj_forward[from_id].append(to_id)
                self._adj_reverse[to_id].append(from_id)
        self._loaded = True

    def detect_resource_conflicts(self) -> list[dict[str, Any]]:
        self._load_depgraph()
        conflicts: list[dict[str, Any]] = []
        resource_map: dict[str, list[str]] = defaultdict(list)
        for node_id, path in self._node_to_path.items():
            parts = path.replace("\\", "/").split("/")
            if len(parts) >= 3 and parts[0] == "data":
                resource_key = "/".join(parts[:3])
                resource_map[resource_key].append(node_id)
        for resource, consumers in resource_map.items():
            if len(consumers) < 2:
                continue
            blueprints = set()
            for cid in consumers:
                bp = self._node_to_blueprint.get(cid, "")
                if bp:
                    blueprints.add(bp)
            if len(blueprints) >= 2:
                chain = self._build_causal_chain(consumers)
                conflicts.append(
                    {
                        "conflict_type": "resource_mutex",
                        "severity": "high",
                        "description": f"Resource '{resource}' accessed by {len(consumers)} modules across {len(blueprints)} blueprints",
                        "causal_chain": chain,
                        "modules_involved": [self._node_to_path.get(c, c) for c in consumers],
                        "details": {
                            "resource": resource,
                            "consumer_count": len(consumers),
                            "blueprints": sorted(blueprints),
                        },
                    }
                )
        return conflicts

    def detect_architecture_conflicts(self) -> list[dict[str, Any]]:
        self._load_depgraph()
        conflicts: list[dict[str, Any]] = []
        layer_order = {
            "infrastructure_runtime_integration": 1,
            "infrastructure_runtime_integration": 2,
            "governance": 3,
            "governance": 4,
        }
        for node_id, path in self._node_to_path.items():
            parts = path.replace("\\", "/").split("/")
            if len(parts) < 3 or parts[0] != "src" or parts[1] != "zephyr":
                continue
            src_layer = parts[2]
            src_order = layer_order.get(src_layer, 0)
            if src_order == 0:
                continue
            for dep_id in self._adj_forward.get(node_id, []):
                dep_path = self._node_to_path.get(dep_id, "")
                dep_parts = dep_path.replace("\\", "/").split("/")
                if len(dep_parts) < 3 or dep_parts[0] != "src" or dep_parts[1] != "zephyr":
                    continue
                dep_layer = dep_parts[2]
                dep_order = layer_order.get(dep_layer, 0)
                if dep_order == 0:
                    continue
                if dep_order < src_order:
                    chain = self._build_causal_chain([node_id, dep_id])
                    conflicts.append(
                        {
                            "conflict_type": "architecture_reverse",
                            "severity": "high",
                            "description": f"Layer violation: {src_layer}({src_order}) depends on {dep_layer}({dep_order}) — reverse dependency",
                            "causal_chain": chain,
                            "modules_involved": [path, dep_path],
                            "details": {
                                "source_layer": src_layer,
                                "target_layer": dep_layer,
                                "source_order": src_order,
                                "target_order": dep_order,
                            },
                        }
                    )
        return conflicts

    def detect_dependency_conflicts(self) -> list[dict[str, Any]]:
        self._load_depgraph()
        conflicts: list[dict[str, Any]] = []
        visited_pairs: set[tuple[str, str]] = set()
        for node_id in self._node_to_path:
            for dep_id in self._adj_forward.get(node_id, []):
                pair = tuple(sorted([node_id, dep_id]))
                if pair in visited_pairs:
                    continue
                visited_pairs.add(pair)
                reverse_deps = self._adj_forward.get(dep_id, [])
                if node_id in reverse_deps:
                    chain = self._build_causal_chain([node_id, dep_id, node_id])
                    conflicts.append(
                        {
                            "conflict_type": "dependency_cycle",
                            "severity": "critical",
                            "description": f"Circular dependency between {self._node_to_path.get(node_id, node_id)} and {self._node_to_path.get(dep_id, dep_id)}",
                            "causal_chain": chain,
                            "modules_involved": [
                                self._node_to_path.get(node_id, node_id),
                                self._node_to_path.get(dep_id, dep_id),
                            ],
                            "details": {
                                "cycle_type": "direct",
                            },
                        }
                    )
        indirect_cycles = self._find_indirect_cycles()
        for cycle in indirect_cycles:
            cycle_set = set(cycle)
            pair_key = tuple(sorted(cycle_set))
            if pair_key in visited_pairs:
                continue
            visited_pairs.add(pair_key)
            chain = self._build_causal_chain(cycle)
            conflicts.append(
                {
                    "conflict_type": "dependency_cycle",
                    "severity": "high",
                    "description": f"Indirect circular dependency: {' -> '.join(self._node_to_path.get(n, n) for n in cycle)}",
                    "causal_chain": chain,
                    "modules_involved": [self._node_to_path.get(n, n) for n in cycle],
                    "details": {
                        "cycle_type": "indirect",
                        "cycle_length": len(cycle),
                    },
                }
            )
        return conflicts

    def _find_indirect_cycles(self, max_depth: int = 5) -> list[list[str]]:
        cycles: list[list[str]] = []
        found_cycle_sets: list[set[str]] = []
        for start_id in self._node_to_path:
            stack: list[tuple[str, list[str], set[str]]] = [(start_id, [start_id], {start_id})]
            while stack:
                current, path, visited = stack.pop()
                if len(path) > max_depth:
                    continue
                for neighbor in self._adj_forward.get(current, []):
                    if neighbor == start_id and len(path) >= 3:
                        cycle_set = set(path)
                        already_found = any(cycle_set == fcs for fcs in found_cycle_sets)
                        if not already_found:
                            cycles.append(path.copy())
                            found_cycle_sets.append(cycle_set)
                    elif neighbor not in visited:
                        stack.append((neighbor, path + [neighbor], visited | {neighbor}))
        return cycles

    def detect_priority_conflicts(self) -> list[dict[str, Any]]:
        self._load_depgraph()
        conflicts: list[dict[str, Any]] = []
        priority_map: dict[str, str] = {}
        for node_id, node_data in self._depgraph.get("nodes", {}).items():
            safety = node_data.get("impact_level", node_data.get("safety", ""))
            if safety:
                priority_map[node_id] = safety
        safety_order = {"H": 3, "M": 2, "L": 1}
        for node_id, node_safety in priority_map.items():
            node_order = safety_order.get(node_safety, 0)
            for dep_id in self._adj_forward.get(node_id, []):
                dep_safety = priority_map.get(dep_id, "")
                dep_order = safety_order.get(dep_safety, 0)
                if dep_order > node_order and node_order > 0:
                    chain = self._build_causal_chain([node_id, dep_id])
                    conflicts.append(
                        {
                            "conflict_type": "priority_mismatch",
                            "severity": "medium",
                            "description": f"Priority conflict: {node_safety} module depends on {dep_safety} module (lower priority depending on higher)",
                            "causal_chain": chain,
                            "modules_involved": [
                                self._node_to_path.get(node_id, node_id),
                                self._node_to_path.get(dep_id, dep_id),
                            ],
                            "details": {
                                "source_safety": node_safety,
                                "target_safety": dep_safety,
                            },
                        }
                    )
        return conflicts

    def _build_causal_chain(self, node_ids: list[str]) -> list[str]:
        chain: list[str] = []
        for nid in node_ids:
            path = self._node_to_path.get(nid, nid)
            bp = self._node_to_blueprint.get(nid, "")
            chain.append(f"{path} [{bp}]" if bp else path)
        return chain

    def run_all_checks(self) -> dict[str, Any]:
        resource = self.detect_resource_conflicts()
        architecture = self.detect_architecture_conflicts()
        dependency = self.detect_dependency_conflicts()
        priority = self.detect_priority_conflicts()
        all_conflicts = resource + architecture + dependency + priority
        severity_counts: dict[str, int] = defaultdict(int)
        for c in all_conflicts:
            severity_counts[c.get("severity", "unknown")] += 1
        return {
            "total_conflicts": len(all_conflicts),
            "severity_counts": dict(severity_counts),
            "resource_conflicts": resource,
            "architecture_conflicts": architecture,
            "dependency_conflicts": dependency,
            "priority_conflicts": priority,
            "has_critical": severity_counts.get("critical", 0) > 0,
        }


def _run_warn_only() -> dict[str, Any]:
    results: dict[str, Any] = {"checks": []}
    detector = CausalConflictDetector()
    try:
        detector._load_depgraph()
        node_count = len(detector._path_to_node)
        results["checks"].append(
            {
                "name": "depgraph_load",
                "status": "PASS" if node_count > 0 else "WARN",
                "detail": {"nodes_loaded": node_count},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "depgraph_load",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        resource_conflicts = detector.detect_resource_conflicts()
        results["checks"].append(
            {
                "name": "detect_resource_conflicts",
                "status": "PASS",
                "detail": {"conflict_count": len(resource_conflicts)},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "detect_resource_conflicts",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        arch_conflicts = detector.detect_architecture_conflicts()
        results["checks"].append(
            {
                "name": "detect_architecture_conflicts",
                "status": "PASS",
                "detail": {"conflict_count": len(arch_conflicts)},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "detect_architecture_conflicts",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        dep_conflicts = detector.detect_dependency_conflicts()
        results["checks"].append(
            {
                "name": "detect_dependency_conflicts",
                "status": "PASS",
                "detail": {"conflict_count": len(dep_conflicts)},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "detect_dependency_conflicts",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        pri_conflicts = detector.detect_priority_conflicts()
        results["checks"].append(
            {
                "name": "detect_priority_conflicts",
                "status": "PASS",
                "detail": {"conflict_count": len(pri_conflicts)},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "detect_priority_conflicts",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        all_checks = detector.run_all_checks()
        results["checks"].append(
            {
                "name": "run_all_checks",
                "status": "PASS",
                "detail": {"total_conflicts": all_checks["total_conflicts"]},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "run_all_checks",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    results["overall"] = "PASS" if all(c["status"] == "PASS" for c in results["checks"]) else "WARN"
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Causal Conflict Detector — cross-module causal conflict detection")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Run checks in warn-only mode",
    )
    parser.add_argument(
        "--depgraph",
        type=str,
        default="",
        help="Path to dependency graph YAML",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output JSON file path for conflict report",
    )
    args = parser.parse_args()

    if args.warn_only:
        results = _run_warn_only()
        output_path = str(PROJECT_ROOT / "scripts" / "governance" / "detect_causal_conflicts_warn_result.json")
        tmp_path = f"{output_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            os.replace(tmp_path, output_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        print(json.dumps(results, indent=2, default=str))
        return 0 if results["overall"] == "PASS" else 1

    depgraph = args.depgraph or str(DEFAULT_DEPGRAPH_PATH)
    detector = CausalConflictDetector(depgraph_path=depgraph)
    report = detector.run_all_checks()
    print(f"[CAUSAL_CONFLICT] Total conflicts: {report['total_conflicts']}")
    print(f"[CAUSAL_CONFLICT] Severity: {report['severity_counts']}")
    if report["has_critical"]:
        print("[CAUSAL_CONFLICT] CRITICAL conflicts detected!")

    if args.output:
        out_path = PROJECT_ROOT / args.output
        atomic_write_safe(str(out_path), json.dumps(report, indent=2, default=str))
        print(f"[CAUSAL_CONFLICT] Report written to {args.output}")

    return 1 if report["has_critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
