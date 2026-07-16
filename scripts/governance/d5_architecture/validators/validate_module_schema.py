# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_module_schema.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_module_schema
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
"""validate_module_schema.py — 模块 Schema 校验（INJ-003/004/005/006）

对标：GOV-MOD-ALPHA_SIGNAL_DOMAIN INJ-003（契约已定义）、INJ-004（生命周期状态合法）、
     INJ-005（运行平面已分配）、INJ-006（KB 决策记录已关联）

检测内容：
- --check-contracts: 模块是否定义了接口契约（cross_layer_contracts.yaml 或 contracts/ 目录）
- --check-field: 模块 frontmatter 指定字段值是否在合法枚举内
- --check-adr: 模块是否关联了 KB 决策记录

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --check-contracts, type: str, description: "检查指定 module_id 的契约定义"}
- {flag: --check-field, type: str, description: "检查指定字段名"}
- {flag: --valid-values, type: str, description: "合法值列表（逗号分隔）"}
- {flag: --check-adr, type: str, description: "检查指定 module_id 的 KB 决策记录关联"}
description: >
  模块 Schema 校验（INJ-003/004/005/006）——契约定义、字段枚举、KB 决策记录关联。
  对标 GOV-MOD-ALPHA_SIGNAL_DOMAIN module-injection-rules-policy.md。
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file

ensure_utf8_stdout()

POLICIES_ROOT = REPO_ROOT / "docs" / "01_policies_and_standards"
MODULES_ROOT = REPO_ROOT / "docs" / "03_modules"
CONTRACTS_DIR = REPO_ROOT / "src" / "zephyr" / "shared" / "contracts"


def find_module_file(module_id: str) -> Path | None:
    """find_module_file implementation."""
    for root in [POLICIES_ROOT, MODULES_ROOT]:
        for f in root.rglob("*"):
            if f.suffix not in (".md", ".yaml", ".yml"):
                continue
            fm = parse_frontmatter_from_file(f)
            if fm and fm.get("module_id") == module_id:
                return f
    return None


def check_contracts(module_id: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    contracts_yaml = CONTRACTS_DIR / "cross_layer_contracts.yaml"
    has_contract = False
    if contracts_yaml.exists():
        import yaml

        data = yaml.safe_load(contracts_yaml.read_text(encoding="utf-8")) or {}
        for entry in data.get("contracts", []):
            if entry.get("provider") == module_id or entry.get("consumer") == module_id:
                has_contract = True
                break
    module_dir = MODULES_ROOT
    for d in module_dir.rglob("*"):
        if d.is_dir() and d.name == "contracts":
            parent_fm_path = d.parent / "blueprint.md"
            if parent_fm_path.exists():
                fm = parse_frontmatter_from_file(parent_fm_path)
                if fm and fm.get("module_id") == module_id:
                    has_contract = True
                    break
    if not has_contract:
        findings.append(
            f"INJ-003 FAIL: module '{module_id}' has no interface contract defined in cross_layer_contracts.yaml or contracts/ directory"
        )
    return findings


def check_field(module_id: str, field: str, valid_values: list[str]) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    fpath = find_module_file(module_id)
    if not fpath:
        findings.append(f"INJ-004/005 FAIL: module '{module_id}' not found in project")
        return findings
    fm = parse_frontmatter_from_file(fpath)
    if not fm:
        findings.append(f"INJ-004/005 FAIL: module '{module_id}' has no parseable frontmatter in {fpath}")
        return findings
    value = fm.get(field)
    if value is None:
        findings.append(f"INJ-004/005 FAIL: module '{module_id}' missing required field '{field}'")
        return findings
    if valid_values and str(value) not in valid_values:
        findings.append(
            f"INJ-004/005 FAIL: module '{module_id}' field '{field}' value '{value}' not in valid values {valid_values}"
        )
    return findings


def check_adr(module_id: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    fpath = find_module_file(module_id)
    if not fpath:
        findings.append(f"INJ-006 FAIL: module '{module_id}' not found in project")
        return findings
    fm = parse_frontmatter_from_file(fpath)
    if not fm:
        findings.append(f"INJ-006 FAIL: module '{module_id}' has no parseable frontmatter")
        return findings
    adr_refs = fm.get("kb_refs") or fm.get("adr_refs") or fm.get("decisions") or fm.get("related_adrs")
    if not adr_refs:
        content = fpath.read_text(encoding="utf-8", errors="replace").lower()
        if "adr-" not in content and "decision" not in content and "kb:decisions" not in content:
            findings.append(
                f"INJ-006 WARNING: module '{module_id}' has no KB decision record association (frontmatter kb_refs/adr_refs/decisions or in-content ADR/KB reference)"
            )
    return findings


def check_config_registry(module_id: str = None) -> list[str]:
    """Check compliance and report findings."""
    import yaml

    findings = []
    config_yaml = (
        REPO_ROOT
        / "architecture_model"
        / "system-configuration.yaml"
    )
    if not config_yaml.exists():
        return findings
    with open(config_yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    registered_keys = set()
    for section in data.get("configuration", []):
        if isinstance(section, dict):
            registered_keys.add(section.get("key", ""))
            for item in section.get("items", []):
                if isinstance(item, dict):
                    registered_keys.add(item.get("key", ""))
    src_root = REPO_ROOT / "src" / "zephyr"
    for py_file in src_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        import re

        config_refs = re.findall(r'config\["([^"]+)"\]|os\.environ\.get\("([^"]+)"\)|os\.getenv\("([^"]+)"\)', source)
        for groups in config_refs:
            key = next((g for g in groups if g), None)
            if (
                key
                and registered_keys
                and key not in registered_keys
                and not key.startswith(("ZEPHYR_", "PYTHON", "PATH"))
            ):
                rel = py_file.relative_to(REPO_ROOT)
                findings.append(
                    f"HC-5 WARNING: {rel} references config key '{key}' not found in system-configuration.yaml"
                )
    return findings


def check_invariants(module_id: str = None) -> list[str]:
    """Check compliance and report findings."""
    import re as re_mod

    findings = []
    contracts_yaml = CONTRACTS_DIR / "cross_layer_contracts.yaml"
    if not contracts_yaml.exists():
        return findings
    import yaml

    with open(contracts_yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    invariant_markers = []
    for contract in data.get("contracts", []):
        if contract.get("status") == "frozen":
            invariant_markers.append(contract.get("provider", ""))
    src_root = REPO_ROOT / "src" / "zephyr"
    for py_file in src_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for marker in invariant_markers:
            pattern = re_mod.compile(rf"{re_mod.escape(marker)}.*?(?:bypass|override|skip|ignore)", re_mod.IGNORECASE)
            matches = pattern.findall(source)
            if matches:
                rel = py_file.relative_to(REPO_ROOT)
                findings.append(f"HC-6 FAIL: {rel} attempts to bypass/override frozen contract '{marker}'")
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Module schema validation (INJ-003/004/005/006)")
    parser.add_argument("--check-contracts", type=str, help="Check contract definition for module_id")
    parser.add_argument("--check-field", type=str, help="Field name to validate")
    parser.add_argument("--valid-values", type=str, help="Comma-separated valid values")
    parser.add_argument("--check-adr", type=str, help="Check KB decision record association for module_id")
    parser.add_argument(
        "--check-config-registry",
        action="store_true",
        help="Check config keys against system-configuration.yaml (HC-5)",
    )
    parser.add_argument(
        "--check-invariants", action="store_true", help="Check for frozen contract bypass attempts (HC-6)"
    )
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.check_contracts:
        all_findings.extend(check_contracts(args.check_contracts))

    if args.check_field:
        valid = [v.strip() for v in args.valid_values.split(",")] if args.valid_values else []
        module_id = args.check_field if not args.check_contracts else args.check_contracts
        all_findings.extend(check_field(module_id, args.check_field, valid))

    if args.check_adr:
        all_findings.extend(check_adr(args.check_adr))

    if args.check_config_registry:
        all_findings.extend(check_config_registry(args.check_contracts))

    if args.check_invariants:
        all_findings.extend(check_invariants(args.check_contracts))

    if not any(
        [args.check_contracts, args.check_field, args.check_adr, args.check_config_registry, args.check_invariants]
    ):
        for f in POLICIES_ROOT.rglob("*.md"):
            fm = parse_frontmatter_from_file(f)
            if fm and fm.get("module_id"):
                mid = fm["module_id"]
                all_findings.extend(check_contracts(mid))
                all_findings.extend(check_adr(mid))

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
