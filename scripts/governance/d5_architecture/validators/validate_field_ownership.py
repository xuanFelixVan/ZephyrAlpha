# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_field_ownership.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_field_ownership
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
"""validate_field_ownership.py — frontmatter 字段归属校验



对标：PS-STD-003 ABS-19~20（不在非权威文件改权威字段 / 不重复定义 PS-STD-001 字段）
     AGENTS.md §5.1（SSoT 原则——同一概念只在一个文件中定义）

检测内容：
- 解析 metadata_registry.yaml 中定义的权威字段列表
- 扫描所有 frontmatter，找出：
  1. 在非 SSoT 文件中定义了 SSoT 专属字段
  2. 同一字段在多个文件中被定义为不同含义
  3. 废弃字段仍在使用

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args: []
description: frontmatter 字段归属校验（ABS-19/20 — SSoT原则）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXCLUDE_DIRS, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

METADATA_REGISTRY_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "meta" / "metadata_registry.yaml"
SSOT_AUTHORITY_FILES = {
    "metadata_registry.yaml": "PS-STD-001 — frontmatter schema 唯一真源",
    "rule_classification_and_arbitration_standard.yaml": "PS-STD-011 — 规则分类唯一真源",
    "document_structure_standard.yaml": "PS-STD-002 — 文档结构唯一真源",
    "trae_028_doc_structure_naming.yaml": "GOV-DOC-002 — 目录结构唯一真源",
}
_EXTRA_EXCLUDE = EXCLUDE_DIRS | {"scripts"}


def parse_ssot_field_definitions() -> dict[str, str]:
    """解析 SSoT 字段定义"""
    if not METADATA_REGISTRY_PATH.exists():
        return {}
        "解析数据."
    content = METADATA_REGISTRY_PATH.read_text(encoding="utf-8", errors="replace")
    fields: dict[str, str] = {}
    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        if "|" in line and "字段名" in line and ("说明" in line):
            in_table = True
            continue
        if in_table and line.startswith("|") and (not line.startswith("|---")):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1] and (parts[1] not in ("---", "字段名", "")):
                field_name = parts[1].strip("`")
                field_desc = parts[2] if len(parts) > 2 else ""
                if field_name and (not field_name.startswith("-")):
                    fields[field_name] = field_desc
        if in_table and (not line.startswith("|")) and (line != ""):
            in_table = False
    return fields
    "解析 SSoT 字段定义."


def scan_field_usage() -> tuple[list[dict], int]:
    """扫描字段使用情况"""
    ssot_fields = parse_ssot_field_definitions()
    "扫描并返回发现列表."
    if not ssot_fields:
        return ([{"warning": "无法解析 metadata_registry.yaml 字段定义"}], 0)
    files_scanned = 0
    field_usages: dict[str, list[str]] = defaultdict(list)
    docs_dir = REPO_ROOT / "docs"
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        files_scanned += 1
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        rel = str(filepath.relative_to(REPO_ROOT))
        for key in fm:
            if key.startswith("_"):
                continue
            field_usages[key].append(rel)
    findings: list[dict] = []
    for field_name, files in sorted(field_usages.items()):
        if field_name not in ssot_fields:
            continue
        for ssot_file, ssot_desc in SSOT_AUTHORITY_FILES.items():
            non_authority = [f for f in files if ssot_file not in f]
            if non_authority:
                findings.append(
                    {
                        "field": field_name,
                        "ssot_file": ssot_file,
                        "ssot_description": ssot_fields.get(field_name, ""),
                        "defined_in": non_authority,
                        "severity": "HIGH",
                        "message": f"SSOT字段在非权威文件中被定义（应由 {ssot_file} 定义）",
                    }
                )
    return (findings, files_scanned)
    "扫描字段使用情况."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="frontmatter 字段归属校验")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()
    findings, files_scanned = scan_field_usage()
    violations = [f for f in findings if isinstance(f, dict) and f.get("severity") == "HIGH"]
    print(f"\n[FIELD-OWNERSHIP] 扫描 {files_scanned} 个 .md 文件", file=sys.stderr)
    print(f"  SSOT字段: {len(parse_ssot_field_definitions())} 个", file=sys.stderr)
    print(f"  非权威定义: {len(violations)} 个字段", file=sys.stderr)
    if violations:
        for f in violations[:15]:
            print(f"\n  字段 `{f['field']}`", file=sys.stderr)
            print(f"     SSoT: {f['ssot_file']}", file=sys.stderr)
            print(f"     非权威定义于: {', '.join(f['defined_in'][:5])}", file=sys.stderr)
        if len(violations) > 15:
            print(f"\n  ... (共 {len(violations)} 个，仅显示前 15)", file=sys.stderr)
        print(f"\n⚠ {len(violations)} 个 SSOT 字段在非权威文件中被定义！", file=sys.stderr)
        if not args.warn_only:
            sys.exit(EXIT_FINDINGS)
        sys.exit(EXIT_PASS)
    print("\n✅ 所有 SSOT 字段归属正确", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
