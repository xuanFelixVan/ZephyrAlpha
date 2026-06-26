# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] scripts.governance.validate_module_id_naming
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] phase_manager.py; CI pipeline; AI session 冷启动
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] module_id 必须符合 PS-STD-001 §5 命名规范; 禁止嵌套编号
# [MODIFY-GUARD] PS-STD-001 §5; PS-REG-012 frontmatter_field_registry.yaml; module_id_registry.yaml
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=CLEAN, exit 1=VIOLATION
# [TESTS] tests/governance/test_validate_module_id_naming.py

r"""
module_id 命名合规性校验门禁

规则来源: PS-STD-001 §5 编号分配铁律
校验内容:
  1. 格式合规: module_id 必须匹配 ^[A-Z]+(-[A-Z]+)?(-[A-Z]+\d*)?-\d{3,4}$
  2. 禁止嵌套编号: 不得出现 XXX-NNN-SUFFIX 模式（如 MOD-MASTER_BLUEPRINT-BASELINE）
  3. 父子关系靠字段: parent_module / belongs_to 表达，不靠编号后缀

用法:
  python scripts/governance/validate_module_id_naming.py [--warn-only] [--blueprint-dir DIR]
"""

import argparse
import re
import sys
from pathlib import Path

VALID_MODULE_ID_PATTERN = re.compile(r"^[A-Z]+(-[A-Z]+)?(-[A-Z]+\d*)?-\d{3,4}$")

NESTED_ID_PATTERN = re.compile(r"^([A-Z]+(-[A-Z]+)?(-[A-Z]+\d*)?-\d{3,4})-[A-Z]")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def extract_frontmatter_field(text: str, field: str) -> str | None:
    in_fm = False
    for i, line in enumerate(text.splitlines()):
        stripped = line.strip().lstrip("\ufeff")
        if i == 0 and stripped == "---":
            in_fm = True
            continue
        if in_fm and stripped == "---":
            break
        if in_fm:
            m = re.match(rf"{field}:\s*(.+)", stripped)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return None


def validate_blueprint(filepath: Path, warn_only: bool = False) -> list[dict]:
    violations = []
    try:
        text = filepath.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return violations

    module_id = extract_frontmatter_field(text, "module_id")
    if not module_id:
        return violations

    if not VALID_MODULE_ID_PATTERN.match(module_id):
        violations.append(
            {
                "file": str(filepath.relative_to(PROJECT_ROOT)),
                "module_id": module_id,
                "violation": "FORMAT_INVALID",
                "message": f"module_id '{module_id}' does not match pattern {VALID_MODULE_ID_PATTERN.pattern}",
            }
        )

    nested_match = NESTED_ID_PATTERN.match(module_id)
    if nested_match:
        parent_id = nested_match.group(1)
        violations.append(
            {
                "file": str(filepath.relative_to(PROJECT_ROOT)),
                "module_id": module_id,
                "violation": "NESTED_ID",
                "message": f"module_id '{module_id}' uses nested numbering (parent={parent_id}). "
                f"Use independent numbering + parent_module field instead. "
                f"See PS-STD-001 §5.4 rule #7.",
            }
        )

    return violations


def main():
    parser = argparse.ArgumentParser(description="Validate module_id naming compliance")
    parser.add_argument("--warn-only", action="store_true", help="Print warnings but exit 0")
    parser.add_argument("--blueprint-dir", default="docs/03_modules", help="Blueprint directory")
    args = parser.parse_args()

    blueprint_dir = PROJECT_ROOT / args.blueprint_dir
    all_violations = []

    for bp_file in sorted(blueprint_dir.rglob("blueprint*.md")):
        violations = validate_blueprint(bp_file, args.warn_only)
        all_violations.extend(violations)

    if not all_violations:
        print("[CLEAN] All module_ids comply with PS-STD-001 §5 naming rules.")
        return 0

    print(f"[VIOLATION] {len(all_violations)} module_id naming violation(s) found:\n")
    for v in all_violations:
        severity = "WARN" if args.warn_only else "FAIL"
        print(f"  [{severity}] {v['violation']}: {v['file']}")
        print(f"         module_id={v['module_id']}")
        print(f"         {v['message']}\n")

    if args.warn_only:
        print(f"[WARN-ONLY] {len(all_violations)} violation(s) detected but not blocking.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
