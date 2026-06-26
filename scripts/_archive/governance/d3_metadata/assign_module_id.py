# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/assign_module_id.py | §
"""assign_module_id.py — 模块 ID 唯一性校验（INJ-001）

对标：GOV-MOD-ALPHA_SIGNAL_DOMAIN INJ-001（ID 唯一性）

检测内容：
- --check: 检查指定 module_id 是否在项目中唯一
- --assign: 为新文件分配下一个可用的 module_id（仅输出建议，不自动写入）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --check, type: str, description: "检查指定 module_id 的唯一性"}
- {flag: --assign, type: str, description: "为新文件建议下一个可用 module_id（格式: DOMAIN-TYPE）"}
description: >
  模块 ID 唯一性校验（INJ-001）——检查 module_id 全局唯一性。
  对标 GOV-MOD-ALPHA_SIGNAL_DOMAIN module-injection-rules-policy.md。
dimensions:
- D3
priority: P1
timeout_seconds: 15
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file

ensure_utf8_stdout()

POLICIES_ROOT = REPO_ROOT / "docs" / "01_policies_and_standards"
MODULES_ROOT = REPO_ROOT / "docs" / "03_modules"


def collect_all_module_ids() -> dict[str, list[Path]]:
    """collect_all_module_ids implementation."""
    id_map: dict[str, list[Path]] = {}
    for root in [POLICIES_ROOT, MODULES_ROOT]:
        for f in root.rglob("*"):
            if f.suffix not in (".md", ".yaml", ".yml"):
                continue
            fm = parse_frontmatter_from_file(f)
            if fm and fm.get("module_id"):
                mid = fm["module_id"]
                id_map.setdefault(mid, []).append(f)
    return id_map


def check_uniqueness(module_id: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    id_map = collect_all_module_ids()
    if module_id not in id_map:
        findings.append(f"INJ-001 WARNING: module_id '{module_id}' not found in any file")
        return findings
    if len(id_map[module_id]) > 1:
        locations = ", ".join(str(p.relative_to(REPO_ROOT)) for p in id_map[module_id])
        findings.append(
            f"INJ-001 FAIL: module_id '{module_id}' is not unique — found in {len(id_map[module_id])} files: {locations}"
        )
    return findings


def check_ast_registry_match(module_id: str = None) -> list[str]:
    """Check compliance and report findings."""
    import ast as ast_mod

    findings = []
    id_map = collect_all_module_ids()
    registry_ids = set(id_map.keys())
    src_root = REPO_ROOT / "src" / "zephyr"
    for py_file in src_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast_mod.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast_mod.walk(tree):
            if isinstance(node, ast_mod.ClassDef):
                for base in node.bases:
                    base_str = ast_mod.dump(base)
                    if "BaseModel" in base_str or "Schema" in base_str:
                        class_id = f"{py_file.stem}::{node.name}"
                        if class_id not in registry_ids and module_id is None:
                            pass
            if isinstance(node, ast_mod.Call):
                func_str = ast_mod.dump(node.func)
                if "register" in func_str or "declare" in func_str:
                    for arg in node.args:
                        if isinstance(arg, ast_mod.Constant) and isinstance(arg.value, str):
                            if arg.value.startswith(("GOV-", "PS-", "OPS-", "MOD-", "META-")):
                                if arg.value not in registry_ids:
                                    rel = py_file.relative_to(REPO_ROOT)
                                    findings.append(
                                        f"HC-1 WARNING: {rel} references module_id '{arg.value}' not found in any registry file"
                                    )
    return findings


def suggest_next_id(domain_type: str) -> str:
    """suggest_next_id implementation."""
    id_map = collect_all_module_ids()
    pattern = re.compile(rf"^{re.escape(domain_type)}-(\d{{3}})$")
    max_num = 0
    for mid in id_map:
        m = pattern.match(mid)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"{domain_type}-{max_num + 1:03d}"


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Module ID uniqueness check (INJ-001)")
    parser.add_argument("--check", type=str, help="Check uniqueness of a specific module_id")
    parser.add_argument("--assign", type=str, help="Suggest next available module_id for DOMAIN-TYPE prefix")
    parser.add_argument("--scan-all", action="store_true", help="Scan all module_ids for duplicates")
    parser.add_argument(
        "--check-ast", action="store_true", help="Check AST code for unregistered module_id references (HC-1)"
    )
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.check:
        all_findings.extend(check_uniqueness(args.check))

    if args.assign:
        suggestion = suggest_next_id(args.assign)
        print(f"INJ-001 SUGGEST: next available module_id for '{args.assign}' = '{suggestion}'")

    if args.scan_all:
        id_map = collect_all_module_ids()
        for mid, paths in id_map.items():
            if len(paths) > 1:
                locations = ", ".join(str(p.relative_to(REPO_ROOT)) for p in paths)
                all_findings.append(f"INJ-001 FAIL: module_id '{mid}' duplicated in {len(paths)} files: {locations}")

    if args.check_ast:
        all_findings.extend(check_ast_registry_match(args.check))

    if not any([args.check, args.assign, args.scan_all, args.check_ast]):
        print("Usage: assign_module_id.py --check <module_id> | --assign <DOMAIN-TYPE> | --scan-all")
        sys.exit(EXIT_ERROR)

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
