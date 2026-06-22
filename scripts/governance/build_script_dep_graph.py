#!/usr/bin/env python3
# [BLUEPRINT] GOV-071 | docs/03_modules/_domain-governance/blueprint.md | §3.9
# [MODULE] scripts.governance.build_script_dep_graph
# [INVARIANTS] DAG不可有循环;拓扑排序必须完整
# [MODIFY-GUARD] manifest格式变更需同步scaffold.py
# [CONSUMERS] run_all.py;run_incremental.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CyclicDependencyError
# [TESTS] tests/test_build_script_dep_graph.py

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "scripts" / "script_manifest.yaml"


class CyclicDependencyError(Exception):
    def __init__(self, cycles: list[list[str]]):
        self.cycles = cycles
        cycle_strs = [" -> ".join(c + [c[0]]) for c in cycles]
        super().__init__(f"Cyclic dependencies detected: {cycle_strs}")


@dataclass
class ScriptNode:
    name: str
    path: str = ""
    depends_on: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    level: int = -1


class ScriptDepGraph:
    def __init__(self, manifest_path: str | None = None):
        self._manifest_path = Path(manifest_path) if manifest_path else DEFAULT_MANIFEST_PATH
        self._nodes: dict[str, ScriptNode] = {}
        self._adj_forward: dict[str, list[str]] = defaultdict(list)
        self._adj_reverse: dict[str, list[str]] = defaultdict(list)
        self._built = False

    def build_dag(self) -> dict[str, Any]:
        self._load_manifest()
        self._extract_import_dependencies()
        self._build_adjacency()
        self._built = True
        return {
            "total_scripts": len(self._nodes),
            "total_edges": sum(len(v) for v in self._adj_forward.values()),
            "nodes": {
                name: {"path": n.path, "depends_on": n.depends_on, "imports": n.imports}
                for name, n in self._nodes.items()
            },
            "edges": [{"from": src, "to": dst} for src, dsts in self._adj_forward.items() for dst in dsts],
        }

    def _load_manifest(self) -> None:
        if not self._manifest_path.exists():
            return
        try:
            import yaml

            with open(str(self._manifest_path), encoding="utf-8") as f:
                manifest = yaml.safe_load(f) or {}
        except ImportError:
            manifest = self._load_manifest_json_fallback()
        except Exception:
            return
        scripts = manifest.get("scripts", [])
        for entry in scripts:
            name = entry.get("name", "")
            path = entry.get("path", "")
            if not name:
                continue
            depends_on = entry.get("depends_on_scripts", [])
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            self._nodes[name] = ScriptNode(
                name=name,
                path=path,
                depends_on=depends_on if isinstance(depends_on, list) else [],
            )

    def _load_manifest_json_fallback(self) -> dict[str, Any]:
        json_path = self._manifest_path.with_suffix(".json")
        if json_path.exists():
            with open(str(json_path), encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _extract_import_dependencies(self) -> None:
        for name, node in self._nodes.items():
            if not node.path:
                continue
            script_file = PROJECT_ROOT / "scripts" / node.path
            if not script_file.exists():
                continue
            try:
                with open(str(script_file), encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source, filename=str(script_file))
                for ast_node in ast.walk(tree):
                    if isinstance(ast_node, ast.Import):
                        for alias in ast_node.names:
                            if alias.name.startswith("scripts"):
                                node.imports.append(alias.name)
                    elif isinstance(ast_node, ast.ImportFrom):
                        if ast_node.module and ast_node.module.startswith("scripts"):
                            node.imports.append(ast_node.module)
            except Exception:
                pass

    def _build_adjacency(self) -> None:
        for name, node in self._nodes.items():
            for dep in node.depends_on:
                if dep in self._nodes:
                    self._adj_forward[name].append(dep)
                    self._adj_reverse[dep].append(name)
            for imp in node.imports:
                imp_parts = imp.split(".")
                if len(imp_parts) >= 2:
                    candidate = imp_parts[1] if imp_parts[0] == "scripts" else imp
                    if candidate in self._nodes and candidate != name:
                        if candidate not in self._adj_forward[name]:
                            self._adj_forward[name].append(candidate)
                            self._adj_reverse[candidate].append(name)

    def topological_sort(self) -> list[str]:
        if not self._built:
            self.build_dag()
        in_degree: dict[str, int] = defaultdict(int)
        for name in self._nodes:
            in_degree.setdefault(name, 0)
        for src, dsts in self._adj_forward.items():
            for dst in dsts:
                in_degree[dst] += 1
        queue = deque(sorted([n for n in self._nodes if in_degree[n] == 0]))
        result: list[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for dep in sorted(self._adj_forward.get(node, [])):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        if len(result) != len(self._nodes):
            remaining = set(self._nodes.keys()) - set(result)
            cycles = self._find_cycles_in(remaining)
            raise CyclicDependencyError(cycles)
        return result

    def detect_cycles(self) -> list[list[str]]:
        if not self._built:
            self.build_dag()
        return self._find_cycles_in(set(self._nodes.keys()))

    def _find_cycles_in(self, node_set: set[str]) -> list[list[str]]:
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def _dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in self._adj_forward.get(node, []):
                if neighbor not in node_set:
                    continue
                if neighbor not in visited:
                    _dfs(neighbor)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    cycles.append(cycle.copy())
            path.pop()
            rec_stack.discard(node)

        for node in sorted(node_set):
            if node not in visited:
                _dfs(node)
        return cycles

    def get_dependencies(self, script_name: str) -> list[str]:
        if not self._built:
            self.build_dag()
        return list(self._adj_forward.get(script_name, []))

    def get_dependents(self, script_name: str) -> list[str]:
        if not self._built:
            self.build_dag()
        return list(self._adj_reverse.get(script_name, []))

    def get_execution_levels(self) -> list[list[str]]:
        if not self._built:
            self.build_dag()
        in_degree: dict[str, int] = defaultdict(int)
        for name in self._nodes:
            in_degree.setdefault(name, 0)
        for src, dsts in self._adj_forward.items():
            for dst in dsts:
                in_degree[dst] += 1
        levels: list[list[str]] = []
        remaining = set(self._nodes.keys())
        current_level = sorted([n for n in remaining if in_degree[n] == 0])
        while current_level:
            levels.append(current_level)
            for node in current_level:
                remaining.discard(node)
                for dep in self._adj_forward.get(node, []):
                    in_degree[dep] -= 1
            current_level = sorted([n for n in remaining if in_degree[n] == 0])
        if remaining:
            cycles = self._find_cycles_in(remaining)
            raise CyclicDependencyError(cycles)
        return levels


def _run_warn_only() -> dict[str, Any]:
    results: dict[str, Any] = {"checks": []}
    graph = ScriptDepGraph()
    try:
        dag = graph.build_dag()
        results["checks"].append(
            {
                "name": "build_dag",
                "status": "PASS",
                "detail": {"total_scripts": dag["total_scripts"], "total_edges": dag["total_edges"]},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "build_dag",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
        results["overall"] = "WARN"
        return results
    try:
        topo = graph.topological_sort()
        results["checks"].append(
            {
                "name": "topological_sort",
                "status": "PASS" if len(topo) == dag["total_scripts"] else "WARN",
                "detail": {"sorted_count": len(topo), "expected": dag["total_scripts"]},
            }
        )
    except CyclicDependencyError as exc:
        results["checks"].append(
            {
                "name": "topological_sort",
                "status": "WARN",
                "detail": {"error": str(exc), "cycles": exc.cycles},
            }
        )
    try:
        cycles = graph.detect_cycles()
        results["checks"].append(
            {
                "name": "detect_cycles",
                "status": "PASS" if len(cycles) == 0 else "WARN",
                "detail": {"cycle_count": len(cycles)},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "detect_cycles",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        levels = graph.get_execution_levels()
        results["checks"].append(
            {
                "name": "get_execution_levels",
                "status": "PASS" if len(levels) > 0 else "WARN",
                "detail": {"level_count": len(levels)},
            }
        )
    except CyclicDependencyError as exc:
        results["checks"].append(
            {
                "name": "get_execution_levels",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    results["overall"] = "PASS" if all(c["status"] == "PASS" for c in results["checks"]) else "WARN"
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Script Dependency Graph — DAG construction and topological sort")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Run checks in warn-only mode",
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="",
        help="Path to script manifest YAML",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output JSON file path for DAG data",
    )
    args = parser.parse_args()

    if args.warn_only:
        results = _run_warn_only()
        output_path = str(PROJECT_ROOT / "scripts" / "governance" / "build_script_dep_graph_warn_result.json")
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

    manifest = args.manifest or str(DEFAULT_MANIFEST_PATH)
    graph = ScriptDepGraph(manifest_path=manifest)
    dag = graph.build_dag()
    print(f"[DEP_GRAPH] Built DAG: {dag['total_scripts']} scripts, {dag['total_edges']} edges")

    try:
        topo = graph.topological_sort()
        print(f"[DEP_GRAPH] Topological sort: {len(topo)} scripts")
    except CyclicDependencyError as exc:
        print(f"[DEP_GRAPH] CYCLE DETECTED: {exc}")
        return 1

    cycles = graph.detect_cycles()
    if cycles:
        print(f"[DEP_GRAPH] WARNING: {len(cycles)} cycles detected")
    else:
        print("[DEP_GRAPH] No cycles detected")

    levels = graph.get_execution_levels()
    print(f"[DEP_GRAPH] Execution levels: {len(levels)}")
    for i, level in enumerate(levels):
        print(f"  Level {i}: {len(level)} scripts")

    if args.output:
        output_data = {
            "dag": dag,
            "topological_order": topo,
            "cycles": cycles,
            "execution_levels": levels,
        }
        out_path = PROJECT_ROOT / args.output
        tmp_path = f"{out_path!s}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, default=str)
            os.replace(tmp_path, str(out_path))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        print(f"[DEP_GRAPH] Output written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
