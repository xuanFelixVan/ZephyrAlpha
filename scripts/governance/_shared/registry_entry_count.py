# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/registry_entry_count.py | §
# [MODULE] scripts.governance._shared.registry_entry_count
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS] scripts.governance.d3_metadata.validate_registry_master_index; scripts.governance.d3_metadata.check_registry_consistency; scripts.governance.generators.generate_registry_master_index; scripts.governance.generators.refresh_master_entries
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 口径真源=登记表自述 counting_rule（或 ROOR 传入）；解析不出=不数（禁"最长 list"启发式）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/test_registry_derivation_canary.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""登记表主条目计数——与 generate_registry_master_index 单一真源对齐。

validate_registry_master_index 等门禁必须使用本模块，禁止用「YAML 中最长 list」启发式。
CR-007 口径派生（2026-09-30）：ROOR/册内自述 counting_rule 即口径真源，
键白名单降级为"无声明册"的兜底覆写。
"""

from __future__ import annotations

import re
from typing import Any

# 口径文本 → (kind, key) 解析（只认显式声明格式；解析不出返回 None）：
#   "<key> 数组条目数"                     → ("yaml_list", key)
#   "<key> 条目数（<说明>）"               → ("yaml_list", key)
#   "<key.a> + <key.b> 条目数合计"         → ("yaml_sum", "key.a+key.b")
#   "<key> 子系统数"                       → ("yaml_dict_len", key)
#   行数/快照头字段类口径（如 meta_question 主表行数）不可由 YAML 结构数出 → None
_LIST_RULE_RE = re.compile(r"^([\w.]+)\s*(?:数组)?条目数(?:（[^）]*）)?$")
_SUM_RULE_RE = re.compile(r"^([\w.]+(?:\s*\+\s*[\w.]+)+)\s+条目数合计$")
_DICT_RULE_RE = re.compile(r"^([\w.]+)\s+子系统数$")

# 无声明册的既有键白名单（兜底覆写，非真源）
_KEY_ORDER = (
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

# 口径真源优先于白名单的例外：这些册的专用口径本身写在分支里，counting_rule 散文
# 只是说明文字，不参与解析
_SPECIAL_STEMS = ("registry_of_registries", "registry_consistency_contract", "task-card-meta-registry")


def parse_counting_rule(rule: Any) -> tuple[str, str] | None:
    """解析 counting_rule 口径文本 → (kind, key)；解析不出返回 None（禁启发式猜键）。

    kind ∈ yaml_list / yaml_sum / yaml_dict_len；行数类口径（快照头 row_count 等）
    不可由 YAML 结构派生，返回 None 由对账侧报 UNSPECIFIED/MANUAL。
    """
    if not isinstance(rule, str):
        return None
    text = rule.strip()
    if not text:
        return None
    m = _SUM_RULE_RE.match(text)
    if m:
        return ("yaml_sum", re.sub(r"\s+", "", m.group(1)))
    m = _LIST_RULE_RE.match(text)
    if m:
        return ("yaml_list", m.group(1))
    m = _DICT_RULE_RE.match(text)
    if m:
        return ("yaml_dict_len", m.group(1))
    return None


def _declared_rule(data: dict[str, Any], counting_rule: str | None) -> str | None:
    """口径文本取用顺序：显式传入（ROOR 带来）优先，否则册内自述。"""
    if counting_rule is not None:
        return counting_rule
    v = data.get("counting_rule")
    return v if isinstance(v, str) else None


def _count_by_spec(data: dict[str, Any], kind: str, key: str) -> int:
    """按解析出的 (kind, key) 机械数数；键面不符返回 0（不虚报，让对账侧报问题）。"""
    if kind == "yaml_list":
        v = data.get(key)
        return len(v) if isinstance(v, list) else 0
    if kind == "yaml_dict_len":
        v = data.get(key)
        return len(v) if isinstance(v, dict) else 0
    if kind == "yaml_sum":
        total = 0
        for part in key.split("+"):
            current: Any = data
            for segment in part.split("."):
                if isinstance(current, dict):
                    current = current.get(segment)
                else:
                    return 0
            if not isinstance(current, list):
                return 0
            total += len(current)
        return total
    return 0


def _key_by_spec(data: dict[str, Any], kind: str, key: str) -> str | None:
    """口径键名展示（yaml_sum 合成 '+' 连接）；键面不符返回 None。"""
    if kind == "yaml_sum":
        return key
    v = data.get(key)
    if kind == "yaml_list" and isinstance(v, list):
        return key
    if kind == "yaml_dict_len" and isinstance(v, dict):
        return key
    return None


def count_primary_registry_entries(data: dict[str, Any], file_stem: str, counting_rule: str | None = None) -> int:
    """按登记表类型统计主条目列表长度。

    口径优先级：显式 counting_rule 参数（ROOR 带来）> 册内自述 counting_rule >
    既有键白名单（无声明册兜底）。声明口径键面不符 ⇒ 返回 0（不猜）。
    """
    if not isinstance(data, dict):
        return 0

    rule_text = _declared_rule(data, counting_rule)
    if rule_text and file_stem not in _SPECIAL_STEMS:
        spec = parse_counting_rule(rule_text)
        if spec is not None:
            return _count_by_spec(data, spec[0], spec[1])
        # 声明了解析不出的口径（行数类/散文）⇒ 不数，交对账侧判 UNSPECIFIED
        return 0

    if file_stem in ("registry_of_registries", "registry_consistency_contract"):
        return len(data.get("registries", [])) + len(data.get("cross_registry_rules", []))

    if file_stem == "task-card-meta-registry":
        mr = data.get("migration_rules")
        if isinstance(mr, list):
            return len(mr)
        return 0

    for key in _KEY_ORDER:
        v = data.get(key)
        if isinstance(v, list):
            return len(v)
    return 0


def primary_count_entry_key(data: dict[str, Any], file_stem: str, counting_rule: str | None = None) -> str:
    """返回用于日志/告警展示的键名（合成计数时用 '+' 连接）。"""
    if not isinstance(data, dict):
        return "(none)"

    rule_text = _declared_rule(data, counting_rule)
    if rule_text and file_stem not in _SPECIAL_STEMS:
        spec = parse_counting_rule(rule_text)
        if spec is not None:
            shown = _key_by_spec(data, spec[0], spec[1])
            if shown is not None:
                return shown
        return "(declared-unparsed)"

    if file_stem in ("registry_of_registries", "registry_consistency_contract"):
        r, c = len(data.get("registries", []) or []), len(data.get("cross_registry_rules", []) or [])
        return f"registries({r})+cross_registry_rules({c})"
    if file_stem == "task-card-meta-registry":
        return "migration_rules"
    for key in _KEY_ORDER:
        v = data.get(key)
        if isinstance(v, list):
            return key
    return "(none)"
