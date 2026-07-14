# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_registry_consistency.py | §
# [MODULE] scripts.governance.d3_metadata.check_registry_consistency
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
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
# [TTL] task_bound
"""check_registry_consistency — 跨登记表一致性校验。

读取 registry_consistency_contract.yaml，按 cross_registry_rules 比对多登记表共享字段。
可将 Finding 写入 scripts/governance/reports/findings.jsonl。
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
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
try:
    from zephyr.infrastructure.finding import (
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
ROR_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry_consistency_contract.yaml"
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
                    if reg_info2:
                        reg_path2 = REPO_ROOT / reg_info2["path"]
                        if reg_path2.exists():
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
                        if reg_info2:
                            reg_data2 = load_yaml(REPO_ROOT / reg_info2["path"])
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


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="跨登记表一致性校验脚本")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻塞流程）")
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
