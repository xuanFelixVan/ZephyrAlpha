#!/usr/bin/env python3
# [BLUEPRINT] GOV-070 | docs/03_modules/_domain_governance/blueprint.md | §3.9
# [MODULE] scripts.governance.analyze_change_impact
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] run_incremental.py;phase_manager.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 影响分析必须包含传递依赖;增量扫描列表不可遗漏直接依赖
# [MODIFY-GUARD] 依赖图格式变更需同步generate_project_depgraph.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DependencyGraphError
# [TESTS] tests/test_analyze_change_impact.py
# [TTL] task_bound

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 治本（2026-06-27）：删除 DEFAULT_DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。

# ── _shared 模块 import bootstrap（P2迁移：复用 get_depgraph_pg_connection）──
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

PROJECT_ROOT = REPO_ROOT


def _load_depgraph_from_db(db_path: Path) -> dict:
    """从 PostgreSQL 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。

    P2迁移后：db_path 参数保留仅为向后兼容，实际连接由 get_depgraph_pg_connection 统一管理。
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

__manifest__ = """
args: []
description: 从 PostgreSQL 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""



class DependencyGraphError(Exception):
    def __init__(self, message: str, path: str = ""):
        self.path = path
        super().__init__(message)


@dataclass
class ImpactLevel:
    direct: list[str] = field(default_factory=list)
    transitive: list[str] = field(default_factory=list)
    speculative: list[str] = field(default_factory=list)


@dataclass
class ImpactResult:
    changed_files: list[str] = field(default_factory=list)
    impact: ImpactLevel = field(default_factory=ImpactLevel)
    scan_list: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    source: str = ""


class ChangeImpactAnalyzer:
    def __init__(self, repo_root: str | None = None):
        self._repo_root = Path(repo_root) if repo_root else PROJECT_ROOT
        self._depgraph: dict[str, Any] = {}
        self._adjacency_forward: dict[str, list[str]] = defaultdict(list)
        self._adjacency_reverse: dict[str, list[str]] = defaultdict(list)
        self._path_to_node: dict[str, str] = {}
        self._node_to_path: dict[str, str] = {}
        self._loaded = False

    def _load_depgraph(self) -> None:
        if self._loaded:
            return
        # 治本（2026-06-27）：depgraph 已迁至 PostgreSQL，连接由 get_depgraph_pg_connection
        # 统一管理，无文件路径概念；连接失败由下方 try/except 捕获并 fail-loud 抛错。
        try:
            self._depgraph = _load_depgraph_from_db(None)
        except Exception as exc:
            raise DependencyGraphError(
                f"Failed to load depgraph from PostgreSQL: {exc}",
                "",
            )
        self._build_adjacency()
        self._loaded = True

    def _build_adjacency(self) -> None:
        nodes = self._depgraph.get("nodes", {})
        edges = self._depgraph.get("edges", [])
        for node_id, node_data in nodes.items():
            path = node_data.get("path", "")
            self._path_to_node[path] = node_id
            self._node_to_path[node_id] = path
        for edge in edges:
            from_id = edge.get("from", "")
            to_id = edge.get("to", "")
            if from_id and to_id:
                self._adjacency_forward[from_id].append(to_id)
                self._adjacency_reverse[to_id].append(from_id)

    def analyze_file_change(self, changed_files: list[str]) -> dict[str, Any]:
        self._load_depgraph()
        impact = ImpactLevel()
        visited_direct: set[str] = set()
        visited_transitive: set[str] = set()

        for changed_file in changed_files:
            normalized = changed_file.replace("\\", "/")
            node_id = self._path_to_node.get(normalized)
            if node_id is None:
                for p, nid in self._path_to_node.items():
                    if p.endswith(normalized) or normalized.endswith(p):
                        node_id = nid
                        break
            if node_id is None:
                continue
            dependents = self._adjacency_reverse.get(node_id, [])
            for dep_id in dependents:
                dep_path = self._node_to_path.get(dep_id, dep_id)
                if dep_path not in visited_direct:
                    impact.direct.append(dep_path)
                    visited_direct.add(dep_path)
                transitive_deps = self._bfs_dependents(dep_id, visited_direct | visited_transitive)
                for td_id in transitive_deps:
                    td_path = self._node_to_path.get(td_id, td_id)
                    if td_path not in visited_transitive and td_path not in visited_direct:
                        impact.transitive.append(td_path)
                        visited_transitive.add(td_path)

            forward_deps = self._adjacency_forward.get(node_id, [])
            for fwd_id in forward_deps:
                fwd_path = self._node_to_path.get(fwd_id, fwd_id)
                if fwd_path not in visited_direct and fwd_path not in visited_transitive:
                    impact.speculative.append(fwd_path)

        risk_score = self._compute_risk_score(changed_files, impact)
        result = ImpactResult(
            changed_files=changed_files,
            impact=impact,
            risk_score=risk_score,
            source="depgraph_analysis",
        )
        result.scan_list = self.generate_incremental_scan_list(
            {"impact": {"direct": impact.direct, "transitive": impact.transitive, "speculative": impact.speculative}}
        )
        return {
            "changed_files": result.changed_files,
            "impact": {
                "direct": result.impact.direct,
                "transitive": result.impact.transitive,
                "speculative": result.impact.speculative,
            },
            "scan_list": result.scan_list,
            "risk_score": result.risk_score,
            "source": result.source,
        }

    def _bfs_dependents(self, start_id: str, exclude: set[str]) -> list[str]:
        result: list[str] = []
        queue = [start_id]
        visited: set[str] = {start_id}
        while queue:
            current = queue.pop(0)
            for dep_id in self._adjacency_reverse.get(current, []):
                if dep_id not in visited and dep_id not in exclude:
                    visited.add(dep_id)
                    result.append(dep_id)
                    queue.append(dep_id)
        return result

    def _compute_risk_score(self, changed_files: list[str], impact: ImpactLevel) -> float:
        direct_count = len(impact.direct)
        transitive_count = len(impact.transitive)
        speculative_count = len(impact.speculative)
        score = min(
            direct_count * 0.3 + transitive_count * 0.15 + speculative_count * 0.05 + len(changed_files) * 0.1,
            1.0,
        )
        return round(score, 3)

    def analyze_commit(self, commit_hash: str) -> dict[str, Any]:
        changed_files = self._get_commit_files(commit_hash)
        if not changed_files:
            return {
                "commit": commit_hash,
                "changed_files": [],
                "impact": {"direct": [], "transitive": [], "speculative": []},
                "scan_list": [],
                "risk_score": 0.0,
                "source": "commit_analysis",
            }
        result = self.analyze_file_change(changed_files)
        result["commit"] = commit_hash
        result["source"] = "commit_analysis"
        try:
            from zephyr.governance.architecture_governance.llm_impact_analyzer import LLMImpactAnalyzer

            analyzer = LLMImpactAnalyzer(project_root=self._repo_root)
            llm_result = analyzer.analyze(commit_hash)
            result["llm_risk_score"] = llm_result.risk_score
            result["llm_risk_level"] = llm_result.risk_level.value
            result["llm_recommendation"] = llm_result.recommendation
        except ImportError:
            result["llm_risk_score"] = None
            result["llm_risk_level"] = None
            result["llm_recommendation"] = None
        except Exception as exc:
            result["llm_risk_score"] = None
            result["llm_risk_level"] = None
            result["llm_recommendation"] = f"error: {exc}"
        return result

    def _get_commit_files(self, commit_hash: str) -> list[str]:
        try:
            completed = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                timeout=15,
            )
            if completed.returncode == 0 and completed.stdout.strip():
                return [line.strip() for line in completed.stdout.strip().splitlines() if line.strip()]
        except Exception:
            pass
        return []

    def generate_incremental_scan_list(self, impact: dict[str, Any]) -> list[str]:
        impact_data = impact.get("impact", impact)
        direct = impact_data.get("direct", [])
        transitive = impact_data.get("transitive", [])
        speculative = impact_data.get("speculative", [])
        scan_set: set[str] = set()
        for path in direct:
            scan_set.add(path)
            scripts = self._path_to_governance_scripts(path)
            scan_set.update(scripts)
        for path in transitive:
            scripts = self._path_to_governance_scripts(path)
            scan_set.update(scripts)
        for path in speculative:
            scripts = self._path_to_governance_scripts(path)
            scan_set.update(scripts)
        return sorted(scan_set)

    def _path_to_governance_scripts(self, file_path: str) -> list[str]:
        parts = file_path.replace("\\", "/").split("/")
        scripts: list[str] = []
        if len(parts) >= 2:
            if parts[0] == "src" and len(parts) >= 3:
                pkg = parts[2] if parts[1] == "zephyr" else parts[1]
                scripts.append("governance/d1_structure/check_module_registration.py")
                scripts.append("governance/d5_architecture/audit_depends_on_chain_depth.py")
            elif parts[0] == "scripts":
                scripts.append("governance/d1_structure/check_script_manifest.py")
            elif parts[0] == "docs":
                scripts.append("governance/d2_links/validate_blueprint_links.py")
        return scripts


def _run_warn_only() -> dict[str, Any]:
    results: dict[str, Any] = {"checks": []}
    try:
        analyzer = ChangeImpactAnalyzer()
        analyzer._load_depgraph()
        node_count = len(analyzer._path_to_node)
        results["checks"].append(
            {
                "name": "depgraph_load",
                "status": "PASS" if node_count > 0 else "WARN",
                "detail": {"nodes_loaded": node_count},
            }
        )
    except DependencyGraphError as exc:
        results["checks"].append(
            {
                "name": "depgraph_load",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    test_files = ["src/zephyr/__init__.py"]
    try:
        impact = analyzer.analyze_file_change(test_files)
        has_impact = bool(impact.get("impact", {}).get("direct") or impact.get("impact", {}).get("transitive"))
        results["checks"].append(
            {
                "name": "analyze_file_change",
                "status": "PASS",
                "detail": {"test_input": test_files, "has_impact": has_impact},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "analyze_file_change",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    try:
        scan_list = analyzer.generate_incremental_scan_list(
            {"impact": {"direct": test_files, "transitive": [], "speculative": []}}
        )
        results["checks"].append(
            {
                "name": "generate_incremental_scan_list",
                "status": "PASS",
                "detail": {"scan_list_count": len(scan_list)},
            }
        )
    except Exception as exc:
        results["checks"].append(
            {
                "name": "generate_incremental_scan_list",
                "status": "WARN",
                "detail": {"error": str(exc)},
            }
        )
    results["overall"] = "PASS" if all(c["status"] == "PASS" for c in results["checks"]) else "WARN"
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Change Impact Analyzer — transitive dependency impact analysis")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Run checks in warn-only mode",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="List of changed files to analyze",
    )
    parser.add_argument(
        "--commit",
        type=str,
        default="",
        help="Commit hash to analyze",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default="",
        help="Repository root path",
    )
    args = parser.parse_args()

    if args.warn_only:
        results = _run_warn_only()
        output_path = str(PROJECT_ROOT / "scripts" / "governance" / "analyze_change_impact_warn_result.json")
        atomic_write_safe(output_path, json.dumps(results, indent=2, default=str))
        print(json.dumps(results, indent=2, default=str))
        return 0 if results["overall"] == "PASS" else 1

    repo_root = args.repo_root or str(PROJECT_ROOT)
    analyzer = ChangeImpactAnalyzer(repo_root=repo_root)

    if args.commit:
        result = analyzer.analyze_commit(args.commit)
    elif args.files:
        result = analyzer.analyze_file_change(args.files)
    else:
        print("[CHANGE_IMPACT] No input specified. Use --files or --commit.")
        return 1

    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
