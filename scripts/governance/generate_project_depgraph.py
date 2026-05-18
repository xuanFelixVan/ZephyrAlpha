#!/usr/bin/env python3
"""
# [BLUEPRINT] MOD-INF-005 | scripts/governance/generate_project_depgraph.py | §7
# [MODULE] scripts.governance.generate_project_depgraph
# [INVARIANTS] --dry-run MUST NOT modify any file; output MUST be valid YAML + Mermaid
# [MODIFY-GUARD] system-dependency-map.md; cross-module-dependency-registry.yaml
# [CONSUMERS] CI pipeline; governance automation; system-dependency-map.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScanError; ParseError
# [TESTS] tests/test_generate_project_depgraph.py
"""

import argparse
import ast
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

NODE_TYPES = [
    "blueprint", "module", "script", "gate", "registry", "contract",
    "policy", "standard", "template", "schema", "infra", "diagram",
    "config", "data", "test", "doc",
]
EDGE_TYPES = ["owned_by", "imports", "references", "depends_on"]

EXEMPT_DIRS = {
    "__pycache__", ".git", ".ailocks", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "_backups", "_temp",
}

SCAN_DIRS = [
    "src/zephyr",
    "scripts",
    "tests",
    "data",
    "config",
    "schemas",
    "docs/03_modules",
    "docs/01_policies_and_standards",
    "docs/02_enterprise_architecture",
    "docs/08_knowledge",
    "docs/09_audit",
]

POLICY_PREFIXES = [
    "docs/01_policies_and_standards/governance/",
    "docs/01_policies_and_standards/meta/",
    "docs/01_policies_and_standards/domains/",
    "docs/01_policies_and_standards/operational/",
]
STANDARD_PREFIXES = [
    "docs/01_policies_and_standards/governance/engineering/",
]
TEMPLATE_PREFIXES = [
    "docs/01_policies_and_standards/templates/",
]
REGISTRY_PREFIXES = [
    "docs/01_policies_and_standards/_registry/catalogs/",
    "docs/01_policies_and_standards/_registry/vocabularies/",
]
CONTRACT_PREFIXES = [
    "docs/01_policies_and_standards/_registry/contracts/",
]
SCHEMA_PREFIXES = [
    "docs/01_policies_and_standards/_registry/schemas/",
    "schemas/",
]

ID_PATTERN = re.compile(
    r"(MOD-INF-\d+|MOD-KB-\d+|MOD-L\d+-\d+|DOM-GOV-\d+|SYS-MASTER-\d+"
    r"|GOV-[A-Z]+-\d+|PS-[A-Z]+-\d+|PS-REG-\d+|PS-STD-\d+"
    r"|DEP-\d+|EN-\d+|GCT-\d+|REG-[A-Z]+-\d+|CT-\d+"
    r"|GOV-DOC-\d+|GOV-ENG-\d+|ADR-\d+|TPL-[A-Z]+-\d+"
    r"|CAT-[A-Z]+-\d+)"
)


def parse_blueprint_header(filepath: Path) -> dict:
    info = {"blueprint_id": "", "blueprint_path": "", "module_path": "", "stability": "", "safety": "", "ai_autonomy": ""}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 15:
                    break
                stripped = line.strip()
                if stripped.startswith("# [BLUEPRINT]"):
                    parts = stripped[len("# [BLUEPRINT]"):].strip().split("|")
                    if len(parts) >= 1:
                        info["blueprint_id"] = parts[0].strip()
                    if len(parts) >= 2:
                        info["blueprint_path"] = parts[1].strip()
                elif stripped.startswith('"""[BLUEPRINT]') or stripped.startswith("'''[BLUEPRINT]"):
                    content = stripped.lstrip('"\'').lstrip()
                    if content.startswith("[BLUEPRINT]"):
                        content = content[len("[BLUEPRINT]"):].strip()
                    else:
                        content = content[len("BLUEPRINT]"):].strip()
                    parts = content.split("|")
                    if len(parts) >= 1:
                        info["blueprint_id"] = parts[0].strip()
                    if len(parts) >= 2:
                        info["blueprint_path"] = parts[1].strip()
                elif stripped.startswith("# [MODULE]"):
                    info["module_path"] = stripped[len("# [MODULE]"):].strip()
                elif stripped.startswith("# [STABILITY]"):
                    info["stability"] = stripped[len("# [STABILITY]"):].strip()
                elif stripped.startswith("# [SAFETY]"):
                    info["safety"] = stripped[len("# [SAFETY]"):].strip()
                elif stripped.startswith("# [AI_AUTONOMY]"):
                    info["ai_autonomy"] = stripped[len("# [AI_AUTONOMY]"):].strip()
                if not info["blueprint_id"] and i < 10:
                    bp_match = __import__("re").search(r'(?:蓝图|blueprint)[:\s]+([A-Z]{2,4}-[A-Z]*-?\d+)', stripped, __import__("re").IGNORECASE)
                    if bp_match:
                        info["blueprint_id"] = bp_match.group(1).upper()
    except Exception:
        pass
    return info


def parse_yaml_header(filepath: Path) -> dict:
    info = {"blueprint_id": "", "blueprint_path": "", "stability": "", "safety": "", "ai_autonomy": ""}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            in_anchor = False
            for i, line in enumerate(f):
                if i >= 30:
                    break
                if "治理锚定" in line:
                    in_anchor = True
                    continue
                if in_anchor and "治理锚定结束" in line:
                    break
                if in_anchor:
                    m = re.match(r"#\s*blueprint:\s*(.+?)(?:\s*\|\s*(.+?))?(?:\s*\|\s*.+)?$", line)
                    if m:
                        info["blueprint_id"] = m.group(1).strip()
                        if m.group(2):
                            info["blueprint_path"] = m.group(2).strip()
                    m = re.match(r"#\s*module_id:\s*(.+)$", line)
                    if m:
                        if not info["blueprint_id"]:
                            info["blueprint_id"] = m.group(1).strip()
                    m = re.match(r"#\s*stability:\s*(.+)$", line)
                    if m:
                        info["stability"] = m.group(1).strip()
                    m = re.match(r"#\s*safety_level:\s*(.+)$", line)
                    if m:
                        info["safety"] = m.group(1).strip()
                    m = re.match(r"#\s*ai_autonomy:\s*(.+)$", line)
                    if m:
                        info["ai_autonomy"] = m.group(1).strip()
    except Exception:
        pass
    return info


def parse_md_frontmatter(filepath: Path) -> dict:
    info = {"blueprint_id": "", "module_id": "", "stability": "", "safety": "", "ai_autonomy": ""}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            in_fm = False
            for i, line in enumerate(f):
                if i >= 40:
                    break
                stripped = line.strip()
                if i == 0 and stripped.lstrip("\ufeff").strip() == "---":
                    in_fm = True
                    continue
                if in_fm and stripped == "---":
                    break
                if in_fm:
                    m = re.match(r"module_id:\s*(.+)$", stripped)
                    if m:
                        info["module_id"] = m.group(1).strip().strip('"').strip("'")
                        if not info["blueprint_id"]:
                            info["blueprint_id"] = info["module_id"]
                    m = re.match(r"stability:\s*(.+)$", stripped)
                    if m:
                        info["stability"] = m.group(1).strip()
                    m = re.match(r"safety_level:\s*(.+)$", stripped)
                    if m:
                        info["safety"] = m.group(1).strip()
                    m = re.match(r"ai_autonomy:\s*(.+)$", stripped)
                    if m:
                        info["ai_autonomy"] = m.group(1).strip()
    except Exception:
        pass
    return info


def extract_py_imports(filepath: Path) -> list:
    imports = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("zephyr") or alias.name.startswith("scripts"):
                        imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    try:
                        rel_parent = filepath.relative_to(PROJECT_ROOT).parent
                    except ValueError:
                        continue
                    parts = list(rel_parent.parts)
                    for _ in range(node.level - 1):
                        if parts:
                            parts.pop()
                    if node.module:
                        parts.append(node.module.replace(".", "/"))
                    base = "/".join(parts)
                    for alias in node.names:
                        mod_path = base + "/" + alias.name.replace(".", "/")
                        if mod_path.startswith("src/zephyr/"):
                            dot_path = mod_path.replace("src/zephyr/", "zephyr.").replace("/", ".")
                            imports.append(dot_path)
                        elif mod_path.startswith("scripts/"):
                            dot_path = mod_path.replace("scripts/", "scripts.").replace("/", ".")
                            imports.append(dot_path)
                elif node.module and (node.module.startswith("zephyr") or node.module.startswith("scripts")):
                    imports.append(node.module)
    except Exception:
        pass
    return imports


def extract_md_references(filepath: Path) -> list:
    refs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return list(set(refs))


def extract_json_references(filepath: Path) -> list:
    refs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return list(set(refs))


def classify_file(rel_path: str) -> str:
    rp = rel_path.replace("\\", "/")

    if rp.startswith("src/zephyr/gates/") and rp.endswith(".yaml"):
        return "gate"
    if rp.startswith("src/zephyr/") and rp.endswith(".py"):
        return "module"
    if rp.startswith("scripts/") and rp.endswith(".py"):
        return "script"
    if rp.startswith("tests/") and rp.endswith(".py"):
        return "test"

    if rp.endswith((".sh", ".ps1")):
        return "infra"

    if rp.endswith(".mmd"):
        return "diagram"

    if rp.endswith(".json"):
        if any(rp.startswith(p) for p in SCHEMA_PREFIXES):
            return "schema"
        return "data"

    if rp.endswith((".yaml", ".yml")):
        if any(rp.startswith(p) for p in REGISTRY_PREFIXES):
            return "registry"
        if any(rp.startswith(p) for p in CONTRACT_PREFIXES):
            return "contract"
        if any(p in rp for p in ("_registry.yaml", "_manifest.yaml")):
            return "registry"
        if rp.startswith("data/"):
            return "data"
        if rp.startswith("config/"):
            return "config"
        return "config"

    if rp.endswith(".md"):
        if rp.endswith("/blueprint.md") or rp.endswith("\\blueprint.md"):
            return "blueprint"
        if rp.startswith("docs/03_modules/_master-blueprint/") and "/blueprint-" in rp:
            return "blueprint"
        if any(rp.startswith(p) for p in TEMPLATE_PREFIXES):
            return "template"
        if any(rp.startswith(p) for p in STANDARD_PREFIXES):
            return "standard"
        if any(rp.startswith(p) for p in POLICY_PREFIXES):
            return "policy"
        if any(rp.startswith(p) for p in SCHEMA_PREFIXES):
            return "schema"
        if rp.startswith("docs/09_audit/"):
            return "doc"
        if rp.startswith("docs/08_knowledge/"):
            return "doc"
        if rp.startswith("docs/02_enterprise_architecture/"):
            return "doc"
        return "doc"

    return ""


def scan_py_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    header = parse_blueprint_header(filepath)
    imports = extract_py_imports(filepath)
    cat = classify_file(rel_path)
    if not cat:
        cat = "module"
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "blueprint_id": header["blueprint_id"],
        "blueprint_path": header["blueprint_path"],
        "module_path": header["module_path"],
        "stability": header["stability"],
        "safety": header["safety"],
        "ai_autonomy": header["ai_autonomy"],
        "imports": imports,
    }


def scan_yaml_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    header = parse_yaml_header(filepath)
    cat = classify_file(rel_path)
    if not cat:
        cat = "config"
    refs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "blueprint_id": header["blueprint_id"],
        "blueprint_path": header["blueprint_path"],
        "stability": header["stability"],
        "safety": header["safety"],
        "ai_autonomy": header["ai_autonomy"],
        "references": list(set(refs)),
    }


def scan_md_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    cat = classify_file(rel_path)
    if not cat:
        cat = "doc"

    if cat == "blueprint":
        return scan_blueprint_file(rel_path)

    fm = parse_md_frontmatter(filepath)
    refs = extract_md_references(filepath)

    bp_id = fm.get("module_id", "") or fm.get("blueprint_id", "")
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "blueprint_id": bp_id,
        "stability": fm.get("stability", ""),
        "safety": fm.get("safety", ""),
        "ai_autonomy": fm.get("ai_autonomy", ""),
        "references": refs,
    }


def scan_blueprint_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    refs = []
    module_id = ""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        in_fm = False
        fm_lines = []
        for i, line in enumerate(content.splitlines()):
            if i >= 40:
                break
            stripped = line.strip()
            if i == 0 and stripped.lstrip("\ufeff").strip() == "---":
                in_fm = True
                continue
            if in_fm and stripped == "---":
                break
            if in_fm:
                fm_lines.append(stripped)
        fm_text = "\n".join(fm_lines)
        m = re.search(r"module_id:\s*(\S+)", fm_text)
        if m:
            module_id = m.group(1).strip('"').strip("'")
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": "blueprint",
        "blueprint_id": module_id,
        "module_id": module_id,
        "references": list(set(refs)),
    }


def scan_json_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    cat = classify_file(rel_path)
    if not cat:
        cat = "data"
    refs = extract_json_references(filepath)
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "blueprint_id": "",
        "references": refs,
    }


def scan_infra_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    header = parse_blueprint_header(filepath)
    refs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": "infra",
        "blueprint_id": header.get("blueprint_id", ""),
        "references": list(set(refs)),
    }


def scan_diagram_file(rel_path: str) -> Optional[dict]:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    refs = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": "diagram",
        "blueprint_id": "",
        "references": list(set(refs)),
    }


def collect_all_files() -> list:
    files = []
    for scan_dir_rel in SCAN_DIRS:
        scan_dir = PROJECT_ROOT / scan_dir_rel
        if not scan_dir.exists():
            continue
        for root, dirs, filenames in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if d not in EXEMPT_DIRS and not d.startswith(".")]
            for fn in filenames:
                fp = Path(root) / fn
                rel = str(fp.relative_to(PROJECT_ROOT)).replace("\\", "/")
                files.append(rel)
    return files


def build_depgraph(files_data: list) -> dict:
    nodes = {}
    edges = []
    edge_set = set()

    path_to_node = {}
    for fd in files_data:
        path = fd["path"]
        path_to_node[path] = fd
        bid_raw = fd.get("blueprint_id", "") or fd.get("module_id", "")
        bid_clean = bid_raw.strip('"').strip("'") if bid_raw else ""
        node_id = path.replace("/", "__").replace(".", "_")
        def _clean(val):
            v = val.strip('"').strip("'")
            if "#" in v:
                v = v[:v.index("#")].strip()
            return v

        nodes[node_id] = {
            "id": node_id,
            "path": path,
            "type": fd.get("type", "unknown"),
            "blueprint_id": bid_clean,
            "stability": _clean(fd.get("stability", "")),
            "safety": _clean(fd.get("safety", "")),
            "ai_autonomy": _clean(fd.get("ai_autonomy", "")),
        }

    bp_id_to_paths = defaultdict(list)
    for fd in files_data:
        bid_raw = fd.get("blueprint_id", "") or fd.get("module_id", "")
        bid_clean = bid_raw.strip('"').strip("'") if bid_raw else ""
        if bid_clean:
            bp_id_to_paths[bid_clean].append(fd["path"])

    for fd in files_data:
        src_path = fd["path"]
        src_id = src_path.replace("/", "__").replace(".", "_")
        if src_id not in nodes:
            continue

        bid_raw = fd.get("blueprint_id", "") or fd.get("module_id", "")
        bid = bid_raw.strip('"').strip("'") if bid_raw else ""
        if bid and fd.get("type") != "blueprint":
            for bp_path in bp_id_to_paths.get(bid, []):
                if bp_path == src_path:
                    continue
                bp_node_id = bp_path.replace("/", "__").replace(".", "_")
                if bp_node_id in nodes and nodes[bp_node_id].get("type") == "blueprint":
                    dst_id = bp_node_id
                    edge_key = (src_id, dst_id, "owned_by")
                    if edge_key not in edge_set:
                        edges.append({"from": src_id, "to": dst_id, "type": "owned_by"})
                        edge_set.add(edge_key)

        imports = fd.get("imports", [])
        for imp in imports:
            imp_parts = imp.split(".")
            if imp_parts[0] == "zephyr":
                imp_parts = imp_parts[1:]
                prefix = "src/zephyr"
            elif imp_parts[0] == "scripts":
                imp_parts = imp_parts[1:]
                prefix = "scripts"
            else:
                continue
            if not imp_parts:
                continue
            for i in range(len(imp_parts), 0, -1):
                candidate = prefix + "/" + "/".join(imp_parts[:i]) + ".py"
                if candidate in path_to_node:
                    dst_id = candidate.replace("/", "__").replace(".", "_")
                    if dst_id == src_id:
                        continue
                    edge_key = (src_id, dst_id, "imports")
                    if edge_key not in edge_set and dst_id in nodes:
                        edges.append({"from": src_id, "to": dst_id, "type": "imports"})
                        edge_set.add(edge_key)
                    break
                candidate2 = prefix + "/" + "/".join(imp_parts[:i]) + "/__init__.py"
                if candidate2 in path_to_node:
                    dst_id = candidate2.replace("/", "__").replace(".", "_")
                    if dst_id == src_id:
                        continue
                    edge_key = (src_id, dst_id, "imports")
                    if edge_key not in edge_set and dst_id in nodes:
                        edges.append({"from": src_id, "to": dst_id, "type": "imports"})
                        edge_set.add(edge_key)
                    break

        refs = fd.get("references", [])
        if fd.get("type") != "blueprint":
            for ref in refs:
                for bp_path in bp_id_to_paths.get(ref, []):
                    if bp_path == src_path:
                        continue
                    bp_node_id = bp_path.replace("/", "__").replace(".", "_")
                    if bp_node_id in nodes and nodes[bp_node_id].get("type") == "blueprint":
                        dst_id = bp_node_id
                        edge_key = (src_id, dst_id, "references")
                        if edge_key not in edge_set:
                            edges.append({"from": src_id, "to": dst_id, "type": "references"})
                            edge_set.add(edge_key)

    by_type = defaultdict(int)
    for n in nodes.values():
        by_type[n["type"]] += 1
    by_edge_type = defaultdict(int)
    for e in edges:
        by_edge_type[e["type"]] += 1

    adjacency_forward = defaultdict(list)
    adjacency_reverse = defaultdict(list)
    for e in edges:
        adjacency_forward[e["from"]].append({"to": e["to"], "type": e["type"]})
        adjacency_reverse[e["to"]].append({"from": e["from"], "type": e["type"]})

    most_depended = sorted(
        [(nid, len(adjacency_reverse.get(nid, []))) for nid in nodes if len(adjacency_reverse.get(nid, [])) > 0],
        key=lambda x: -x[1]
    )[:20]

    orphans = [nid for nid in nodes if not adjacency_forward.get(nid) and not adjacency_reverse.get(nid)]

    return {
        "metadata": {
            "graph_id": "PROJECT-ENTITY-DEPGRAPH-001",
            "version": "2.1.0",
            "scope": "全项目实体级依赖图（全覆盖）",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes_by_type": dict(by_type),
            "edges_by_type": dict(by_edge_type),
        },
        "nodes": nodes,
        "edges": edges,
        "adjacency_forward": dict(adjacency_forward),
        "adjacency_reverse": dict(adjacency_reverse),
        "most_depended_upon": most_depended,
        "orphan_nodes": orphans[:50],
    }


def generate_mermaid_by_blueprint(depgraph: dict) -> str:
    bp_groups = defaultdict(list)
    for nid, node in depgraph["nodes"].items():
        bid = node.get("blueprint_id", "UNMAPPED")
        if not bid:
            bid = "UNMAPPED"
        bp_groups[bid].append(node)

    lines = ["flowchart TB"]
    for bid in sorted(bp_groups.keys()):
        nodes_in_group = bp_groups[bid]
        if bid == "UNMAPPED":
            continue
        safe_bid = bid.replace("-", "_").replace(".", "_")
        lines.append(f"    subgraph {safe_bid}[\"{bid} ({len(nodes_in_group)})\"]")
        for node in nodes_in_group[:10]:
            safe_nid = node["id"]
            short_path = "/".join(node["path"].split("/")[-2:])
            ntype = node["type"]
            lines.append(f"        {safe_nid}[\"{short_path}<br/>({ntype})\"]")
        if len(nodes_in_group) > 10:
            lines.append(f"        {safe_bid}_more[\"... +{len(nodes_in_group)-10} more\"]")
        lines.append("    end")

    edge_count = 0
    for edge in depgraph["edges"]:
        if edge["type"] in ("owned_by", "references"):
            continue
        if edge_count >= 300:
            break
        from_id = edge["from"]
        to_id = edge["to"]
        etype = edge["type"]
        style = {"imports": "-->", "references": "-.->", "depends_on": "-->"}.get(etype, "-->")
        lines.append(f"    {from_id} {style} {to_id}")
        edge_count += 1

    if edge_count >= 300:
        total_imports = sum(1 for e in depgraph["edges"] if e["type"] == "imports")
        lines.append(f"    %% ... {total_imports - edge_count} more import edges omitted")

    return "\n".join(lines)


def generate_mermaid_by_type(depgraph: dict) -> str:
    type_groups = defaultdict(list)
    for nid, node in depgraph["nodes"].items():
        type_groups[node["type"]].append(node)

    lines = ["flowchart LR"]
    for ntype in sorted(type_groups.keys()):
        nodes_in_group = type_groups[ntype]
        safe_type = ntype.replace("-", "_")
        lines.append(f"    subgraph {safe_type}[\"{ntype} ({len(nodes_in_group)})\"]")
        for node in nodes_in_group[:15]:
            safe_nid = node["id"]
            short_path = "/".join(node["path"].split("/")[-2:])
            lines.append(f"        {safe_nid}[\"{short_path}\"]")
        if len(nodes_in_group) > 15:
            lines.append(f"        {safe_type}_more[\"... +{len(nodes_in_group)-15} more\"]")
        lines.append("    end")

    return "\n".join(lines)


def generate_markdown_section(depgraph: dict) -> str:
    meta = depgraph["metadata"]
    lines = []
    lines.append("## §19 实体级依赖图（全项目文件级）")
    lines.append("")
    lines.append(f"> **graph_id**: {meta['graph_id']} | **version**: {meta['version']} | **scope**: {meta['scope']}")
    lines.append(f"> **total_nodes**: {meta['total_nodes']} | **total_edges**: {meta['total_edges']}")
    lines.append(f"> 生成脚本: `scripts/governance/generate_project_depgraph.py`")
    lines.append("")

    lines.append("### §19.1 节点统计")
    lines.append("")
    lines.append("| 类型 | 数量 |")
    lines.append("|------|:----:|")
    for ntype, count in sorted(meta["nodes_by_type"].items()):
        lines.append(f"| {ntype} | {count} |")
    lines.append(f"| **合计** | **{meta['total_nodes']}** |")
    lines.append("")

    lines.append("### §19.2 边统计")
    lines.append("")
    lines.append("| 边类型 | 数量 | 含义 |")
    lines.append("|--------|:----:|------|")
    edge_desc = {"owned_by": "文件归属蓝图", "imports": "Python import 依赖", "references": "YAML/MD/JSON 中引用 ID", "depends_on": "逻辑依赖"}
    for etype, count in sorted(meta["edges_by_type"].items()):
        lines.append(f"| {etype} | {count} | {edge_desc.get(etype, '')} |")
    lines.append(f"| **合计** | **{meta['total_edges']}** | |")
    lines.append("")

    lines.append("### §19.3 Top 20 被依赖节点")
    lines.append("")
    lines.append("| # | 节点 | 被依赖次数 | 类型 | 蓝图 |")
    lines.append("|---|------|:---------:|------|------|")
    for i, (nid, count) in enumerate(depgraph.get("most_depended_upon", [])[:20], 1):
        node = depgraph["nodes"].get(nid, {})
        short = "/".join(node.get("path", nid).split("/")[-2:])
        lines.append(f"| {i} | {short} | {count} | {node.get('type', '')} | {node.get('blueprint_id', '')} |")
    lines.append("")

    orphans = depgraph.get("orphan_nodes", [])
    if orphans:
        lines.append("### §19.4 孤儿节点（无入边无出边）")
        lines.append("")
        lines.append(f"共 {len(orphans)} 个孤儿节点（仅列前 50 个）：")
        lines.append("")
        for nid in orphans[:50]:
            node = depgraph["nodes"].get(nid, {})
            short = "/".join(node.get("path", nid).split("/")[-2:])
            lines.append(f"- `{short}` ({node.get('type', '')}) [{node.get('blueprint_id', '')}]")
        lines.append("")

    lines.append("### §19.5 按蓝图分组视图")
    lines.append("")
    lines.append("```mermaid")
    lines.append(generate_mermaid_by_blueprint(depgraph))
    lines.append("```")
    lines.append("")

    lines.append("### §19.6 按类型分组视图")
    lines.append("")
    lines.append("```mermaid")
    lines.append(generate_mermaid_by_type(depgraph))
    lines.append("```")
    lines.append("")

    bp_groups = defaultdict(list)
    for nid, node in depgraph["nodes"].items():
        bid = node.get("blueprint_id", "UNMAPPED")
        bp_groups[bid].append(node)

    lines.append("### §19.7 蓝图-文件归属明细")
    lines.append("")
    lines.append("| 蓝图 | 文件数 | 类型分布 |")
    lines.append("|------|:------:|---------|")
    for bid in sorted(bp_groups.keys()):
        nodes_in = bp_groups[bid]
        type_dist = defaultdict(int)
        for n in nodes_in:
            type_dist[n["type"]] += 1
        dist_str = ", ".join(f"{t}:{c}" for t, c in sorted(type_dist.items()))
        lines.append(f"| {bid} | {len(nodes_in)} | {dist_str} |")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate project entity-level dependency graph (full coverage)")
    parser.add_argument("--output-yaml", type=str, default="", help="Output YAML data file path")
    parser.add_argument("--output-md-section", type=str, default="", help="Output markdown section file path")
    parser.add_argument("--max-workers", type=int, default=8, help="ThreadPoolExecutor workers")
    args = parser.parse_args()

    print("[DEPGRAPH] Scanning project files...")
    all_files = collect_all_files()
    print(f"[DEPGRAPH] Found {len(all_files)} files")

    py_files = [f for f in all_files if f.endswith(".py")]
    yaml_files = [f for f in all_files if f.endswith((".yaml", ".yml"))]
    md_files = [f for f in all_files if f.endswith(".md")]
    json_files = [f for f in all_files if f.endswith(".json")]
    infra_files = [f for f in all_files if f.endswith((".sh", ".ps1"))]
    diagram_files = [f for f in all_files if f.endswith(".mmd")]

    files_data = []

    print(f"[DEPGRAPH] Scanning {len(py_files)} .py files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_py_file, f): f for f in py_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(yaml_files)} .yaml files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_yaml_file, f): f for f in yaml_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(md_files)} .md files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_md_file, f): f for f in md_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(json_files)} .json files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_json_file, f): f for f in json_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(infra_files)} infra files (.sh/.ps1)...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_infra_file, f): f for f in infra_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(diagram_files)} diagram files (.mmd)...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(scan_diagram_file, f): f for f in diagram_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Total scanned: {len(files_data)} entities")

    print("[DEPGRAPH] Building dependency graph...")
    depgraph = build_depgraph(files_data)

    meta = depgraph["metadata"]
    print(f"[DEPGRAPH] Nodes: {meta['total_nodes']} | Edges: {meta['total_edges']}")
    print(f"[DEPGRAPH] Nodes by type: {meta['nodes_by_type']}")
    print(f"[DEPGRAPH] Edges by type: {meta['edges_by_type']}")

    if args.output_yaml:
        import yaml
        out_path = PROJECT_ROOT / args.output_yaml
        tmp_path = str(out_path) + f".{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(depgraph, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, str(out_path))
        print(f"[DEPGRAPH] YAML written to {args.output_yaml}")

    md_section = generate_markdown_section(depgraph)

    if args.output_md_section:
        out_path = PROJECT_ROOT / args.output_md_section
        tmp_path = str(out_path) + f".{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(md_section)
        os.replace(tmp_path, str(out_path))
        print(f"[DEPGRAPH] Markdown section written to {args.output_md_section}")
    else:
        print("\n" + "=" * 60)
        print("MARKDOWN SECTION (paste into system-dependency-map.md):")
        print("=" * 60)
        print(md_section[:3000])
        if len(md_section) > 3000:
            print(f"\n... truncated ({len(md_section)} total chars)")

    sys.exit(0)


if __name__ == "__main__":
    main()
