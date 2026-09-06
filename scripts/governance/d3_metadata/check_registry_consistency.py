# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_registry_consistency.py | §
# [MODULE] scripts.governance.d3_metadata.check_registry_consistency
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] CR-001~006 只读不改文件；CR-007 默认只读，--update-entry-counts 显式授权才写 ROOR（行级手术保注释）；回填仅限 ENTRY_SPECS 已登记口径的 STALE 行
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/test_registry_entry_counts.py（CR-007 对账+回填）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_registry_consistency — 跨登记表一致性校验。

读取 registry_consistency_contract.yaml，按 cross_registry_rules 比对多登记表共享字段。
可将 Finding 写入 scripts/governance/reports/findings.jsonl。

CR-007（2026-09-06 Owner 批"账本数字自动回填"）：ROOR entry_count 实测对账——
按 ENTRY_SPECS 显式口径逐表数数，STALE/MISSING/UNSPECIFIED 即 FAIL（CI 执法）；
--update-entry-counts 行级手术回填（保注释保格式，仅动 STALE 行的数字，
值变更且缺 counting_rule 时补插口径行）。
"""

from __future__ import annotations

__manifest__ = {
    "args": [],
    "description": "跨登记表一致性校验（多注册表共享字段对账）",
    "dimensions": ["D3", "D5", "D11"],
    "priority": "P1",
    "timeout_seconds": 60,
    "warn_only": False,
}

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Iterator

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
try:
    from zephyr.infrastructure.script_system.finding import (
        BlastRadius,
        Dimension,
        Finding,
        FindingCollection,
        RemediationAction,
        Severity,
    )

    FINDING_AVAILABLE = True
except ImportError:
    FINDING_AVAILABLE = False
ROR_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry_consistency_contract.yaml"
)
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.yaml_utils import load_yaml


def get_nested_value(data: dict, yaml_path: str) -> str | None:
    """get nested value"""
    parts = yaml_path.replace("[]", "").split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            return current
        else:
            return None
    return current


def get_registry_value(registry_data: dict, yaml_path: str, module_id: str) -> str | None:
    """get registry value"""
    prefix = yaml_path.split("[]")[0]
    suffix = yaml_path.split("[].")[-1] if "[]." in yaml_path else ""
    items = registry_data.get(prefix, [])
    if isinstance(items, list):
        for item in items:
            if item.get("module_id") == module_id:
                if suffix:
                    parts = suffix.split(".")
                    current = item
                    for part in parts:
                        if isinstance(current, dict):
                            current = current.get(part)
                        else:
                            return None
                    return str(current) if current is not None else None
                return str(item) if item is not None else None
    return None


def get_physical_value(module_path_relative: str, frontmatter_key: str) -> str | None:
    """get physical value"""
    file_path = REPO_ROOT / "docs" / module_path_relative / "blueprint.md"
    if not file_path.exists():
        return None
    fm = parse_frontmatter_from_file(file_path) or {}
    val = fm.get(frontmatter_key)
    return str(val) if val is not None else None


def collect_module_ids(ror: dict, rule: dict) -> set:
    """collect module ids"""
    module_ids = set()
    for src in rule.get("sources", []):
        if "registry" in src:
            reg_info = next((r for r in ror["registries"] if r["id"] == src["registry"]), None)
            if reg_info:
                reg_path = REPO_ROOT / reg_info["path"]
                if reg_path.exists():
                    reg_data = load_yaml(reg_path)
                    prefix = src["yaml_path"].split("[]")[0]
                    items = reg_data.get(prefix, [])
                    if isinstance(items, list):
                        for item in items:
                            mid = item.get("module_id")
                            if mid:
                                module_ids.add(mid)
        elif src.get("source") == "physical_blueprint":
            module_ids_from_registry = set()
            for s2 in rule.get("sources", []):
                if "registry" in s2:
                    reg_info2 = next((r for r in ror["registries"] if r["id"] == s2["registry"]), None)
                    if not reg_info2:
                        continue
                    # 2026-09-05 AI-00 G2 收口：retired/derived 登记表 fail-open 跳过
                    # （对齐下方/本函数既有 exists() 姿态；此前本分支无防护致 FileNotFoundError 崩溃）
                    if reg_info2.get("status") in ("retired", "derived"):
                        continue
                    reg_path2 = REPO_ROOT / reg_info2["path"]
                    if not reg_path2.exists():
                        continue
                    reg_data2 = load_yaml(reg_path2)
                    prefix2 = s2["yaml_path"].split("[]")[0]
                    items2 = reg_data2.get(prefix2, [])
                    if isinstance(items2, list):
                        for item in items2:
                            mid = item.get("module_id")
                            if mid:
                                module_ids_from_registry.add(mid)
            if not module_ids_from_registry:
                for s2 in rule.get("sources", []):
                    if "registry" in s2:
                        reg_info2 = next((r for r in ror["registries"] if r["id"] == s2["registry"]), None)
                        if not reg_info2:
                            continue
                        if reg_info2.get("status") in ("retired", "derived"):
                            continue
                        reg_path2 = REPO_ROOT / reg_info2["path"]
                        if not reg_path2.exists():
                            continue
                        reg_data2 = load_yaml(reg_path2)
                        prefix2 = s2["yaml_path"].split("[]")[0]
                        items2 = reg_data2.get(prefix2, [])
                        if isinstance(items2, list):
                            for item in items2:
                                mid = item.get("module_id")
                                if mid:
                                    module_ids.add(mid)
            else:
                module_ids |= module_ids_from_registry
    return module_ids


def get_module_path(ror: dict, module_id: str) -> str | None:
    """get module path"""
    reg_info = next((r for r in ror["registries"] if r["id"] == "REG-001"), None)
    if reg_info:
        reg_path = REPO_ROOT / reg_info["path"]
        if reg_path.exists():
            reg_data = load_yaml(reg_path)
            items = reg_data.get("modules", [])
            for item in items:
                if item.get("module_id") == module_id:
                    path = item.get("path", "")
                    return path.replace("docs/", "").rstrip("/")
    return None


def check_rule(ror: dict, rule: dict) -> FindingCollection:
    """check rule"""
    collection = FindingCollection()
    rule_id = rule["rule_id"]
    consistency = rule.get("consistency", "exact")
    ssoT_source = rule.get("ssoT", "")
    if consistency == "derived":
        return collection
    module_ids = collect_module_ids(ror, rule)
    fields = rule.get("fields", [])
    for module_id in sorted(module_ids):
        module_path = get_module_path(ror, module_id)
        if not module_path:
            continue
        values = {}
        for src in rule.get("sources", []):
            source_label = src.get("registry", src.get("source", "unknown"))
            if "registry" in src:
                reg_info = next((r for r in ror["registries"] if r["id"] == src["registry"]), None)
                if not reg_info:
                    continue
                reg_path = REPO_ROOT / reg_info["path"]
                if not reg_path.exists():
                    continue
                reg_data = load_yaml(reg_path)
                for field in fields:
                    val = get_registry_value(reg_data, src["yaml_path"], module_id)
                    key = f"{source_label}:{field}"
                    if val is not None:
                        values[key] = val
            elif src.get("source") == "physical_blueprint":
                for field in fields:
                    val = get_physical_value(module_path, src.get("frontmatter_key", field))
                    key = f"physical:{field}"
                    if val is not None:
                        values[key] = val
        unique_values = set(values.values())
        if len(unique_values) > 1:
            ssoT_value = None
            if ssoT_source == "REG-001":
                for field in fields:
                    val = get_registry_value(
                        load_yaml(REPO_ROOT / next(r for r in ror["registries"] if r["id"] == "REG-001")["path"]),
                        "modules[].blueprint.status"
                        if field == "status"
                        else "modules[].priority"
                        if field == "priority"
                        else f"modules[].{field}",
                        module_id,
                    )
                    if val:
                        ssoT_value = val
            elif ssoT_source == "physical_blueprint":
                for field in fields:
                    val = get_physical_value(module_path, field)
                    if val:
                        ssoT_value = val
            detail_lines = []
            for key, val in sorted(values.items()):
                marker = " ← SSoT" if ssoT_value and val == ssoT_value else ""
                detail_lines.append(f"  {key} = {val}{marker}")
            evidence = "不一致的值:\n" + "\n".join(detail_lines)
            fj = "/".join(fields)
            description = f"[{rule_id}] {module_id} 的 {fj} 字段跨表不一致"
            severity = Severity.CRITICAL if rule.get("violation_action") == "block" else Severity.HIGH
            blast = BlastRadius.MODULE
            f = Finding(
                dimension=Dimension.D3,
                severity=severity,
                category=f"跨登记表一致性 — {rule_id}",
                target_file=f"docs/{module_path}/blueprint.md",
                description=description,
                evidence=evidence,
                blast_radius=blast,
                remediation_action=RemediationAction.FIX,
                remediation_priority="P0" if severity == Severity.CRITICAL else "P1",
            )
            collection.add(f)
    return collection


# ═══════════════════════════════════════════════════════════════════════════════
# CR-007 · ROOR entry_count 实测对账与回填（2026-09-06 Owner 批"账本数字自动回填"）
#
# 病灶：ROOR entry_count 手工维护，registry 增减后数字漂移无人发现
#   （2026-09-06 实测 13 表漂移：SCRIPT-001 483→755、INV-001 24434→31962、
#    FREEZE-001 15→38、KB-001 4→0 等）。
# 治理：显式口径登记（ENTRY_SPECS / ENTRY_MANUAL）→ CI 对账（漂移即 FAIL）
#   → --update-entry-counts 行级手术回填（保注释保格式）。
# 新增登记表时必须同步补 ENTRY_SPECS（可自动数）或 ENTRY_MANUAL（不可自动数+原因），
# 否则 CR-007 报 UNSPECIFIED 阻断——这是防"新表无口径静默漂移"的强制闭环。
# ═══════════════════════════════════════════════════════════════════════════════

ROOR_PATH = REPO_ROOT / "docs" / "registry_of_registries.yaml"

# 口径元组：(kind, key, counting_rule 文本)
# kind ∈ yaml_list（顶层数组条目数）/ yaml_field（顶层整数字段值）/
#         yaml_sum（多点位求和，key 用 + 连接，段内 . 寻址）/
#         yaml_dict_len（顶层 dict 键数）/ glob（目录内文件数，key=pattern）
ENTRY_SPECS: dict[str, tuple[str, str, str]] = {
    # ── tier 1 治理与流程级 ──
    "REG-GATE-001": ("yaml_list", "gates", "gates 数组条目数"),
    "REG-SCRIPT-001": ("yaml_list", "scripts", "scripts 数组条目数（generate_manifest.py 全树再生）"),
    "REG-SCRIPT-002": ("yaml_list", "scripts", "scripts 数组条目数（governance 子集，__manifest__ 块提取）"),
    "REG-PIPE-001": ("yaml_list", "routes", "routes 数组条目数"),
    "REG-CAP-001": ("yaml_list", "decisions", "decisions 数组条目数"),
    "REG-EMBED-001": ("yaml_list", "models", "models 数组条目数"),
    "REG-DRIFT-001": (
        "yaml_sum",
        "detectors.existing+detectors.new",
        "detectors.existing + detectors.new 条目数合计",
    ),
    "REG-SKILL-001": ("glob", "skill_*.yaml", "skill_*.yaml 文件数（data/capability_cards/）"),
    "REG-AFX-PATTERN-001": ("yaml_list", "patterns", "patterns 数组条目数"),
    "REG-CATALOG-001": ("yaml_list", "registries", "registries 数组条目数"),
    "REG-STD-001": ("yaml_list", "aliases", "aliases 数组条目数"),
    "REG-STD-002": ("yaml_list", "aliases", "aliases 数组条目数"),
    "REG-STD-004": ("yaml_list", "aliases", "aliases 数组条目数"),
    "REG-CROSS-001": ("yaml_list", "registries", "registries 数组条目数"),
    "REG-CROSS-002": ("yaml_list", "dependencies", "dependencies 数组条目数"),
    "REG-DIR-001": ("yaml_list", "directories", "directories 数组条目数"),
    "REG-DOC-001": ("yaml_list", "files", "files 数组条目数（rule catalog 文件级）"),
    "REG-GATE-CAT-001": ("yaml_list", "gates", "gates 数组条目数"),
    "REG-INFRA-001": ("yaml_list", "infrastructure", "infrastructure 数组条目数"),
    "REG-INTF-001": ("yaml_list", "interfaces", "interfaces 数组条目数"),
    "REG-KB-001": ("yaml_list", "knowledge_entries", "knowledge_entries 数组条目数（模板就位内容待填充）"),
    "REG-TASK-META-001": ("yaml_dict_len", "systems", "systems 子系统数"),
    "REG-FRONTMATTER-001": ("yaml_list", "fields", "fields 数组条目数"),
    "REG-FUNC-DOMAIN-001": ("yaml_list", "entries", "entries 数组条目数"),
    "REG-MIGRATION-001": ("yaml_list", "entries", "entries 数组条目数"),
    "REG-ARCH-ISSUE-001": ("yaml_list", "entries", "entries 数组条目数（含 deprecated 全量）"),
    "REG-CAPCAN-001": ("yaml_list", "capabilities", "capabilities 数组条目数"),
    "REG-GEN-001": ("yaml_list", "creation_tokens", "creation_tokens 数组条目数"),
    # ── tier 2 数据与运行时级 ──
    "REG-ERRCODE-001": ("yaml_list", "error_codes", "error_codes 条目数"),
    "REG-INV-001": ("yaml_field", "total_assets", "total_assets 字段值（generate_asset_index.py 再生）"),
    "REG-TEMPLATE-001": ("yaml_list", "templates", "templates 数组条目数"),
    "REG-PATHWAY-001": ("yaml_list", "pathways", "pathways 数组条目数"),
    "REG-MOD-ID-001": ("yaml_list", "registered_ids", "registered_ids 数组条目数"),
    "REG-ARCH-001": ("yaml_list", "domains", "domains 数组条目数"),
    "REG-CACHE-001": ("yaml_list", "entries", "entries 数组条目数"),
    "REG-FREEZE-001": (
        "yaml_sum",
        "p0_critical_contracts+cross_cutting_contracts+backpressure_contracts"
        "+p1_blueprint_contracts+extension_contracts+external_contracts",
        "六组 *_contracts 数组条目数合计（已冻结跨层契约全量）",
    ),
    "REG-RB-001": ("yaml_list", "scenarios", "scenarios 数组条目数"),
    "REG-RB-002": ("yaml_list", "articles", "articles 数组条目数"),
    "REG-SM-001": ("yaml_list", "state_machines", "state_machines 数组条目数"),
    # ── tier 3 业务领域级 ──
    "REG-UNI-001": ("yaml_list", "universes", "universes 数组条目数"),
    "REG-BMK-001": ("yaml_list", "benchmarks", "benchmarks 数组条目数"),
    "REG-CST-001": ("yaml_list", "cost_models", "cost_models 数组条目数"),
    "REG-FCT-001": ("yaml_list", "factors", "factors 数组条目数"),
    "REG-STR-001": ("yaml_list", "strategies", "strategies 数组条目数"),
    "REG-RLM-001": ("yaml_list", "risk_limits", "risk_limits 数组条目数"),
    "REG-TECHNICAL-INDICATOR-001": ("yaml_list", "indicators", "indicators 数组条目数"),
    "REG-PAT-001": ("yaml_list", "chart_patterns", "chart_patterns 数组条目数"),
    "REG-EXA-001": ("yaml_list", "execution_algos", "execution_algos 数组条目数"),
    "REG-DATAFLOW-001": ("yaml_list", "datasets", "datasets 数组条目数（含 deprecated 全量）"),
    "REG-FLD-001": ("yaml_list", "fields", "fields 数组条目数"),
    "REG-EXP-001": ("yaml_list", "experiments", "experiments 数组条目数"),
    "REG-SEAT-001": ("yaml_list", "seats", "seats 数组条目数"),
    "REG-CYCLE-001": ("yaml_list", "cycles", "cycles 数组条目数"),
    "REG-ML-001": ("yaml_list", "models", "models 数组条目数"),
    "REG-EVT-001": ("yaml_list", "event_types", "event_types 数组条目数"),
    "REG-MAC-001": ("yaml_list", "indicators", "indicators 数组条目数"),
    "REG-PFM-001": ("yaml_list", "portfolio_models", "portfolio_models 数组条目数"),
    "REG-FEATURE-ADJ-001": ("yaml_list", "features", "features 数组条目数"),
    "REG-CMP-REPORT-001": ("yaml_list", "report_items", "report_items 数组条目数"),
    "REG-ATH-001": ("yaml_list", "thresholds", "thresholds 数组条目数"),
}

# 不可自动数的表（原因显式登记；改口径需同步本表）
ENTRY_MANUAL: dict[str, str] = {
    "REG-MOD-ALPHA_SIGNAL_DOMAIN": "retired（module_registry.yaml 已退库，commit 2145eb3688）",
    "REG-DOMAIN-GOV-001": "markdown frontmatter 口径",
    "REG-AFX-FIXER-001": "code_inline（engine.py fixer_map 字典）",
    "REG-STD-003": "markdown 口径（quality_standard.md）",
    "REG-STD-005": "语义口径（Session 状态机 3 禁止转换，见 trae_048 sections）",
    "REG-STD-006": "语义口径（门禁检查项 A1-D2 共 12 项，2026-09-06 裁定）",
    "REG-STD-007": "语义口径（事故响应分级 P0/P1/P2 共 3 级）",
    "REG-STD-008": "语义口径（导航入口文件数 4）",
    "REG-ARCH-PANORAMA-001": "postgresql 表（需 DB 凭据，离线不可数）",
    "REG-DEPGRAPH-001": "postgresql 表（需 DB 凭据，离线不可数）",
    "REG-BLUEPRINT-001": "派生退库（03df6215e8），sync_registry_from_blueprints.py 运行时再生，离线不可数",
    "REG-SYS-MASTER-001": "markdown 单体蓝图（恒 1）",
    "REG-MOD-MASTER_BLUEPRINT": "markdown 单体蓝图（恒 1）",
}


def _walk_roor(node: Any) -> Iterator[dict]:
    """深度遍历 registry_of_registries.yaml，产出全部登记表 dict（跨 tier 嵌套）。"""
    if isinstance(node, dict):
        if isinstance(node.get("registries"), list):
            yield from node["registries"]
        for value in node.values():
            yield from _walk_roor(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_roor(item)


def _actual_entry_count(spec: tuple[str, str, str], physical_path: str) -> int | None:
    """按口径元组实测一个登记表的条目数；物理文件不可读返回 None。"""
    kind, key, _rule = spec
    path = Path(physical_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if kind == "glob":
        return sum(1 for _ in path.glob(key)) if path.is_dir() else None
    if not path.is_file():
        return None
    try:
        data = load_yaml(path)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    if kind == "yaml_list":
        value = data.get(key)
        return len(value) if isinstance(value, list) else None
    if kind == "yaml_field":
        return data.get(key) if isinstance(data.get(key), int) else None
    if kind == "yaml_dict_len":
        value = data.get(key)
        return len(value) if isinstance(value, dict) else None
    if kind == "yaml_sum":
        total = 0
        for part in key.split("+"):
            current: Any = data
            for segment in part.strip().split("."):
                if isinstance(current, dict):
                    current = current.get(segment)
                else:
                    return None
            if not isinstance(current, list):
                return None
            total += len(current)
        return total
    return None


def verify_entry_counts(roor_path: Path = ROOR_PATH) -> list[dict] | None:
    """CR-007 对账：返回逐表结果行（含 verdict），ROOR 不存在返回 None。

    verdict ∈ MATCH / STALE / MANUAL / MISSING / UNSPECIFIED / NO_COUNT；
    其中 STALE / MISSING / UNSPECIFIED 视为问题（FAIL），MANUAL / NO_COUNT 仅留痕。
    """
    if not roor_path.exists():
        return None
    ror = load_yaml(roor_path)
    rows: list[dict] = []
    for reg in _walk_roor(ror):
        rid = reg.get("registry_id") or reg.get("id")
        if not rid:
            continue
        expected = reg.get("entry_count")
        physical_path = reg.get("physical_path") or ""
        if rid in ENTRY_MANUAL:
            rows.append(
                {"rid": rid, "verdict": "MANUAL", "expected": expected, "actual": None, "note": ENTRY_MANUAL[rid]}
            )
            continue
        spec = ENTRY_SPECS.get(rid)
        if spec is None:
            rows.append(
                {
                    "rid": rid,
                    "verdict": "UNSPECIFIED",
                    "expected": expected,
                    "actual": None,
                    "note": "未登记计数口径——新表必须补 ENTRY_SPECS/ENTRY_MANUAL",
                    "path": physical_path,
                }
            )
            continue
        if expected is None:
            rows.append(
                {"rid": rid, "verdict": "NO_COUNT", "expected": None, "actual": None, "note": "ROOR 无 entry_count 字段"}
            )
            continue
        actual = _actual_entry_count(spec, physical_path)
        if actual is None:
            rows.append(
                {
                    "rid": rid,
                    "verdict": "MISSING",
                    "expected": expected,
                    "actual": None,
                    "note": f"物理文件不可读/不存在: {physical_path}",
                    "path": physical_path,
                }
            )
            continue
        verdict = "MATCH" if (isinstance(expected, int) and expected == actual) else "STALE"
        rows.append(
            {"rid": rid, "verdict": verdict, "expected": expected, "actual": actual, "note": spec[2], "path": physical_path}
        )
    return rows


def apply_roor_entry_count_updates(rows: list[dict], roor_path: Path = ROOR_PATH) -> list[str]:
    """CR-007 回填：对 STALE 行做行级手术更新（保注释保格式）。

    仅替换 entry_count 数字；该表块内缺 counting_rule 时按口径补插一行。
    返回更新描述列表（供打印/提交留痕）。
    """
    fixes = {r["rid"]: r for r in rows if r["verdict"] == "STALE"}
    if not fixes:
        return []
    rule_texts = {rid: ENTRY_SPECS[rid][2] for rid in fixes if rid in ENTRY_SPECS}
    text = roor_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    rid_re = re.compile(r"^\s*-\s*registry_id:\s*(\S+)\s*$")
    ec_re = re.compile(r"^(\s*)entry_count:\s*(\d+)(.*)$")  # 尾注释（含 inline #）保留于 group(3)
    cr_re = re.compile(r"^\s*counting_rule:")
    updates: list[str] = []
    current_rid: str | None = None
    entry_idx: int | None = None
    has_rule = False
    insertions: dict[int, str] = {}  # line_idx -> 待插行（entry_count 行后）

    def _flush() -> None:
        nonlocal current_rid, entry_idx, has_rule
        if current_rid in fixes and entry_idx is not None:
            actual = fixes[current_rid]["actual"]
            m = ec_re.match(lines[entry_idx])
            lines[entry_idx] = f"{m.group(1)}entry_count: {actual}{m.group(3)}"
            note = f"{current_rid}: {fixes[current_rid]['expected']} -> {actual}"
            if current_rid in rule_texts and not has_rule:
                insertions[entry_idx] = f"{m.group(1)}counting_rule: {rule_texts[current_rid]}"
                note += "（补 counting_rule）"
            updates.append(note)
        current_rid, entry_idx, has_rule = None, None, False

    for idx, line in enumerate(lines):
        m = rid_re.match(line)
        if m:
            _flush()
            current_rid = m.group(1)
            continue
        if current_rid is None:
            continue
        if ec_re.match(line) and entry_idx is None:
            entry_idx = idx
        elif cr_re.match(line):
            has_rule = True
    _flush()

    if insertions:
        for idx in sorted(insertions, reverse=True):
            lines.insert(idx + 1, insertions[idx])
    roor_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return updates


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="跨登记表一致性校验脚本")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻塞流程）")
    parser.add_argument(
        "--update-entry-counts",
        action="store_true",
        help="CR-007：把实测条目数回填 ROOR（行级手术保注释；仅 STALE 行）",
    )
    args = parser.parse_args()
    if not ROR_PATH.exists():
        print(f"[SKIP] registry_consistency_contract.yaml 不存在: {ROR_PATH}", file=sys.stderr)
        sys.exit(EXIT_PASS)
    ror = load_yaml(ROR_PATH)
    rules = ror.get("cross_registry_rules", [])
    if not rules:
        print("[OK] 无跨表一致性规则定义", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if not FINDING_AVAILABLE:
        print("[SKIP] Finding 模块不可用，跳过结构化输出", file=sys.stderr)
        sys.exit(EXIT_PASS)
    all_findings = FindingCollection()
    for rule in rules:
        rule_id = rule.get("rule_id", "?")
        findings = check_rule(ror, rule)
        all_findings.extend(findings.findings)
        status = "PASS" if findings.total == 0 else f"FAIL ({findings.total} 项)"
        rtitle = rule.get("title", "?")
        print(f"  {rule_id}: {rtitle} ... {status}", file=sys.stderr)

    # CR-007：ROOR entry_count 实测对账（--update-entry-counts 先回填再对账）
    entry_problems = 0
    entry_rows = verify_entry_counts()
    if entry_rows is None:
        print("  CR-007: entry_count 实测对账 ... SKIP（ROOR 不存在）", file=sys.stderr)
    else:
        if args.update_entry_counts:
            updates = apply_roor_entry_count_updates(entry_rows)
            for u in updates:
                print(f"    [FIXED] {u}", file=sys.stderr)
            if updates:
                entry_rows = verify_entry_counts()  # 回填后复验
        for row in entry_rows:
            verdict = row["verdict"]
            if verdict == "MATCH":
                continue
            if verdict == "STALE":
                entry_problems += 1
                print(
                    f"    STALE: {row['rid']} ROOR={row['expected']} 实测={row['actual']}（{row['note']}）",
                    file=sys.stderr,
                )
                if FINDING_AVAILABLE:
                    all_findings.add(
                        Finding(
                            dimension=Dimension.D3,
                            severity=Severity.HIGH,
                            category="跨登记表一致性 — CR-007",
                            target_file=row.get("path") or "docs/registry_of_registries.yaml",
                            description=f"[CR-007] {row['rid']} entry_count 漂移: ROOR={row['expected']} 实测={row['actual']}",
                            evidence=f"counting_rule: {row['note']}",
                            blast_radius=BlastRadius.MODULE,
                            remediation_action=RemediationAction.FIX,
                            remediation_priority="P1",
                        )
                    )
            elif verdict in ("MISSING", "UNSPECIFIED"):
                entry_problems += 1
                print(f"    {verdict}: {row['rid']} {row['note']}", file=sys.stderr)
        status = "PASS" if entry_problems == 0 else f"FAIL ({entry_problems} 项)"
        print(f"  CR-007: entry_count 实测对账（ROOR）... {status}", file=sys.stderr)

    total = all_findings.total
    if total == 0:
        print("\n[OK] 所有跨登记表一致性规则通过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    else:
        print(f"\n[FAIL] {total} 项跨表不一致", file=sys.stderr)
        for f in all_findings.critical_only().findings:
            print(f"  CRITICAL: {f.description}", file=sys.stderr)
            print(f"    {f.evidence}", file=sys.stderr)
        output_path = REPO_ROOT / "scripts" / "governance" / "reports" / "findings.jsonl"
        all_findings.append_jsonl(str(output_path))
        print(f"\n报告已追加: {output_path}", file=sys.stderr)
        if args.warn_only:
            sys.exit(EXIT_PASS)
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
