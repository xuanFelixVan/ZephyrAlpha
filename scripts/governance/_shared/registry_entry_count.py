# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/registry_entry_count.py | §
# [MODULE] scripts.governance._shared.registry_entry_count
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""登记表主条目计数——与 generate_registry_master_index 单一真源对齐。

validate_registry_master_index 等门禁必须使用本模块，禁止用「YAML 中最长 list」启发式。
"""

from __future__ import annotations

from typing import Any


def count_primary_registry_entries(data: dict[str, Any], file_stem: str) -> int:
    """按登记表类型统计主条目列表长度（与 _count_primary_list 逻辑一致）。"""
    if not isinstance(data, dict):
        return 0

    if file_stem in ("registry_of_registries", "registry_consistency_contract"):
        return len(data.get("registries", [])) + len(data.get("cross_registry_rules", []))

    if file_stem == "task-card-meta-registry":
        mr = data.get("migration_rules")
        if isinstance(mr, list):
            return len(mr)
        return 0

    order = (
        "files",
        "gates",
        "directories",
        "risks",
        "dependencies",
        "infrastructure",
        "contracts",
        "scripts",
        "fields",
        "sessions",
        "knowledge_entries",
        "adr_entries",
        "documents",
        "entries",
        "registries",
        "interfaces",  # P5 修复：interface_contract_registry.yaml 的主键是 interfaces
    )
    for key in order:
        v = data.get(key)
        if isinstance(v, list):
            return len(v)
    return 0


def primary_count_entry_key(data: dict[str, Any], file_stem: str) -> str:
    """返回用于日志/告警展示的键名（合成计数时用 '+' 连接）。"""
    if file_stem in ("registry_of_registries", "registry_consistency_contract"):
        r, c = len(data.get("registries", []) or []), len(data.get("cross_registry_rules", []) or [])
        return f"registries({r})+cross_registry_rules({c})"
    if file_stem == "task-card-meta-registry":
        return "migration_rules"
    order = (
        "files",
        "gates",
        "directories",
        "risks",
        "dependencies",
        "infrastructure",
        "contracts",
        "scripts",
        "fields",
        "sessions",
        "knowledge_entries",
        "adr_entries",
        "documents",
        "entries",
        "registries",
        "interfaces",  # P5 修复：interface_contract_registry.yaml 的主键是 interfaces
    )
    for key in order:
        v = data.get(key)
        if isinstance(v, list):
            return key
    return "(none)"
