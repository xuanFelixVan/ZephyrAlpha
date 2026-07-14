#!/usr/bin/env python3
"""
# [BLUEPRINT] MOD-INF-005 | scripts/governance/scan_ground_truth_deps.py | §7
# [MODULE] scripts.governance.scan_ground_truth_deps
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] Task card system; governance automation; architecture refactoring
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] Output MUST be ground-truth file-level dependency graph; every import MUST resolve to actual file; unresolved MUST be flagged
# [MODIFY-GUARD] depgraph; cross_pkg_imports_scan.json
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScanError; ResolveError
# [TESTS] tests/test_scan_ground_truth_deps.py
# [TTL] task_bound
"""

import argparse
import ast
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC
from pathlib import Path
from _shared.constants import REPO_ROOT

PROJECT_ROOT = REPO_ROOT
ZEPHYR_ROOT = PROJECT_ROOT / "src" / "zephyr"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"

EXEMPT_DIRS = {
    "__pycache__",
    ".git",
    ".ailocks",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "_backups",
    "_temp",
}

OUTPUT_DIR = PROJECT_ROOT / "data" / "asset_index"


def _file_to_module(filepath: Path, base: Path) -> str:
    rel = filepath.relative_to(base)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    elif parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def _module_to_file_candidates(module_path: str, base: Path) -> list[Path]:
    parts = module_path.split(".")
    candidates = []
    current = base
    for i, part in enumerate(parts):
        current = current / part
        if i == len(parts) - 1:
            py_file = current.with_suffix(".py")
            init_file = current / "__init__.py"
            if py_file.exists():
                candidates.append(py_file)
            if init_file.exists():
                candidates.append(init_file)
        else:
            if not current.exists():
                break
            init_file = current / "__init__.py"
            if init_file.exists():
                candidates.append(init_file)
    return candidates


def _resolve_absolute_import(module_path: str) -> dict | None:
    if module_path.startswith("zephyr."):
        rest = module_path[len("zephyr.") :]
        candidates = _module_to_file_candidates(rest, ZEPHYR_ROOT)
        if candidates:
            primary = candidates[0]
            return {
                "resolved_file": str(primary.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "resolution": "exact" if primary.suffix == ".py" and primary.name != "__init__.py" else "package_init",
                "all_candidates": [str(c.relative_to(PROJECT_ROOT)).replace("\\", "/") for c in candidates],
            }
        return {"resolved_file": None, "resolution": "unresolved", "all_candidates": []}
    elif module_path.startswith("scripts."):
        rest = module_path[len("scripts.") :]
        candidates = _module_to_file_candidates(rest, SCRIPTS_ROOT)
        if candidates:
            primary = candidates[0]
            return {
                "resolved_file": str(primary.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "resolution": "exact" if primary.suffix == ".py" and primary.name != "__init__.py" else "package_init",
                "all_candidates": [str(c.relative_to(PROJECT_ROOT)).replace("\\", "/") for c in candidates],
            }
        return {"resolved_file": None, "resolution": "unresolved", "all_candidates": []}
    return None


def _resolve_relative_import(filepath: Path, level: int, module: str | None) -> dict | None:
    try:
        rel = filepath.relative_to(ZEPHYR_ROOT)
    except ValueError:
        try:
            rel = filepath.relative_to(SCRIPTS_ROOT)
        except ValueError:
            return None

    parts = list(rel.parts)
    if parts[-1].endswith(".py"):
        parts = parts[:-1]

    for _ in range(level - 1):
        if parts:
            parts.pop()
        else:
            return {"resolved_file": None, "resolution": "unresolved_relative_overflow", "all_candidates": []}

    if module:
        parts.extend(module.split("."))

    base = ZEPHYR_ROOT if filepath.is_relative_to(ZEPHYR_ROOT) else SCRIPTS_ROOT
    full_module = ".".join(parts)
    candidates = _module_to_file_candidates(full_module, base)
    if candidates:
        primary = candidates[0]
        return {
            "resolved_file": str(primary.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "resolution": "exact" if primary.suffix == ".py" and primary.name != "__init__.py" else "package_init",
            "all_candidates": [str(c.relative_to(PROJECT_ROOT)).replace("\\", "/") for c in candidates],
        }
    return {"resolved_file": None, "resolution": "unresolved", "all_candidates": []}


def _extract_dynamic_imports(source: str, filepath: Path) -> list[dict]:
    results = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                func_name = None
                if isinstance(func, ast.Attribute) and func.attr == "import_module":
                    if isinstance(func.value, ast.Name) and func.value.id == "importlib":
                        func_name = "importlib.import_module"
                elif isinstance(func, ast.Name) and func.id == "__import__":
                    func_name = "__import__"
                if func_name and node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        results.append(
                            {
                                "type": "dynamic",
                                "function": func_name,
                                "module_arg": first_arg.value,
                                "line": node.lineno,
                            }
                        )
    except SyntaxError:
        pass
    return results


def _extract_try_except_imports(source: str) -> list[dict]:
    results = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    for child in ast.walk(handler):
                        if isinstance(child, (ast.Import, ast.ImportFrom)):
                            results.append(
                                {
                                    "type": "try_except",
                                    "line": child.lineno,
                                }
                            )
                            break
    except SyntaxError:
        pass
    return results


def scan_file(filepath: Path) -> dict:
    rel_path = str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")
    result = {
        "file": rel_path,
        "imports": [],
        "dynamic_imports": [],
        "try_except_imports": [],
        "errors": [],
    }

    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as e:
        result["errors"].append(f"SyntaxError: {e}")
        return result
    except Exception as e:
        result["errors"].append(f"ParseError: {e}")
        return result

    result["dynamic_imports"] = _extract_dynamic_imports(source, filepath)
    result["try_except_imports"] = _extract_try_except_imports(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_info = {
                    "type": "absolute",
                    "raw_module": alias.name,
                    "imported_names": [alias.name],
                    "line": node.lineno,
                    "is_internal": alias.name.startswith("zephyr") or alias.name.startswith("scripts"),
                }
                if import_info["is_internal"]:
                    resolved = _resolve_absolute_import(alias.name)
                    if resolved:
                        import_info["resolved_file"] = resolved["resolved_file"]
                        import_info["resolution"] = resolved["resolution"]
                    else:
                        import_info["resolved_file"] = None
                        import_info["resolution"] = "external"
                else:
                    import_info["resolved_file"] = None
                    import_info["resolution"] = "external"
                result["imports"].append(import_info)

        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                imported_names = [alias.name for alias in node.names] if node.names else []
                import_info = {
                    "type": "relative",
                    "level": node.level,
                    "raw_module": node.module or "",
                    "imported_names": imported_names,
                    "line": node.lineno,
                    "is_internal": True,
                }
                resolved = _resolve_relative_import(filepath, node.level, node.module)
                if resolved:
                    import_info["resolved_file"] = resolved["resolved_file"]
                    import_info["resolution"] = resolved["resolution"]
                else:
                    import_info["resolved_file"] = None
                    import_info["resolution"] = "unresolved"
                result["imports"].append(import_info)

            elif node.module and (node.module.startswith("zephyr") or node.module.startswith("scripts")):
                imported_names = [alias.name for alias in node.names] if node.names else []
                import_info = {
                    "type": "absolute",
                    "raw_module": node.module,
                    "imported_names": imported_names,
                    "line": node.lineno,
                    "is_internal": True,
                }
                resolved = _resolve_absolute_import(node.module)
                if resolved:
                    import_info["resolved_file"] = resolved["resolved_file"]
                    import_info["resolution"] = resolved["resolution"]

                    if imported_names and resolved["resolved_file"] and "__init__.py" in resolved["resolved_file"]:
                        base_for_sub = ZEPHYR_ROOT if node.module.startswith("zephyr.") else SCRIPTS_ROOT
                        rest = (
                            node.module[len("zephyr.") :]
                            if node.module.startswith("zephyr.")
                            else node.module[len("scripts.") :]
                        )
                        for name in imported_names:
                            sub_candidates = _module_to_file_candidates(rest + "." + name, base_for_sub)
                            if sub_candidates:
                                sub_primary = sub_candidates[0]
                                if sub_primary.suffix == ".py" and sub_primary.name != "__init__.py":
                                    import_info["resolved_file"] = str(sub_primary.relative_to(PROJECT_ROOT)).replace(
                                        "\\", "/"
                                    )
                                    import_info["resolution"] = "exact_submodule"
                                    break
                else:
                    import_info["resolved_file"] = None
                    import_info["resolution"] = "unresolved"
                result["imports"].append(import_info)

            elif node.module:
                imported_names = [alias.name for alias in node.names] if node.names else []
                import_info = {
                    "type": "absolute",
                    "raw_module": node.module,
                    "imported_names": imported_names,
                    "line": node.lineno,
                    "is_internal": False,
                    "resolved_file": None,
                    "resolution": "external",
                }
                result["imports"].append(import_info)

    return result


def _determine_package(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "zephyr":
        return parts[2]
    if len(parts) >= 2 and parts[0] == "scripts":
        return "scripts"
    return "unknown"


def _determine_lpc_layer(package: str) -> str:
    if package.startswith("l") and len(package) >= 3 and package[1:3].isdigit():
        return f"C-{package[:3]}"
    b_track = {
        "llm-security": "B",
        "vector-memory": "B",
        "context-engine": "B",
        "orchestrator": "B",
        "feedback-loop": "B",
        "gates": "B",
        "pipeline": "B",
        "core": "B",
        "db": "B",
        "kb": "B",
        "mcp": "B",
        "shared": "B",
        "agent-rbac": "B",
        "agent-spec": "B",
        "audit-trail": "B",
        "rollback": "B",
        "escalation-engine": "B",
        "drift-detector": "B",
        "budget-enforcer": "B",
        "a2a": "B",
        "telemetry": "B",
        "behavioral-auditor": "B",
        "behavioral-admission": "B",
        "auto-fix-engine": "B",
        "local-model": "B",
        "runtime": "B",
        "trading-contracts": "B",
        "governance": "B",
    }
    return b_track.get(package, "unknown")


def collect_py_files(scan_roots: list[Path]) -> list[Path]:
    files = []
    for root in scan_roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXEMPT_DIRS]
            for fn in filenames:
                if fn.endswith(".py"):
                    files.append(Path(dirpath) / fn)
    return sorted(files)


def build_ground_truth_graph(scan_results: list[dict]) -> dict:
    file_index = {}
    for r in scan_results:
        file_index[r["file"]] = r

    edges = []
    edge_set = set()
    for r in scan_results:
        src_file = r["file"]
        for imp in r["imports"]:
            if not imp["is_internal"]:
                continue
            tgt_file = imp.get("resolved_file")
            if not tgt_file:
                continue
            edge_key = (src_file, tgt_file)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append(
                    {
                        "source": src_file,
                        "target": tgt_file,
                        "import_type": imp["type"],
                        "resolution": imp["resolution"],
                        "imported_names": imp.get("imported_names", []),
                        "line": imp.get("line", 0),
                    }
                )

    pkg_edges = defaultdict(lambda: defaultdict(set))
    for e in edges:
        src_pkg = _determine_package(e["source"])
        tgt_pkg = _determine_package(e["target"])
        if src_pkg != tgt_pkg:
            for name in e.get("imported_names", []):
                pkg_edges[src_pkg][tgt_pkg].add(name)

    pkg_edge_list = []
    for src_pkg in sorted(pkg_edges):
        for tgt_pkg in sorted(pkg_edges[src_pkg]):
            pkg_edge_list.append(
                {
                    "source_pkg": src_pkg,
                    "target_pkg": tgt_pkg,
                    "import_count": len(pkg_edges[src_pkg][tgt_pkg]),
                    "imported_symbols": sorted(pkg_edges[src_pkg][tgt_pkg]),
                }
            )

    adjacency = defaultdict(list)
    for e in edges:
        adjacency[e["source"]].append(e["target"])
    adjacency = dict(adjacency)

    reverse_adj = defaultdict(list)
    for e in edges:
        reverse_adj[e["target"]].append(e["source"])
    reverse_adj = dict(reverse_adj)

    unresolved = []
    for r in scan_results:
        for imp in r["imports"]:
            if imp["is_internal"] and imp.get("resolution") in ("unresolved", "unresolved_relative_overflow"):
                unresolved.append(
                    {
                        "source_file": r["file"],
                        "raw_module": imp.get("raw_module", ""),
                        "type": imp["type"],
                        "line": imp.get("line", 0),
                        "resolution": imp["resolution"],
                    }
                )

    stats = {
        "total_files": len(scan_results),
        "total_imports": sum(len(r["imports"]) for r in scan_results),
        "internal_imports": sum(1 for r in scan_results for imp in r["imports"] if imp["is_internal"]),
        "external_imports": sum(1 for r in scan_results for imp in r["imports"] if not imp["is_internal"]),
        "resolved_edges": len(edges),
        "unresolved_imports": len(unresolved),
        "dynamic_imports": sum(len(r["dynamic_imports"]) for r in scan_results),
        "try_except_imports": sum(len(r["try_except_imports"]) for r in scan_results),
        "cross_pkg_edges": len(pkg_edge_list),
        "parse_errors": sum(1 for r in scan_results if r["errors"]),
    }

    return {
        "metadata": {
            "graph_id": "GROUND-TRUTH-DEPGRAPH-001",
            "version": "1.0.0",
            "scope": "全项目文件级地面实况依赖图（AST精确解析）",
            "generated_at": _now_iso(),
        },
        "stats": stats,
        "edges": edges,
        "package_edges": pkg_edge_list,
        "adjacency": adjacency,
        "reverse_adjacency": reverse_adj,
        "unresolved": unresolved,
    }


def _now_iso() -> str:
    from datetime import datetime

    return datetime.now(UTC).isoformat()


def detect_cycles(adjacency: dict) -> list[list[str]]:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(int)
    cycles = []
    path = []

    def dfs(node):
        color[node] = GRAY
        path.append(node)
        for neighbor in adjacency.get(node, []):
            if color[neighbor] == GRAY:
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:].copy())
            elif color[neighbor] == WHITE:
                dfs(neighbor)
        path.pop()
        color[node] = BLACK

    all_nodes = set(adjacency.keys())
    for targets in adjacency.values():
        all_nodes.update(targets)

    for node in sorted(all_nodes):
        if color[node] == WHITE:
            dfs(node)

    return cycles


def analyze_violations(graph: dict) -> dict:
    pkg_edges = graph["package_edges"]
    violations = {
        "c_to_c_upward": [],
        "b_to_c": [],
        "bidirectional": [],
        "c_layer_self_cycle": [],
    }

    c_layers = {}
    for e in pkg_edges:
        src, tgt = e["source_pkg"], e["target_pkg"]
        src_layer = _determine_lpc_layer(src)
        tgt_layer = _determine_lpc_layer(tgt)

        if src_layer.startswith("C-") and tgt_layer.startswith("C-"):
            src_num = int(src_layer[2:])
            tgt_num = int(tgt_layer[2:])
            if src_num > tgt_num:
                violations["c_to_c_upward"].append(e)
            if src_num == tgt_num and src == tgt:
                violations["c_layer_self_cycle"].append(e)

        if src_layer == "B" and tgt_layer.startswith("C-"):
            violations["b_to_c"].append(e)

    edge_pairs = set()
    for e in pkg_edges:
        pair = (e["source_pkg"], e["target_pkg"])
        edge_pairs.add(pair)

    for a, b in edge_pairs:
        if (b, a) in edge_pairs and a < b:
            a_to_b = [e for e in pkg_edges if e["source_pkg"] == a and e["target_pkg"] == b]
            b_to_a = [e for e in pkg_edges if e["source_pkg"] == b and e["target_pkg"] == a]
            violations["bidirectional"].append(
                {
                    "packages": (a, b),
                    "a_to_b_count": a_to_b[0]["import_count"] if a_to_b else 0,
                    "b_to_a_count": b_to_a[0]["import_count"] if b_to_a else 0,
                }
            )

    return violations


def main():
    parser = argparse.ArgumentParser(description="Ground-truth file-level dependency scanner")
    parser.add_argument("--scan-roots", nargs="+", default=["src/zephyr", "scripts"], help="Root directories to scan")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Output directory")
    parser.add_argument("--max-workers", type=int, default=8, help="ThreadPoolExecutor max workers")
    parser.add_argument(
        "--check", action="store_true", help="Check mode: compare with existing depgraph and report drift"
    )
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even if issues found (for CI non-blocking)")
    args = parser.parse_args()

    scan_root_paths = [PROJECT_ROOT / r for r in args.scan_roots]
    py_files = collect_py_files(scan_root_paths)
    print(f"[SCAN] Found {len(py_files)} .py files across {len(args.scan_roots)} roots")

    scan_results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_file, fp): fp for fp in py_files}
        for future in as_completed(futures):
            try:
                result = future.result()
                scan_results.append(result)
            except Exception as e:
                fp = futures[future]
                scan_results.append(
                    {
                        "file": str(fp.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                        "imports": [],
                        "dynamic_imports": [],
                        "try_except_imports": [],
                        "errors": [f"ScanError: {e}"],
                    }
                )

    scan_results.sort(key=lambda r: r["file"])
    print(
        f"[SCAN] Scanned {len(scan_results)} files, "
        f"{sum(len(r['imports']) for r in scan_results)} total imports, "
        f"{sum(1 for r in scan_results if r['errors'])} errors"
    )

    graph = build_ground_truth_graph(scan_results)
    stats = graph["stats"]
    print(
        f"[BUILD] Ground-truth graph: {stats['resolved_edges']} edges, "
        f"{stats['unresolved_imports']} unresolved, "
        f"{stats['cross_pkg_edges']} cross-package edges"
    )

    cycles = detect_cycles(graph["adjacency"])
    print(f"[CYCLE] Detected {len(cycles)} file-level cycles")

    violations = analyze_violations(graph)
    print(
        f"[VIOLATION] C→C upward: {len(violations['c_to_c_upward'])}, "
        f"B→C: {len(violations['b_to_c'])}, "
        f"Bidirectional: {len(violations['bidirectional'])}, "
        f"Self-cycle: {len(violations['c_layer_self_cycle'])}"
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_detail_path = output_dir / "ground_truth_file_deps.json"
    with open(file_detail_path, "w", encoding="utf-8") as f:
        json.dump(scan_results, f, ensure_ascii=False, indent=1)
    print(f"[WRITE] File-level detail → {file_detail_path}")

    graph_path = output_dir / "ground_truth_depgraph.json"
    graph_output = {
        "metadata": graph["metadata"],
        "stats": stats,
        "cycles_summary": {
            "total_cycles": len(cycles),
            "top_10_longest": sorted(cycles, key=len, reverse=True)[:10],
        },
        "violations": violations,
        "package_edges": graph["package_edges"],
        "unresolved": graph["unresolved"],
    }
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph_output, f, ensure_ascii=False, indent=1)
    print(f"[WRITE] Graph summary → {graph_path}")

    adj_path = output_dir / "ground_truth_adjacency.json"
    with open(adj_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": graph["metadata"],
                "adjacency": graph["adjacency"],
                "reverse_adjacency": graph["reverse_adjacency"],
            },
            f,
            ensure_ascii=False,
            indent=1,
        )
    print(f"[WRITE] Adjacency → {adj_path}")

    print("\n=== SUMMARY ===")
    print(f"Files scanned:        {stats['total_files']}")
    print(f"Total imports:        {stats['total_imports']}")
    print(f"Internal imports:     {stats['internal_imports']}")
    print(f"External imports:     {stats['external_imports']}")
    print(f"Resolved edges:       {stats['resolved_edges']}")
    print(f"Unresolved imports:   {stats['unresolved_imports']}")
    print(f"Dynamic imports:      {stats['dynamic_imports']}")
    print(f"Try-except imports:   {stats['try_except_imports']}")
    print(f"Cross-package edges:  {stats['cross_pkg_edges']}")
    print(f"File-level cycles:    {len(cycles)}")
    print(f"C→C upward violations:{len(violations['c_to_c_upward'])}")
    print(f"B→C violations:       {len(violations['b_to_c'])}")
    print(f"Bidirectional pairs:  {len(violations['bidirectional'])}")
    print(f"Parse errors:         {stats['parse_errors']}")

    if not args.warn_only:
        if stats["unresolved_imports"] > 0:
            print(f"\n[WARN] {stats['unresolved_imports']} unresolved internal imports found")
        if len(cycles) > 0:
            print(f"[WARN] {len(cycles)} file-level cycles detected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
