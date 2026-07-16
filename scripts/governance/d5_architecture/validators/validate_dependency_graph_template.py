# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_dependency_graph_template
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [TTL] permanent
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.validators.validate_dependency_graph_template
[INVARIANTS] 治理脚本执行正确
[MODIFY-GUARD] __init__.py;script_manifest.yaml
[CONSUMERS] CI pipeline;governance gate
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] sys.exit(1)
[TESTS] tests/governance/test_d5_architecture.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 依赖图模板合规验证（TPL-DEPGRAPH-001 v4.0.0 — D5架构一致性）
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

REQUIRED_SECTIONS = ["graph_id", "nodes", "edges", "adjacency", "properties", "compositions", "constraints"]

NODE_REQUIRED_FIELDS = ["node_id", "type", "layer", "change_policy", "impact_level"]

EDGE_REQUIRED_FIELDS = ["edge_id", "from", "to", "dep_type", "strength", "direction"]

NODE_TYPES = {  # noqa: gate-vocab  node_type 枚举，非 file_category
    "application",
    "module",
    "package",
    "script",
    "service",
    "library",
    "config",
    "data",
    "gate",
    "domain",
    "aggregate",
}

LAYERS = {
    "L0_infrastructure",
    "L1_foundation",
    "L2_domain",
    "L3_application",
    "shared",
    "contracts",
    "meta",
    "domain_integration",
}

DEP_TYPES = {  # noqa: gate-vocab  模板允许的 dep_type 子集（10/12，排除 references/owned_by）
    "import_depends",
    "blueprint_depends",
    "script_depends",
    "data_depends",
    "runtime_depends",
    "config_depends",
    "test_depends",
    "event_depends",
    "contract_depends",
    "shared_kernel",
}

STRENGTHS = {"hard", "soft", "optional", "event_driven", "conditional"}

DIRECTIONS = {"inward", "outward", "lateral"}

COMPLETENESS_VALUES = {
    "complete",
    "incomplete",
    "incomplete_first_party_only",
    "incomplete_third_party_only",
    "unknown",
}

DEPENDENCY_GRAPH_PATHS = [
    REPO_ROOT / "data" / "asset_index" / "dependency-graph.json",
    REPO_ROOT / "docs" / "02_enterprise_architecture" / "04_architecture_principles_decisions" / "dependency_path_panorama.md",
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "cross-module-dependency-registry.yaml",
]

TEMPLATE_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "templates" / "dependency-graph-template.md"


def load_yaml_safe(path: Path) -> dict | None:
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def validate_yaml_dependency_graph(data: dict, source_path: str) -> list[dict]:
    findings = []

    for section in REQUIRED_SECTIONS:
        if section not in data or data[section] is None:
            findings.append(
                {
                    "rule": "MAD-005-R1",
                    "severity": "ERROR",
                    "message": f"必填结构缺失或为空: {section}",
                    "source": source_path,
                }
            )

    nodes = data.get("nodes") or []
    for i, node in enumerate(nodes):
        for field in NODE_REQUIRED_FIELDS:
            if field not in node or not node[field]:
                findings.append(
                    {
                        "rule": "MAD-005-R2",
                        "severity": "ERROR",
                        "message": f"节点[{i}] 缺少必填字段: {field} (node_id={node.get('node_id', '?')})",
                        "source": source_path,
                    }
                )
        if node.get("type") and node["type"] not in NODE_TYPES:
            findings.append(
                {
                    "rule": "MAD-004-R6",
                    "severity": "WARN",
                    "message": f"节点[{i}] type='{node['type']}' 不在受控词表中 (node_id={node.get('node_id', '?')})",
                    "source": source_path,
                }
            )
        if node.get("layer") and node["layer"] not in LAYERS:
            findings.append(
                {
                    "rule": "MAD-004-R6",
                    "severity": "WARN",
                    "message": f"节点[{i}] layer='{node['layer']}' 不在受控词表中 (node_id={node.get('node_id', '?')})",
                    "source": source_path,
                }
            )

    edges = data.get("edges") or []
    for i, edge in enumerate(edges):
        for field in EDGE_REQUIRED_FIELDS:
            if field not in edge or not edge[field]:
                findings.append(
                    {
                        "rule": "MAD-004-R3",
                        "severity": "ERROR",
                        "message": f"边[{i}] 缺少必填字段: {field} (edge_id={edge.get('edge_id', '?')})",
                        "source": source_path,
                    }
                )
        if edge.get("dep_type") and edge["dep_type"] not in DEP_TYPES:
            findings.append(
                {
                    "rule": "MAD-004-R6",
                    "severity": "WARN",
                    "message": f"边[{i}] dep_type='{edge['dep_type']}' 不在受控词表中 (edge_id={edge.get('edge_id', '?')})",
                    "source": source_path,
                }
            )
        if edge.get("strength") and edge["strength"] not in STRENGTHS:
            findings.append(
                {
                    "rule": "MAD-004-R6",
                    "severity": "WARN",
                    "message": f"边[{i}] strength='{edge['strength']}' 不在受控词表中 (edge_id={edge.get('edge_id', '?')})",
                    "source": source_path,
                }
            )
        if edge.get("direction") and edge["direction"] not in DIRECTIONS:
            findings.append(
                {
                    "rule": "MAD-004-R6",
                    "severity": "WARN",
                    "message": f"边[{i}] direction='{edge['direction']}' 不在受控词表中 (edge_id={edge.get('edge_id', '?')})",
                    "source": source_path,
                }
            )

    adjacency = data.get("adjacency") or {}
    if "forward" not in adjacency:
        findings.append(
            {"rule": "MAD-004-R4", "severity": "ERROR", "message": "邻接表缺少 forward 方向", "source": source_path}
        )
    if "reverse" not in adjacency:
        findings.append(
            {"rule": "MAD-004-R4", "severity": "ERROR", "message": "邻接表缺少 reverse 方向", "source": source_path}
        )

    compositions = data.get("compositions") or {}
    completeness = compositions.get("completeness")
    if completeness and completeness not in COMPLETENESS_VALUES:
        findings.append(
            {
                "rule": "MAD-004-R5",
                "severity": "ERROR",
                "message": f"completeness='{completeness}' 不在受控词表中",
                "source": source_path,
            }
        )

    blueprint_links = data.get("blueprint_links") or []
    for i, link in enumerate(blueprint_links):
        bp_path = link.get("blueprint_path", "")
        if bp_path:
            full_path = REPO_ROOT / bp_path
            if not full_path.exists():
                findings.append(
                    {
                        "rule": "MAD-004-R7",
                        "severity": "WARN",
                        "message": f"蓝图链接[{i}] 路径不存在: {bp_path}",
                        "source": source_path,
                    }
                )
            elif full_path.suffix == ".md":
                content = full_path.read_text(encoding="utf-8")
                if "[BLUEPRINT]" not in content:
                    findings.append(
                        {
                            "rule": "MAD-004-R7",
                            "severity": "WARN",
                            "message": f"蓝图链接[{i}] 文件缺少 [BLUEPRINT] 字段: {bp_path}",
                            "source": source_path,
                        }
                    )

    return findings


def validate_cross_module_registry(path: Path) -> list[dict]:
    findings = []
    data = load_yaml_safe(path)
    if data is None:
        return [{"rule": "MAD-004-R1", "severity": "ERROR", "message": f"无法加载 YAML: {path}", "source": str(path)}]

    dep_graph = data.get("dependency-graph") or {}
    forward = dep_graph.get("forward") or {}
    reverse = dep_graph.get("reverse") or {}

    if not forward:
        findings.append(
            {
                "rule": "MAD-004-R4",
                "severity": "WARN",
                "message": "cross-module-dependency-registry: dependency-graph.forward 为空",
                "source": str(path),
            }
        )
    if not reverse:
        findings.append(
            {
                "rule": "MAD-004-R4",
                "severity": "WARN",
                "message": "cross-module-dependency-registry: dependency-graph.reverse 为空",
                "source": str(path),
            }
        )

    completeness = (data.get("compositions") or {}).get("completeness")
    if not completeness:
        findings.append(
            {
                "rule": "MAD-004-R5",
                "severity": "WARN",
                "message": "cross-module-dependency-registry: 未声明 completeness",
                "source": str(path),
            }
        )

    return findings


def main() -> int:
    all_findings = []

    dep_graph_json = REPO_ROOT / "data" / "asset_index" / "dependency-graph.json"
    if dep_graph_json.exists():
        try:
            import json

            with open(dep_graph_json, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "nodes" in data:
                if isinstance(data["nodes"], dict):
                    node_list = []
                    for k, v in data["nodes"].items():
                        node_entry = {"node_id": k}
                        if isinstance(v, dict):
                            node_entry.update(v)
                        node_list.append(node_entry)
                    data["nodes"] = node_list
                if isinstance(data.get("edges"), dict):
                    edge_list = []
                    for k, v in data["edges"].items():
                        edge_entry = {"edge_id": k}
                        if isinstance(v, dict):
                            edge_entry.update(v)
                        edge_list.append(edge_entry)
                    data["edges"] = edge_list
            findings = validate_yaml_dependency_graph(data, str(dep_graph_json))
            all_findings.extend(findings)
        except Exception as e:
            all_findings.append(
                {
                    "rule": "MAD-005-R1",
                    "severity": "ERROR",
                    "message": f"无法加载 dependency-graph.json: {e}",
                    "source": str(dep_graph_json),
                }
            )

    cross_module_yaml = (
        REPO_ROOT
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "catalogs"
        / "cross-module-dependency-registry.yaml"
    )
    if cross_module_yaml.exists():
        findings = validate_cross_module_registry(cross_module_yaml)
        all_findings.extend(findings)

    if not TEMPLATE_PATH.exists():
        all_findings.append(
            {
                "rule": "MAD-004-R1",
                "severity": "ERROR",
                "message": f"依赖图模板不存在: {TEMPLATE_PATH}",
                "source": "TPL-DEPGRAPH-001",
            }
        )

    errors = [f for f in all_findings if f["severity"] == "ERROR"]
    warns = [f for f in all_findings if f["severity"] == "WARN"]

    if errors:
        print(f"MAD-004 FAIL: {len(errors)} errors, {len(warns)} warnings")
        for f in errors:
            print(f"  ERROR [{f['rule']}] {f['message']}")
        for f in warns:
            print(f"  WARN  [{f['rule']}] {f['message']}")
        return EXIT_FINDINGS

    if warns:
        print(f"MAD-004 WARN: {len(warns)} warnings (no errors)")
        for f in warns:
            print(f"  WARN  [{f['rule']}] {f['message']}")
        return EXIT_PASS

    print("MAD-004 PASS: 依赖图模板合规验证通过")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
