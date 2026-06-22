# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_template_compliance.py | §
from __future__ import annotations

"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain-governance/governance-automation/blueprint.md | §
[MODULE] scripts.governance.d3_metadata.check_template_compliance
[INVARIANTS] 模板合规检查必须覆盖所有模板
[MODIFY-GUARD] __init__.py;script_manifest.yaml
[CONSUMERS] CI pipeline;governance gate
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] sys.exit(1)
[TESTS] tests/governance/test_d3_metadata.py
"""
"""
通用模板合规检查--读取模板的 COMPLIANCE_CHECKLIST，验证目标文档是否符合。
对标: blueprint-construction-template.md v4.0 的 COMPLIANCE_CHECKLIST 模式，泛化到全部 11 个模板。

支持模板类型: blueprint / task-card / playbook / policy / protocol /
  register / risk-register / roadmap / runbook / standard / dependency-graph

用法:
  python check_template_compliance.py <文档路径> --template <模板类型>
  python check_template_compliance.py <文档路径> --auto  (自动从 frontmatter 推断)
  python check_template_compliance.py --all  (扫描所有文档，按类型批量检查)

exit: 0=pass, 1=findings, 2=error
"""

__manifest__ = """
args: ["文档路径", "--template", "--auto", "--all", "--warn-only"]
description: 通用模板合规检查——读取 COMPLIANCE_CHECKLIST 验证文档（D3元数据合规）
dimensions:
- D3
priority: P1
timeout_seconds: 60
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

ensure_utf8_stdout()

TEMPLATES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "templates"

TEMPLATE_TYPE_TO_FILE = {
    "blueprint": "blueprint-construction-template.md",
    "playbook": "playbook-template.md",
    "policy": "policy-policy.md",
    "protocol": "protocol-protocol.md",
    "register": "register-registry.md",
    "risk-register": "risk-register-registry.md",
    "roadmap": "roadmap-template.md",
    "runbook": "runbook-runbook.md",
    "standard": "standard-standard.md",
    "dependency-graph": "dependency-graph-template.md",
}

DOC_TYPE_TO_TEMPLATE = {
    "blueprint": "blueprint",
    "task_card": "task-card",
    "operational_rule": "playbook",
    "policy": "policy",
    "protocol": "protocol",
    "register": "register",
    "risk_register": "risk-register",
    "plan": "roadmap",
    "standard": "standard",
    "template": "dependency-graph",
}


def extract_required_sections(template_path: Path) -> dict[str, str]:
    content = template_path.read_text(encoding="utf-8")
    match = re.search(r"REQUIRED_SECTIONS:\s*\n(.*?)END_REQUIRED_SECTIONS", content, re.DOTALL)
    if not match:
        return {}
    sections = {}
    for line in match.group(1).strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'(\S+):\s*"([^"]+)"', line)
        if m:
            sections[m.group(1)] = m.group(2)
    return sections


def detect_template_type(doc_path: Path) -> str | None:
    content = doc_path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None
    fm_text = fm_match.group(1)
    doc_type_match = re.search(r"doc_type:\s*['\"]?(\S+)['\"]?", fm_text)
    if doc_type_match:
        doc_type = doc_type_match.group(1).strip("'\"")
        return DOC_TYPE_TO_TEMPLATE.get(doc_type)
    return None


def check_document(doc_path: Path, template_type: str, warn_only: bool = False) -> int:
    if not doc_path.exists():
        print(f"ERROR: 文件不存在: {doc_path}")
        return EXIT_ERROR

    template_file = TEMPLATE_TYPE_TO_FILE.get(template_type)
    if not template_file:
        print(f"ERROR: 未知模板类型: {template_type}")
        print(f"  可用类型: {', '.join(TEMPLATE_TYPE_TO_FILE.keys())}")
        return EXIT_ERROR

    template_path = TEMPLATES_DIR / template_file
    if not template_path.exists():
        print(f"ERROR: 模板文件不存在: {template_path}")
        return EXIT_ERROR

    required = extract_required_sections(template_path)
    if not required:
        print(f"WARN: 模板 {template_type} 没有 COMPLIANCE_CHECKLIST，跳过")
        return EXIT_PASS

    content = doc_path.read_text(encoding="utf-8")
    headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    content_lower = content.lower()

    errors = 0
    warnings = 0
    found = 0

    print(f"  模板: {template_type} ({len(required)} 项必填章节)")

    for sec_id, keyword in required.items():
        is_sub = "." in sec_id or sec_id.startswith("pre_")
        matched = False
        for h in headings:
            if keyword.lower() in h.lower():
                matched = True
                break
        if not matched and keyword.lower() not in content_lower:
            prefix = "  ⚠️" if is_sub else "  ❌"
            print(f"{prefix} 缺失: {sec_id} — {keyword}")
            if is_sub:
                warnings += 1
            else:
                errors += 1
        else:
            found += 1

    total = len(required)
    compliance = found / total * 100 if total > 0 else 0

    print(f"\n  合规率: {compliance:.0f}% ({found}/{total})")

    if errors > 0:
        print(f"  结果: ❌ FAIL ({errors} 错误, {warnings} 警告)")
        return EXIT_FINDINGS if not warn_only else EXIT_PASS
    elif warnings > 0:
        print(f"  结果: ⚠️ WARN ({warnings} 警告)")
        return EXIT_PASS
    else:
        print("  结果: ✅ PASS")
        return EXIT_PASS


def check_all_documents(warn_only: bool = False) -> int:
    total_exit = EXIT_PASS
    checked = 0

    scan_dirs = [
        REPO_ROOT / "docs" / "01_policies_and_standards",
        REPO_ROOT / "docs" / "03_modules",
        REPO_ROOT / "docs" / "02_enterprise_architecture",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for md_file in scan_dir.rglob("*.md"):
            if md_file.name.endswith("-template.md"):
                continue
            template_type = detect_template_type(md_file)
            if template_type is None:
                continue

            print(f"\n{'=' * 60}")
            print(f"检查: {md_file.relative_to(REPO_ROOT)}")
            print(f"{'=' * 60}")
            exit_code = check_document(md_file, template_type, warn_only)
            if exit_code != EXIT_PASS:
                total_exit = EXIT_FINDINGS
            checked += 1

    print(f"\n{'=' * 60}")
    print(f"总计检查 {checked} 个文档")
    print(f"{'=' * 60}")
    return total_exit


def main() -> int:
    parser = argparse.ArgumentParser(description="通用模板合规检查")
    parser.add_argument("document", nargs="*", help="文档文件路径")
    parser.add_argument("--template", "-t", choices=list(TEMPLATE_TYPE_TO_FILE.keys()), help="模板类型")
    parser.add_argument("--auto", "-a", action="store_true", help="自动从 frontmatter 推断模板类型")
    parser.add_argument("--all", action="store_true", help="扫描所有文档，按类型批量检查")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断")
    args = parser.parse_args()

    if args.all:
        return check_all_documents(args.warn_only)

    if not args.document:
        parser.print_help()
        return EXIT_ERROR

    total_exit = EXIT_PASS
    for doc in args.document:
        doc_path = Path(doc)
        if args.template:
            template_type = args.template
        elif args.auto:
            template_type = detect_template_type(doc_path)
            if template_type is None:
                print(f"ERROR: 无法推断模板类型: {doc}")
                return EXIT_ERROR
        else:
            print("ERROR: 必须指定 --template <类型> 或 --auto")
            return EXIT_ERROR

        print(f"\n{'=' * 60}")
        print(f"检查: {doc}")
        print(f"{'=' * 60}")
        exit_code = check_document(doc_path, template_type, args.warn_only)
        if exit_code != EXIT_PASS:
            total_exit = EXIT_FINDINGS

    return total_exit


if __name__ == "__main__":
    sys.exit(main())
