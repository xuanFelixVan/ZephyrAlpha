# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_architecture.py | §
# [MODULE] scripts.governance.d3_metadata.validate_architecture
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
# [TTL] permanent
"""
validate_architecture.py - Validate rule files against architecture_contract.yaml
Reads architecture_contract.yaml and validates all .md/.yaml files under
docs/01_policies_and_standards/ for directory compliance, frontmatter fields,
and doc_type / rule_form consistency.

向内收原则（P7-FIX）：VR 校验逻辑从 architecture_contract.yaml 的 machine_check
结构化字段动态读取执行，禁止在脚本里硬编码 VR 逻辑（否则变成第二个真源）。
脚本只实现通用的 machine_check 执行引擎，不"知道"任何具体 VR 编号。
"""

from __future__ import annotations

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

__manifest__ = """
args:
- --ci
- --warn-only
description: GATE-16 Architecture compliance check (VR machine_check engine — reads architecture_contract.yaml validation_rules[].machine_check and executes generically)
dimensions:
- D3
- D4
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

# 扫描根目录：与 architecture_contract.yaml contract_scope 对齐
_SCAN_DIR = REPO_ROOT / "docs" / "01_policies_and_standards"
_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "architecture_contract.yaml"
)


def _load_frontmatter(fpath: Path) -> dict:
    """从 .md / .yaml 文件读取 frontmatter 字段（统一返回 dict）。

    .md  → YAML frontmatter（--- 分隔），用 _shared.frontmatter 解析
    .yaml/.yml → 顶层 YAML keys（整个文件是 dict，frontmatter 字段即顶层键）
    解析失败返回空 dict（跳过该文件，不阻断）。
    """
    import yaml

    suffix = fpath.suffix.lower()
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    if suffix == ".md":
        from _shared.frontmatter import parse_frontmatter

        metadata, _body = parse_frontmatter(text)
        return metadata if isinstance(metadata, dict) else {}
    if suffix in (".yaml", ".yml"):
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            return {}
        return data if isinstance(data, dict) else {}
    return {}


def _file_matches_directory_scope(fpath: Path, directory_scope: str) -> bool:
    """文件路径中是否包含 directory_scope 路径组件（如 governance / operational）。

    匹配 governance/、domains/x/governance/ 等任意层级的 governance 子目录。
    """
    try:
        rel_parts = fpath.relative_to(_SCAN_DIR).parts
    except ValueError:
        rel_parts = fpath.parts
    return any(part == directory_scope for part in rel_parts)


def _iter_target_files() -> list[Path]:
    """枚举扫描目录下所有 .md / .yaml / .yml 文件。"""
    # ARCH-036 P3-C4: 静默失效修正 — 返回空列表会让调用方认为"无文件需检查"，
    # 导致架构验证整体跳过。改为 stderr 警告。
    if not _SCAN_DIR.exists():
        print(f"[WARN] _SCAN_DIR not found: {_SCAN_DIR} — architecture validation scan skipped", file=sys.stderr)
        return []
    return [
        p
        for p in _SCAN_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in (".md", ".yaml", ".yml")
    ]


def _check_machine_rule(rule: dict, files: list[Path]) -> list[str]:
    """执行单条 machine_check 规则，返回违规描述列表。

    machine_check 结构（来自 architecture_contract.yaml）：
      filter_doc_type: policy        # 可选：仅检查 doc_type=此值 的文件
      filter_field: rule_form        # 可选：前置条件字段
      filter_value: procedural       # 可选：前置条件值
      assert_field: rule_form        # 必填：断言字段
      assert_equals: declarative     # 可选：字段必须等于此值
      assert_not_equals: inspection  # 可选：字段必须不等于此值
      assert_required: true          # 可选：字段必须存在
    """
    mc = rule.get("machine_check", {})
    if not mc:
        return []

    rule_id = rule.get("id", "?")
    rule_name = rule.get("name", "")
    violations: list[str] = []

    # 确定扫描范围：directory_scoped → 仅该子目录；project_wide → 全部
    tier = rule.get("tier", "project_wide")
    directory_scope = rule.get("directory_scope", "")
    if tier == "directory_scoped" and directory_scope:
        target_files = [f for f in files if _file_matches_directory_scope(f, directory_scope)]
    else:
        target_files = files

    filter_doc_type = mc.get("filter_doc_type")
    filter_field = mc.get("filter_field")
    filter_value = mc.get("filter_value")
    assert_field = mc.get("assert_field")
    assert_equals = mc.get("assert_equals")
    assert_not_equals = mc.get("assert_not_equals")
    assert_required = mc.get("assert_required", False)

    for fpath in target_files:
        fm = _load_frontmatter(fpath)
        if not fm:
            continue

        # 应用 filter_doc_type：仅检查 doc_type 匹配的文件
        if filter_doc_type is not None:
            if str(fm.get("doc_type", "")).strip() != filter_doc_type:
                continue

        # 应用 filter_field + filter_value：前置条件不满足则跳过
        if filter_field is not None:
            actual = str(fm.get(filter_field, "")).strip()
            if actual != filter_value:
                continue

        # 执行断言
        rel = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
        actual_value = fm.get(assert_field)

        # assert_required：字段必须存在且非空
        if assert_required and not actual_value:
            violations.append(
                f"  {rule_id} VIOLATION: {rel} —— 缺少必填字段 '{assert_field}'"
                f"（{rule_name}）"
            )
            continue

        # assert_equals：字段必须等于指定值
        if assert_equals is not None:
            actual_str = str(actual_value).strip() if actual_value else ""
            if actual_str != assert_equals:
                violations.append(
                    f"  {rule_id} VIOLATION: {rel} —— {assert_field}='{actual_str}'"
                    f" 不等于期望值 '{assert_equals}'（{rule_name}）"
                )
            continue

        # assert_not_equals：字段必须不等于指定值
        if assert_not_equals is not None:
            actual_str = str(actual_value).strip() if actual_value else ""
            if actual_str == assert_not_equals:
                violations.append(
                    f"  {rule_id} VIOLATION: {rel} —— {assert_field}='{actual_str}'"
                    f" 等于禁止值 '{assert_not_equals}'（{rule_name}）"
                )

    return violations


def main() -> int:
    """Validate architecture compliance against contract."""
    parser = argparse.ArgumentParser(
        description="GATE-16 架构合规校验——从 architecture_contract.yaml 动态读取 machine_check 执行"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 模式：发现违规 exit 1 阻断提交（默认行为）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现违规仅打印，exit 0 不阻断",
    )
    args = parser.parse_args()

    warn_only = args.warn_only

    print("=" * 72)
    print("GATE-16: 架构合规校验（VR machine_check 引擎）")
    print("真源: architecture_contract.yaml validation_rules[].machine_check")
    print(f"模式: {'--warn-only（警告不阻断）' if warn_only else '--ci / 默认（违规即阻断）'}")
    print("=" * 72)
    print()

    if not _CONTRACT_PATH.exists():
        print("WARN: architecture_contract.yaml not found, baseline pass")
        return EXIT_PASS

    import yaml

    with open(_CONTRACT_PATH, encoding="utf-8") as f:
        contract = yaml.safe_load(f)

    if not isinstance(contract, dict):
        print("WARN: architecture_contract.yaml 解析失败，baseline pass")
        return EXIT_PASS

    validation_rules = contract.get("validation_rules", [])
    machine_rules = [r for r in validation_rules if isinstance(r, dict) and r.get("machine_check")]

    if not machine_rules:
        print("WARN: architecture_contract.yaml 中无 machine_check 规则，baseline pass")
        return EXIT_PASS

    files = _iter_target_files()
    print(f"扫描目录: {_SCAN_DIR.relative_to(REPO_ROOT)}")
    print(f"目标文件: {len(files)} 个 (.md/.yaml/.yml)")
    print(f"machine_check 规则: {len(machine_rules)} 条")
    print()

    all_violations: list[str] = []
    for rule in machine_rules:
        rid = rule.get("id", "?")
        rname = rule.get("name", "")
        violations = _check_machine_rule(rule, files)
        status = "FAIL" if violations else "PASS"
        print(f"  [{status}] {rid}: {rname} ({len(violations)} 违规)")
        all_violations.extend(violations)

    print()
    if all_violations:
        print(f"🔴 发现 {len(all_violations)} 处 VR 违规:")
        for v in all_violations:
            print(v)
        print()
        if warn_only:
            print("（--warn-only 模式，exit 0 不阻断）")
            return EXIT_PASS
        return EXIT_FINDINGS

    print("✅ 架构合规校验通过——所有 machine_check 规则无违规")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
