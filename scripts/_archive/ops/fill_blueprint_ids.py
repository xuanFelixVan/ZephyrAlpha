# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [TTL] task_bound
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

ROOT = Path(r"d:\ZephyrAlpha")
DEPGRAPH_PATH = ROOT / "data" / "databases" / "depgraph.db"
MODULE_REGISTRY_PATH = ROOT / "docs" / "03_modules" / "module-registry.yaml"
BLUEPRINT_REGISTRY_PATH = ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"
SRC_ZEPHYR = ROOT / "src" / "zephyr"


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.unsafe_load(f)


def build_registry_mapping(module_registry, blueprint_registry):
    mapping = {}
    for m in module_registry.get("modules", []):
        mid = m["module_id"]
        name = m["name"]
        dir_name = name.replace("-", "_")
        mapping[dir_name] = mid
    for b in blueprint_registry.get("blueprints", []):
        mid = b["module_id"]
        name = b["name"]
        dir_name = name.replace("-", "_")
        if dir_name not in mapping:
            mapping[dir_name] = mid
    return mapping


MANUAL_OVERRIDES = {
    "a2a": "MOD-INF-025",
    "core": "MOD-INF-002",
    "db": "MOD-DATABASE",
    "escalation": "MOD-INF-022",
    "escalation-engine": "MOD-INF-022",
    "shared": "MOD-INF-016",
    "contracts": "MOD-INF-016",
    "gates": "MOD-GATE_ENGINE",
    "governance": "DOM-GOV-001",
    "hooks": "MOD-INF-002",
    "infrastructure": "MOD-INF-002",
    "data": "MOD-L00-001",
    "infrastructure.runtime_integration": "MOD-INF-002",
    "factor": "MOD-L02-001",
    "signal": "MOD-L03-001",
    "risk": "MOD-L04-001",
    "pf_core": "MOD-L05-001",
    "ex_core": "MOD-L06-001",
    "pf_core": "MOD-L07-001",
    "frontend": "MOD-L08-001",
    "research": "MOD-L09-001",
    "compliance": "MOD-L10-001",
    "ml_train": "MOD-L11-001",
    "integration": "MOD-L13-001",
    "lifecycle_manager": "MOD-INF-002",
    "orchestrator": "MOD-INF-035",
    "runtime": "MOD-INF-035",
    "script_system": "MOD-INF-005",
    "mcp": "MOD-INF-013",
    "mcp_servers": "MOD-INF-013",
    "rollback": "MOD-INF-021",
    "system-telemetry": "MOD-INF-015",
    "telemetry": "MOD-INF-015",
    "task_system": "MOD-TASK_SYSTEM",
    "vector-memory": "MOD-INF-011",
    "model-capability-exam": "MOD-INF-036",
    "_cross_layer": "MOD-INF-002",
    "__init__": "MOD-INF-002",
}

SUBDIR_OVERRIDES = {
    "infrastructure.runtime_integration": {
        "a2a_protocol": "MOD-INF-025",
        "code_dedup_engine": "MOD-INF-017",
        "script_system": "MOD-INF-005",
    },
}


def resolve_module_id(path_str, registry_mapping):
    parts = path_str.split("/")
    if len(parts) < 3 or parts[0] != "src" or parts[1] != "zephyr":
        return None

    if len(parts) == 3:
        return "MOD-INF-002"

    if len(parts) >= 5:
        parent_dir = parts[2]
        sub_dir = parts[3]
        if parent_dir in SUBDIR_OVERRIDES:
            sub_mapping = SUBDIR_OVERRIDES[parent_dir]
            if sub_dir in sub_mapping:
                return sub_mapping[sub_dir]

    for depth in range(len(parts) - 1, 2, -1):
        dir_name = parts[depth - 1] if depth >= 3 else None
        if dir_name and dir_name in MANUAL_OVERRIDES:
            return MANUAL_OVERRIDES[dir_name]
        if dir_name and dir_name in registry_mapping:
            return registry_mapping[dir_name]

    top_dir = parts[2]
    if top_dir in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[top_dir]
    if top_dir in registry_mapping:
        return registry_mapping[top_dir]

    return None


def find_blueprint_line_hash(lines):
    for i, line in enumerate(lines[:15]):
        if re.match(r"^#\s*\[BLUEPRINT\]", line):
            return i
    return -1


def find_blueprint_line_docstring(lines):
    in_doc = False
    for i, line in enumerate(lines[:20]):
        if '"""' in line:
            if not in_doc:
                in_doc = True
                if "[BLUEPRINT]" in line:
                    return i
            else:
                break
        elif in_doc and "[BLUEPRINT]" in line:
            return i
    return -1


def extract_existing_blueprint_id(lines):
    idx = find_blueprint_line_hash(lines)
    if idx >= 0:
        m = re.search(r"\[BLUEPRINT\]\s*(\S+)", lines[idx])
        if m:
            return m.group(1)
    idx = find_blueprint_line_docstring(lines)
    if idx >= 0:
        m = re.search(r"\[BLUEPRINT\]\s*(\S+)", lines[idx])
        if m:
            return m.group(1)
    return ""


def process_file(file_path, module_id, blueprint_rel_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return "skip_read_error"

    lines = content.split("\n")
    existing_bp_id = extract_existing_blueprint_id(lines)
    if existing_bp_id and existing_bp_id == module_id:
        return "skip_correct"

    blueprint_value = f"{module_id} | {blueprint_rel_path} | §"

    hash_idx = find_blueprint_line_hash(lines)
    if hash_idx >= 0:
        lines[hash_idx] = f"# [BLUEPRINT] {blueprint_value}"
        new_content = "\n".join(lines)
    else:
        doc_idx = find_blueprint_line_docstring(lines)
        if doc_idx >= 0:
            line = lines[doc_idx]
            stripped = line.strip()
            if stripped.startswith('"""'):
                lines[doc_idx] = f'"""[BLUEPRINT] {blueprint_value}'
            else:
                lines[doc_idx] = f"[BLUEPRINT] {blueprint_value}"
            new_content = "\n".join(lines)
        else:
            header_line = f"# [BLUEPRINT] {blueprint_value}"
            insert_pos = 0
            if lines and lines[0].startswith("#!"):
                insert_pos = 1
            lines.insert(insert_pos, header_line)
            new_content = "\n".join(lines)

    tmp_path = f"{file_path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, file_path)
        return "updated"
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return "skip_write_error"


def main():
    print("Loading depgraph...")
    depgraph = load_yaml(DEPGRAPH_PATH)
    nodes = depgraph.get("nodes", {})

    print("Loading registries...")
    module_registry = load_yaml(MODULE_REGISTRY_PATH)
    blueprint_registry = load_yaml(BLUEPRINT_REGISTRY_PATH)

    print("Building directory -> module_id mapping...")
    registry_mapping = build_registry_mapping(module_registry, blueprint_registry)
    print(f"  Registry mapping: {len(registry_mapping)} directories")

    dir_to_bp_path = {}
    for b in blueprint_registry.get("blueprints", []):
        mid = b["module_id"]
        fp = b.get("file_path", "")
        if fp:
            dir_to_bp_path[mid] = fp

    empty_bp_nodes = []
    for node_id, node in nodes.items():
        bp_id = node.get("blueprint_id", "")
        path_str = node.get("path", "")
        node_type = node.get("type", "")
        if not path_str.startswith("src/zephyr/"):
            continue
        if not path_str.endswith(".py"):
            continue
        if node_type != "module":
            continue
        if bp_id and bp_id.strip():
            continue
        empty_bp_nodes.append(node)

    print(f"\nFound {len(empty_bp_nodes)} nodes with empty blueprint_id under src/zephyr/")

    resolved = []
    unresolved = []
    for node in empty_bp_nodes:
        path_str = node["path"]
        module_id = resolve_module_id(path_str, registry_mapping)
        if not module_id:
            parts = path_str.split("/")
            dir_hint = parts[2] if len(parts) >= 3 else "?"
            sub_hint = parts[3] if len(parts) >= 4 else ""
            unresolved.append((path_str, f"no_mapping:{dir_hint}/{sub_hint}"))
            continue
        bp_path = dir_to_bp_path.get(module_id, "docs/03_modules/_unknown/blueprint.md")
        file_path = str(ROOT / path_str.replace("/", os.sep))
        if not os.path.isfile(file_path):
            unresolved.append((path_str, "file_not_found"))
            continue
        resolved.append((file_path, path_str, module_id, bp_path))

    print(f"Resolved: {len(resolved)}, Unresolved: {len(unresolved)}")

    if unresolved:
        print("\nUnresolved breakdown:")
        seen = {}
        for path_str, reason in unresolved:
            rk = reason.split(":")[0]
            seen.setdefault(rk, []).append((path_str, reason))
        for rk, items in seen.items():
            print(f"  {rk}: {len(items)} files")
            for p, r in items[:5]:
                print(f"    - {p} ({r})")

    print(f"\nProcessing {len(resolved)} files...")

    stats = {"updated": 0, "skip_correct": 0, "skip_read_error": 0, "skip_write_error": 0}
    updated_files = []
    corrected_files = []

    def process_one(item):
        file_path, path_str, module_id, bp_path = item
        return process_file(file_path, module_id, bp_path), path_str

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_one, item): item for item in resolved}
        for future in as_completed(futures):
            result, path_str = future.result()
            if result == "updated":
                stats["updated"] += 1
                updated_files.append(path_str)
            elif result == "skip_correct":
                stats["skip_correct"] += 1
            elif result.startswith("skip"):
                stats[result] += 1

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total empty blueprint_id nodes: {len(empty_bp_nodes)}")
    print(f"Resolved (mapping found):       {len(resolved)}")
    print(f"Unresolved (no mapping):        {len(unresolved)}")
    print(f"Files updated:                  {stats['updated']}")
    print(f"Skipped (already correct):      {stats['skip_correct']}")
    print(f"Skipped (read error):           {stats['skip_read_error']}")
    print(f"Skipped (write error):          {stats['skip_write_error']}")

    if updated_files:
        print("\nUpdated files (first 30):")
        for f in sorted(updated_files)[:30]:
            print(f"  + {f}")
        if len(updated_files) > 30:
            print(f"  ... and {len(updated_files) - 30} more")


if __name__ == "__main__":
    main()
