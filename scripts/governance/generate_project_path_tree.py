# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §
# [MODULE] scripts.governance.generate_project_path_tree
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] AI cold-start; depgraph generator; migration tasks
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] --write MUST preserve design-state nodes; output MUST be valid YAML
# [MODIFY-GUARD] PostgreSQL arch_directory_tree
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PanoramaLoadError
# [TESTS]
# [TTL] task_bound
"""从磁盘扫描生成路径全景图的tree段（运营态目录结构）。

核心变更（DM-283/DM-310）:
  - 输出写入 depgraph 的 tree 段（而非独立文件）
  - 每个目录节点输出 lifecycle/__domain_id__/__subdomain_id__/__target_path__
  - 双态保护：生成运营态时不覆盖设计态节点（lifecycle: design 优先于 operational）
  - DM-310: __state__ 统一为 lifecycle 字段（与 depgraph 一致）

用法:
    python scripts/governance/generate_project_path_tree.py            # stdout
    python scripts/governance/generate_project_path_tree.py --write    # 覆写全景图tree段
    python scripts/governance/generate_project_path_tree.py --check    # CI 漂移检测
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 从磁盘扫描生成路径全景图的tree段（运营态目录结构）。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import logging
# 治本（2026-06-29）：删除 import os / import subprocess（锁剧场删除后无使用）。
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402

PROJECT_ROOT = REPO_ROOT


def _yaml_load(path):
    """Load YAML with C loader if available (10-50x faster than pure Python)."""
    try:
        from yaml import CSafeLoader

        loader = CSafeLoader
    except ImportError:
        loader = yaml.SafeLoader
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=loader)


def _load_panorama_from_db(db_path):
    """Load panorama data from PostgreSQL database, returning a dict compatible with the old YAML structure.

    P2迁移后：depgraph 已迁移到 PostgreSQL。db_path 参数保留用于日志引用。
    Reads from: domains table, arch_directory_tree table, arch_path_mappings table.
    Returns dict with keys: domains, tree, meta, and optional path sections.
    """
    conn = get_depgraph_pg_connection(autocommit=True)
    data = {"domains": {}, "tree": {}, "meta": {}}

    # Load domains — map to the same structure as the YAML panorama domains section
    for row in conn.execute("SELECT * FROM domains"):
        domain = dict(row)
        did = domain.pop("domain_id")
        domain_entry = {
            "parent_domain": domain.get("domain_group", ""),
            "domain_id": did,
            "subdomain_id": did,
            "ssot_path": domain.get("ssot_path", ""),
            "ssot_module": "",
            "covers": [],
            "aliases": [],
            "change_policy": domain.get("lifecycle", ""),
            "impact_level": "M",
            "modification_permission": "",
        }
        data["domains"][did] = domain_entry

    # Enrich domains with covers/aliases from arch_path_mappings
    for row in conn.execute("SELECT * FROM arch_path_mappings"):
        mapping = dict(row)
        did = mapping.get("domain_id", "")
        if did in data["domains"]:
            covers_raw = mapping.get("covers", "")
            if covers_raw:
                try:
                    data["domains"][did]["covers"] = json.loads(covers_raw)
                except (json.JSONDecodeError, TypeError):
                    data["domains"][did]["covers"] = [covers_raw] if covers_raw else []
            aliases_raw = mapping.get("aliases", "")
            if aliases_raw:
                try:
                    data["domains"][did]["aliases"] = json.loads(aliases_raw)
                except (json.JSONDecodeError, TypeError):
                    data["domains"][did]["aliases"] = [aliases_raw] if aliases_raw else []

    # Build tree structure from arch_directory_tree
    tree = {}
    for row in conn.execute("SELECT * FROM arch_directory_tree ORDER BY path"):
        entry = dict(row)
        path = entry.get("path", "")
        if not path:
            continue
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

    # Load metadata
    try:
        cur = conn.execute("SELECT version FROM _schema_version ORDER BY version DESC LIMIT 1")
        r = cur.fetchone()
        if r:
            data["meta"]["schema_version"] = r["version"]
    except Exception:
        pass

    conn.close()
    return data


def _write_tree_to_db(db_path, tree, total_files, total_dirs):
    """Write tree structure to PostgreSQL arch_directory_tree table.

    P2迁移后：depgraph 已迁移到 PostgreSQL。db_path 参数保留用于日志引用。
    Clears existing operational rows (preserves design-state), then inserts new ones.
    """
    conn = get_depgraph_pg_connection(autocommit=False)
    try:
        # Clear existing operational data (preserve design-state)
        conn.execute("DELETE FROM arch_directory_tree WHERE COALESCE(design_maturity, '') != 'design'")

        def _insert_tree_node(cursor, path, node_data, parent_path=None):
            """Recursively insert tree nodes."""
            state = node_data.get("lifecycle", "operational")
            # Skip design-state nodes (already in DB)
            if state == "design":
                return

            cursor.execute(
                """INSERT INTO arch_directory_tree
                (path, parent_path, path_type, domain_id, design_maturity, blueprint_id,
                 change_policy, modification_permission, build_status, last_scanned)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (path) DO NOTHING""",
                (
                    path,
                    parent_path,
                    "directory",
                    node_data.get("__domain_id__", ""),
                    state,
                    node_data.get("__blueprint_id__", ""),
                    node_data.get("__stability__", node_data.get("change_policy", "")),
                    node_data.get("__ai_autonomy__", node_data.get("modification_permission", "")),
                    node_data.get("build_status", "unbuilt"),
                    datetime.now(UTC).isoformat(),
                ),
            )

            # Recurse into children
            for key, val in node_data.items():
                if key.startswith("__") or not isinstance(val, dict):
                    continue
                child_path = f"{path}/{key}" if path else key
                _insert_tree_node(cursor, child_path, val, path)

        # Insert all root nodes
        for root_name, root_data in tree.items():
            if isinstance(root_data, dict):
                _insert_tree_node(conn, root_name, root_data)

        conn.commit()
        count = conn.execute("SELECT COUNT(*) AS cnt FROM arch_directory_tree").fetchone()["cnt"]
        print(f"[PATH-TREE-DB] Updated {count} directory tree nodes")
    except Exception as e:
        conn.rollback()
        print(f"[PATH-TREE-DB] ERROR: {e}")
        raise
    finally:
        conn.close()


# 治本（2026-06-29）：删除 DEPGRAPH_DB_PATH = PROJECT_ROOT / "data" / "databases" / "depgraph.db"。
# P2 PG 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。
# 此常量指向往已归档 .db 文件，是路径污染源（对齐 apply_depgraph.py / extract_depgraph.py 已治本）。
# _load_panorama_from_db / _write_tree_to_db 的 db_path 参数保留但 PG 模式下不使用（传 None）。

SCAN_ROOTS = ["src/zephyr", "scripts", "tests", "config", "docs", "data"]
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".ailocks",
    ".audit_cache",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    ".idea",
    ".vs",
    ".eggs",
    "*.egg-info",
    "cache",
    "telemetry",
}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".so", ".dll", ".exe", ".obj", ".pdb", ".idb"}
MAX_DEPTH = 8

logger = logging.getLogger(__name__)


def _should_skip_dir(name: str) -> bool:
    if name in SKIP_DIRS:
        return True
    if name.endswith(".egg-info"):
        return True
    return False


def load_domain_derivation() -> dict:
    """Load domain derivation from panorama's domains section.

    Panorama has 35 flat functional domains, each with:
      - domain_id: functional domain name (e.g., "capacity-assurance")
      - ssot_path: target directory path
      - parent_domain: parent domain name (for architecture_layer)

    Returns:
        {path_prefix: {domain_id, subdomain_id}} sorted by prefix length desc.
    """
    # P2迁移后：depgraph 已迁移到 PostgreSQL，不再检查 .db 文件是否存在
    try:
        data = _load_panorama_from_db(None)
    except Exception:
        return {}
    if not data:
        return {}

    derivation = {}

    # From domains section (35 flat functional domains)
    domains_data = data.get("domains", {})
    for func_domain_name, func_domain_val in domains_data.items():
        if not isinstance(func_domain_val, dict):
            continue
        domain_id = func_domain_val.get("domain_id", func_domain_name)
        subdomain_id = func_domain_val.get("subdomain_id", "")
        ssot_path = (func_domain_val.get("ssot_path") or "").replace("\\", "/").rstrip("/") + "/"
        if ssot_path and domain_id:
            derivation[ssot_path] = {
                "domain_id": domain_id,
                "subdomain_id": subdomain_id,
            }

    # From tree section (current operational paths with __domain_id__)
    tree_data = data.get("tree", {})
    _extract_tree_domain_ids(tree_data, "", derivation)

    # From path design sections (blueprint_paths, test_paths, etc.)
    # These define design-state paths for non-code areas
    path_sections = [
        "blueprint_paths",
        "test_paths",
        "script_paths",
        "knowledge_paths",
        "data_paths",
        "gate_paths",
        "frontend_paths",
    ]
    for section_name in path_sections:
        section_data = data.get(section_name)
        if not section_data or not isinstance(section_data, dict):
            continue
        _extract_path_section_domains(section_data, section_name, derivation)

    # Sort by key length descending for best prefix match
    derivation = dict(sorted(derivation.items(), key=lambda x: len(x[0]), reverse=True))

    # Fallback: add path prefixes not covered by domains table ssot_path
    # These directories contain governance/utility/config files, mapped to closest domain
    PATH_DOMAIN_FALLBACK = {
        # scripts/ — governance/utility scripts
        "scripts/governance/": "D_GOVERNANCE",
        "scripts/data/": "D_DATA_ENG",
        "scripts/construction/": "D_GOVERNANCE",
        "scripts/autonomy_core/": "D_AUTONOMY_CORE",
        "scripts/cleanup/": "D_GOVERNANCE",
        "scripts/connect/": "D_INTEGRATION",
        "scripts/database/": "D_DATA_ENG",
        "scripts/repair/": "D_GOVERNANCE",
        "scripts/": "D_GOVERNANCE",
        # data/ — data files and databases
        "data/databases/": "D_DATA_ENG",
        "data/asset_index/": "D_GOVERNANCE",
        "data/metrics/": "D_GOVERNANCE",
        "data/reports/": "D_GOVERNANCE",
        "data/": "D_DATA_ENG",
        # docs/ — governance documentation
        "docs/03_modules/": "D_GOVERNANCE",
        "docs/01_policies_and_standards/": "D_GOVERNANCE",
        "docs/02_enterprise_architecture/": "D_GOVERNANCE",
        "docs/": "D_GOVERNANCE",
        # tests/ — quality assurance
        "tests/": "D_GOVERNANCE",
        # config/ — configuration
        "config/": "D_GOVERNANCE",
        # agent_spec/ — agent specifications
        "agent_spec/": "D_AUTONOMY_CORE",
    }
    for prefix, did in PATH_DOMAIN_FALLBACK.items():
        if prefix not in derivation:
            derivation[prefix] = {"domain_id": did, "subdomain_id": ""}

    # Re-sort after adding fallbacks
    derivation = dict(sorted(derivation.items(), key=lambda x: len(x[0]), reverse=True))

    return derivation


def _extract_tree_domain_ids(tree_node: dict, current_path: str, derivation: dict) -> None:
    """Recursively extract domain_id from panorama tree section."""
    if not isinstance(tree_node, dict):
        return
    domain_id = tree_node.get("__domain_id__", "")
    subdomain_id = tree_node.get("__subdomain_id__", "")
    if domain_id and current_path:
        prefix = (current_path or "").replace("\\", "/")
        if not prefix.endswith("/"):
            prefix += "/"
        if prefix not in derivation:
            derivation[prefix] = {"domain_id": domain_id, "subdomain_id": subdomain_id}
    for key, val in tree_node.items():
        if key.startswith("__") or not isinstance(val, dict):
            continue
        child_path = f"{current_path}/{key}" if current_path else key
        _extract_tree_domain_ids(val, child_path, derivation)


def _extract_path_section_domains(section_data: dict, section_name: str, derivation: dict) -> None:
    """Extract domain derivation entries from path design sections.

    Path sections like blueprint_paths define design_root and structure patterns
    like '{design_root}{domain_id}/'. We expand these patterns using the 35
    functional domains to create derivation entries for each domain's path.
    """
    design_root = (section_data.get("design_root") or "").replace("\\", "/").rstrip("/") + "/"
    if not design_root or design_root == "/":
        return

    # Map section names to domain derivation
    # blueprint_paths → registry_management (blueprints are governance artifacts)
    # test_paths → code_dedup (tests are quality assurance)
    # script_paths → script_governance
    # etc.
    SECTION_DOMAIN_MAP = {
        "blueprint_paths": "registry_management",
        "test_paths": "code_dedup",
        "script_paths": "script_governance",
        "knowledge_paths": "knowledge_management",
        "data_paths": "persistence",
        "gate_paths": "gate_orchestration",
        "frontend_paths": "runtime_integration",
    }
    section_domain = SECTION_DOMAIN_MAP.get(section_name, "")

    # Add the design_root itself with the section's domain
    if section_domain:
        derivation[design_root] = {"domain_id": section_domain, "subdomain_id": ""}

    # If structure contains {domain_id}, expand for each known domain
    structure = section_data.get("structure") or ""
    if "{domain_id}" in structure and section_domain:
        # Load domain IDs from panorama domains section
        panorama = {}
        try:
            panorama = _load_panorama_from_db(None) or {}
        except Exception:
            pass
        domains_data = panorama.get("domains", {})
        for func_domain_name, func_domain_val in domains_data.items():
            if not isinstance(func_domain_val, dict):
                continue
            domain_id = func_domain_val.get("domain_id") or func_domain_name
            expanded = structure.replace("{design_root}", design_root).replace("{domain_id}", domain_id)
            expanded = (expanded or "").replace("\\", "/").rstrip("/") + "/"
            if expanded not in derivation:
                derivation[expanded] = {"domain_id": domain_id, "subdomain_id": ""}


def derive_domain_for_path(rel_path: str, domain_derivation: dict) -> tuple:
    """Derive domain_id and subdomain_id from path using panorama derivation.

    Returns: (domain_id, subdomain_id)
    """
    rp = (rel_path or "").replace("\\", "/") + "/"
    for prefix, info in domain_derivation.items():
        if rp.startswith(prefix):
            return info["domain_id"], info["subdomain_id"]
    return "", ""


def scan_directory(root: Path, prefix: str = "", depth: int = 0, domain_derivation: dict = None) -> dict:
    if depth > MAX_DEPTH:
        return {"__truncated__": True}

    if domain_derivation is None:
        domain_derivation = {}

    dirs: dict[str, dict] = {}
    files: list[str] = []

    try:
        entries = sorted(root.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        return {"__permission_denied__": True}

    for entry in entries:
        if entry.name.startswith(".") and entry.name not in {".env", ".pre_commit-config.yaml"}:
            continue
        if entry.is_dir():
            if _should_skip_dir(entry.name):
                continue
            subdir = scan_directory(
                entry,
                prefix=f"{prefix}/{entry.name}",
                depth=depth + 1,
                domain_derivation=domain_derivation,
            )
            if subdir:
                dirs[entry.name] = subdir
        elif entry.is_file():
            if entry.suffix in SKIP_EXTENSIONS:
                continue
            files.append(entry.name)

    result: dict = {}
    result["lifecycle"] = "operational"

    # Derive domain info for this directory
    domain_id, subdomain_id = derive_domain_for_path(prefix, domain_derivation)
    result["__domain_id__"] = domain_id
    result["__subdomain_id__"] = subdomain_id
    result["__target_path__"] = None

    if files:
        result["__files__"] = files
        result["__file_count__"] = len(files)
    if dirs:
        result.update(dirs)
    return result


def count_tree(tree: dict) -> tuple[int, int]:
    file_count = tree.get("__file_count__", 0)
    dir_count = 0
    for key, val in tree.items():
        if key.startswith("__"):
            continue
        if isinstance(val, dict):
            dir_count += 1
            fc, dc = count_tree(val)
            file_count += fc
            dir_count += dc
    return file_count, dir_count


def merge_with_design_nodes(new_tree: dict, old_tree: dict) -> dict:
    """Merge new operational tree with old tree, preserving design-state nodes.

    For each directory node in old_tree:
    - If lifecycle == "design", preserve it entirely (don't overwrite)
    - If lifecycle == "operational" or no lifecycle, use new_tree's version
    - If a node exists in old_tree but not in new_tree and is design-state, keep it
    - If lifecycle == "pending_deletion", preserve it (migration in progress)
    - If lifecycle is a dict (legacy from __state__ migration), fix it
    """
    if not old_tree:
        return new_tree

    merged = dict(new_tree)

    for key, old_val in old_tree.items():
        if key.startswith("__"):
            continue
        if not isinstance(old_val, dict):
            continue

        # Fix legacy dict lifecycle values
        _fix_dict_lifecycle(old_val)

        if key not in merged:
            # Node exists in old but not new — preserve if design-state or pending_deletion
            if old_val.get("lifecycle") in ("design", "pending_deletion"):
                merged[key] = old_val
        else:
            # Node exists in both — recurse, but preserve design-state children
            new_val = merged[key]
            if isinstance(new_val, dict):
                if old_val.get("lifecycle") in ("design", "pending_deletion"):
                    # Old node is design/pending_deletion, preserve it entirely
                    merged[key] = old_val
                else:
                    # Both operational, merge children recursively
                    merged[key] = merge_with_design_nodes(new_val, old_val)

    return merged


def _fix_dict_lifecycle(node: dict) -> None:
    """Fix legacy dict lifecycle values from __state__→lifecycle migration.

    Some old design-state nodes had their entire metadata dict as the __state__ value.
    After renaming __state__→lifecycle, the lifecycle field became a dict like:
      lifecycle: {lifecycle: operational, __domain_id__: ..., ...}
    This function extracts the string lifecycle value and merges remaining keys.
    """
    lc = node.get("lifecycle")
    if not isinstance(lc, dict):
        return
    # Extract the nested string lifecycle value
    nested_lc = lc.get("lifecycle", "")
    if isinstance(nested_lc, str) and nested_lc:
        node["lifecycle"] = nested_lc
        # Merge remaining keys from the dict into the node (if not already present)
        for k, v in lc.items():
            if k != "lifecycle" and k not in node:
                node[k] = v
    elif "__truncated__" in lc:
        node["lifecycle"] = "operational"
    else:
        # Fallback: just set to operational
        node["lifecycle"] = "operational"


def _fix_all_dict_lifecycle(tree: dict) -> int:
    """Walk entire tree and fix all dict lifecycle values. Returns count fixed."""
    fixed = 0
    if not isinstance(tree, dict):
        return 0
    _fix_dict_lifecycle(tree)
    if isinstance(tree.get("lifecycle"), str):
        # Was just fixed
        pass
    for key, val in tree.items():
        if key.startswith("__") or not isinstance(val, dict):
            continue
        fixed += _fix_all_dict_lifecycle(val)
    return fixed


def generate_tree(domain_derivation: dict) -> dict:
    """Generate the full tree structure from disk scan."""
    tree = {}
    for root_name in SCAN_ROOTS:
        root_path = PROJECT_ROOT / root_name
        if not root_path.exists():
            tree[root_name] = {"lifecycle": "absent"}
            continue
        subtree = scan_directory(root_path, prefix=root_name, domain_derivation=domain_derivation)
        tree[root_name] = subtree
    return tree


def _mark_pending_deletion(tree: dict, target_path: str) -> bool:
    """Mark an operational node as pending_deletion if its files have been migrated.

    target_path is a relative path like 'src/zephyr/old_module/file.py'.
    Walk the tree to find the node and mark it.
    Returns True if marked, False if not found or already marked.
    """
    parts = (target_path or "").replace("\\", "/").split("/")
    current = tree
    # Walk to the parent directory
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    # The last part is the file or directory name
    last = parts[-1]
    if not isinstance(current, dict):
        return False

    # Check if it's a file in __files__ list
    if "__files__" in current and last in current["__files__"]:
        # File exists in this directory — mark the directory as pending_deletion
        # if it's operational and the specific file has been migrated
        if current.get("lifecycle") == "operational":
            current["lifecycle"] = "pending_deletion"
            return True
        return False

    # Check if it's a subdirectory
    if last in current and isinstance(current[last], dict):
        node = current[last]
        if node.get("lifecycle") == "operational":
            node["lifecycle"] = "pending_deletion"
            return True
        return False

    return False


def cmd_write() -> None:
    """Write tree to PostgreSQL arch_directory_tree, preserving design-state nodes.

    治本（2026-06-29）：删除文件锁剧场（对齐 apply_depgraph.py / sync_yaml_to_depgraph.py）。
    P2 PG 迁移后 depgraph 已迁至 PostgreSQL，PG MVCC 事务（autocommit=False）提供原子性，
    文件锁对 PG 写无保护作用（锁键指向往已归档 .db 文件，语义悬空）。
    迁移文档 §7 漏删此脚本的锁，本次治本补齐。
    """
    # === PHASE 1: Compute (read-only / pure computation) ===
    domain_derivation = load_domain_derivation()
    print(f"[PATH-TREE] Loaded {len(domain_derivation)} domain derivation entries")

    new_tree = generate_tree(domain_derivation)

    migration_registry_path = PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "migration-registry.yaml"
    pending_entries = []
    if migration_registry_path.exists():
        try:
            reg = _yaml_load(migration_registry_path)
            if reg and "entries" in reg:
                for entry in reg["entries"]:
                    if entry.get("status") == "completed":
                        continue
                    old_p = (entry.get("old_path") or "").replace("\\", "/")
                    new_p = (entry.get("new_path") or "").replace("\\", "/")
                    if not old_p or not new_p:
                        continue
                    new_disk = PROJECT_ROOT / new_p
                    if new_disk.exists():
                        pending_entries.append(old_p)
        except Exception:
            pass

    print("[PATH-TREE] Computation done. Ready to write.")

    # === PHASE 2: Read → Merge → Write (PG MVCC 保护，无需文件锁) ===
    try:
        panorama = _load_panorama_from_db(None)
    except Exception as e:
        print(f"[FAIL] Cannot load panorama: {e}")
        sys.exit(1)

    if not panorama:
        print("[FAIL] Panorama is empty")
        sys.exit(1)

    old_tree = panorama.get("tree", {})
    merged_tree = merge_with_design_nodes(new_tree, old_tree)
    _fix_all_dict_lifecycle(merged_tree)

    pending_count = 0
    for old_p in pending_entries:
        if _mark_pending_deletion(merged_tree, old_p):
            pending_count += 1
    if pending_count:
        print(f"[PATH-TREE] Marked {pending_count} nodes as pending_deletion")

    total_files = 0
    total_dirs = 0
    for root_name, subtree in merged_tree.items():
        if isinstance(subtree, dict):
            fc, dc = count_tree(subtree)
            total_files += fc
            total_dirs += dc

    _write_tree_to_db(None, merged_tree, total_files, total_dirs)

    print("[OK] Tree written to PostgreSQL arch_directory_tree")
    print(f"     Files: {total_files} | Directories: {total_dirs}")


def cmd_check() -> None:
    """Check if panorama tree is in sync with disk."""
    # P2迁移后：depgraph 已迁移到 PostgreSQL，不再检查 .db 文件是否存在
    try:
        panorama = _load_panorama_from_db(None)
    except Exception as e:
        print(f"[FAIL] Cannot load panorama: {e}")
        sys.exit(1)

    domain_derivation = load_domain_derivation()
    new_tree = generate_tree(domain_derivation)
    old_tree = panorama.get("tree", {})

    # Compare only operational nodes (strip design-state from old_tree for comparison)
    def strip_design(tree: dict) -> dict:
        result = {}
        for key, val in tree.items():
            if key.startswith("__"):
                if key != "lifecycle":
                    result[key] = val
                continue
            if isinstance(val, dict):
                if val.get("lifecycle") in ("design", "pending_deletion"):
                    continue
                result[key] = strip_design(val)
            else:
                result[key] = val
        return result

    new_stripped = strip_design(new_tree)
    old_stripped = strip_design(old_tree)

    new_yaml = yaml.dump(new_stripped, allow_unicode=True, default_flow_style=False, sort_keys=True)
    old_yaml = yaml.dump(old_stripped, allow_unicode=True, default_flow_style=False, sort_keys=True)

    if new_yaml != old_yaml:
        print("[FAIL] Panorama tree is OUT OF SYNC with disk.")
        print("       Run: python scripts/governance/generate_project_path_tree.py --write")
        sys.exit(1)
    else:
        print("[OK] Panorama tree is in sync with disk.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate panorama tree section (PostgreSQL arch_directory_tree)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write", action="store_true", help="Write tree to PostgreSQL arch_directory_tree (preserves design-state rows)"
    )
    group.add_argument("--check", action="store_true", help="CI mode: exit 1 if mismatch")
    args = parser.parse_args()

    if args.check:
        cmd_check()
    elif args.write:
        cmd_write()
    else:
        # 默认输出 YAML 到 stdout（调试/预览用，不写 DB）
        domain_derivation = load_domain_derivation()
        tree = generate_tree(domain_derivation)
        print(yaml.dump({"tree": tree}, allow_unicode=True, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
