# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain-governance/registry-governance/blueprint.md | §
# [MODULE] scripts.migration._migration_shared
# [INVARIANTS] 所有搬家脚本共享的数据加载和批次筛选逻辑
# [MODIFY-GUARD] mapping/import格式变更时需同步更新
# [CONSUMERS] preflight_check; create_target_dirs; execute_move; update_imports; update_non_import_refs; verify_batch; rollback_batch; lock_batch
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError:data_files -> exit 1
# [TESTS] tests/test_migration_shared.py
"""搬家脚本共享模块——数据加载、批次筛选、原子写入。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPING_FILE = PROJECT_ROOT / "data" / "asset_index" / "path-migration-mapping.yaml"
IMPORT_MANIFEST_FILE = PROJECT_ROOT / "data" / "asset_index" / "import-update-manifest.yaml"
MIGRATION_LOG_FILE = PROJECT_ROOT / "data" / "asset_index" / "migration-log.yaml"
PATH_TREE_FILE = PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "project-path-tree.yaml"

BATCH_TO_GROUP = {
    1: "cross_cutting_infra",
    2: "data_upstream",
    3: "core_value_chain",
    4: "enhanced_extension",
}


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed.", file=sys.stderr)
        sys.exit(2)
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print(f"[ERROR] Invalid YAML structure in {path}", file=sys.stderr)
        sys.exit(2)
    return data


def save_yaml(path: Path, data: dict) -> None:
    import yaml
    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    atomic_write(path, content)


def atomic_write(path: Path, content: str) -> None:
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def load_mapping() -> list[dict]:
    data = load_yaml(MAPPING_FILE)
    return data.get("mappings", [])


def filter_by_batch(mappings: list[dict], batch: int) -> list[dict]:
    group = BATCH_TO_GROUP.get(batch)
    if not group:
        print(f"[ERROR] Unknown batch: {batch}. Valid: 1-4", file=sys.stderr)
        sys.exit(1)
    return [m for m in mappings if m.get("domain_group") == group]


def filter_by_all_batches(mappings: list[dict]) -> list[dict]:
    groups = set(BATCH_TO_GROUP.values())
    return [m for m in mappings if m.get("domain_group") in groups]


def load_import_manifest() -> list[dict]:
    data = load_yaml(IMPORT_MANIFEST_FILE)
    return data.get("updates", [])


def filter_imports_by_domains(updates: list[dict], domains: set[str]) -> list[dict]:
    result = []
    for upd in updates:
        filepath = upd.get("file", "")
        parts = filepath.replace("\\", "/").split("/")
        matched = False
        for domain_dir in domains:
            if domain_dir in parts:
                matched = True
                break
        if not matched:
            for change in upd.get("changes", []):
                old = change.get("old", "")
                new = change.get("new", "")
                for domain_dir in domains:
                    if domain_dir in old or domain_dir in new:
                        matched = True
                        break
                if matched:
                    break
        if matched:
            result.append(upd)
    return result


def get_domain_dirs_for_batch(batch: int) -> set[str]:
    mappings = load_mapping()
    batch_mappings = filter_by_batch(mappings, batch)
    dirs = set()
    for m in batch_mappings:
        tp = m.get("target_path", "")
        parts = tp.replace("\\", "/").split("/")
        if len(parts) >= 3:
            dirs.add(parts[2])
    return dirs


def load_migration_log() -> dict:
    if not MIGRATION_LOG_FILE.exists():
        return {"batches": []}
    return load_yaml(MIGRATION_LOG_FILE)


def save_migration_log(log: dict) -> None:
    save_yaml(MIGRATION_LOG_FILE, log)
