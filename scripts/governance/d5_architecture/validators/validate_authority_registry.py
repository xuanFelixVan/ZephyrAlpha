# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_authority_registry.py | §
"""AI 自治权限注册表 pre-commit 自校验 (Authority Registry Validator · V-11)

任务编号 : T-V2-003 (Wave 0 终审 R74 兜底)
权限层级 : Immutable Core
创建日期 : 2026-04-27

功能说明
--------
作为 pre-commit 钩子运行，校验 ai-autonomy-authority-registry.md 中的权限标注：
1. 三层权限值必须属于 {Immutable Core, Human-Gated, AI-Modifiable}
2. 每行必填字段：module / authority / rationale
3. 同一 module_id 不得重复出现（禁止权限漂移）
4. 模块覆盖率检查（业务核心 + 平台能力 + 基础设施 + 治理）

校验目标
--------
- docs/01_policies_and_standards/_registry/catalogs/ai-autonomy-authority-registry.md

用法
----
正常扫描：
    python scripts/governance/validate_authority_registry.py

骨架阶段（只警告不阻塞）：
    python scripts/governance/validate_authority_registry.py --warn-only

CI 模式（违规 exit 1）：
    python scripts/governance/validate_authority_registry.py --ci
"""

from __future__ import annotations

__manifest__ = """
args: []
description: AI autonomy authority registry validator (3-tier auth / required fields / duplicate detection)
dimensions:
- D5
priority: P1
timeout_seconds: 30
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
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
try:
    from pydantic import BaseModel, Field
except ImportError:
    print("ERROR: Pydantic v2 未安装，请运行 `pip install pydantic>=2.0.0`", file=sys.stderr)
    sys.exit(EXIT_ERROR)
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装，请运行 `pip install pyyaml`", file=sys.stderr)
    sys.exit(EXIT_ERROR)
from _shared.constants import REPO_ROOT, EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR

REGISTRY_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "ai-autonomy-authority-registry.md"
)
VALID_AUTHORITIES = {"Immutable Core", "Human-Gated", "AI-Modifiable"}
REQUIRED_SECTIONS = {"2.1", "2.2", "2.3"}
SECTION_HEADER_RE = re.compile("^###\\s+(\\d+\\.\\d+)")
HEADER_ROW_KEYWORDS = {
    "模块",
    "组件",
    "路径",
    "权限",
    "判定理由",
    "审批要求",
    "层级",
    "语义",
    "AI 自主修改权限",
    "修改流程",
    "layer",
    "module",
    "authority",
    "rationale",
}
SKIP_FIRST_CELL_PATTERNS = [
    re.compile("^`[^`]*`$"),
    re.compile("^（"),
    re.compile("^见\\s"),
    re.compile("^同上$"),
    re.compile("^来源文档$"),
]
DATA_TABLE_SECTIONS_PREFIX = "2."


class AuthorityEntry(BaseModel):
    module: str
    authority: str
    rationale: str
    section: str = ""

    def is_valid_authority(self) -> bool:
        """判断 authority 值是否合法"""
        return self.authority in VALID_AUTHORITIES


def _is_header_row(cells: list[str]) -> bool:
    """_is_header_row implementation."""
    non_empty = [c for c in cells if c.strip()]
    if not non_empty:
        return False
    return any(c.strip() in HEADER_ROW_KEYWORDS for c in non_empty[:3])


def _is_separator_row(stripped: str) -> bool:
    """_is_separator_row implementation."""
    return bool(re.match("^\\|[\\s\\-:]+\\|", stripped))


def _extract_authority(cells: list[str]) -> str:
    """_extract_authority implementation."""
    for cell in cells[1:]:
        for valid in VALID_AUTHORITIES:
            if valid in cell:
                return valid
    for cell in cells[1:]:
        if "Immutable" in cell:
            return "Immutable Core"
        if "Human-Gated" in cell:
            return "Human-Gated"
        if "AI-Modifiable" in cell:
            return "AI-Modifiable"
    return ""


def _extract_rationale(cells: list[str], authority_col_idx: int) -> str:
    """_extract_rationale implementation."""
    for i in range(authority_col_idx + 1, len(cells)):
        val = cells[i].strip()
        if val and val not in VALID_AUTHORITIES:
            return val
    if len(cells) > 2:
        for i in range(2, len(cells)):
            val = cells[i].strip()
            if val and val not in VALID_AUTHORITIES:
                return val
    return ""


def parse_registry_tables(path: Path) -> list[AuthorityEntry]:
    """解析注册表表格"""
    text = path.read_text(encoding="utf-8")
    entries: list[AuthorityEntry] = []
    current_section = ""
    in_data_section = False
    for line in text.splitlines():
        header_match = SECTION_HEADER_RE.match(line.strip())
        if header_match:
            current_section = header_match.group(1)
            in_data_section = current_section.startswith(DATA_TABLE_SECTIONS_PREFIX)
            continue
        h2_match = re.match("^##\\s+[^#]", line.strip())
        if h2_match and (not line.strip().startswith("## 二")):
            in_data_section = False
            continue
        if not in_data_section:
            continue
        if "|" not in line:
            continue
        stripped = line.strip()
        if _is_separator_row(stripped):
            continue
        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c != ""]
        if len(cells) < 3:
            continue
        if _is_header_row(cells):
            continue
        first_cell = cells[0].strip()
        if not first_cell:
            continue
        for pat in SKIP_FIRST_CELL_PATTERNS:
            if pat.match(first_cell):
                break
        else:
            authority_val = _extract_authority(cells)
            rationale = _extract_rationale(cells, 2)
            entries.append(
                AuthorityEntry(module=first_cell, authority=authority_val, rationale=rationale, section=current_section)
            )
    return entries


def validate_authority_values(entries: list[AuthorityEntry]) -> list[str]:
    """校验 authority 值"""
    errors: list[str] = []
    for e in entries:
        if not e.authority:
            errors.append(f"[{e.section}] {e.module}: 缺少权限标注")
        elif not e.is_valid_authority():
            errors.append(f"[{e.section}] {e.module}: 无效权限值 '{e.authority}'，必须 ∈ {VALID_AUTHORITIES}")
    return errors


def validate_duplicate_modules(entries: list[AuthorityEntry]) -> list[str]:
    """校验重复模块"""
    errors: list[str] = []
    seen: dict[str, list[str]] = {}
    for e in entries:
        normalized = e.module.strip().lower()
        if normalized in seen:
            seen[normalized].append(e.section)
        else:
            seen[normalized] = [e.section]
    for module, sections in seen.items():
        if len(sections) > 1:
            errors.append(f"重复模块: '{module}' 出现在 {len(sections)} 个章节: {sections}")
    return errors


def validate_section_coverage(entries: list[AuthorityEntry]) -> list[str]:
    """校验段落覆盖"""
    errors: list[str] = []
    found_sections: set[str] = set()
    for e in entries:
        if e.section:
            found_sections.add(e.section)
    missing = REQUIRED_SECTIONS - found_sections
    if missing:
        errors.append(f"缺少必要章节的权限标注: {missing}")
    return errors


def validate_required_fields(entries: list[AuthorityEntry]) -> list[str]:
    """校验必填字段"""
    errors: list[str] = []
    for e in entries:
        if not e.module.strip():
            errors.append(f"[{e.section}]: 模块名为空")
        if not e.rationale.strip() and e.authority in {"Immutable Core", "Human-Gated"}:
            errors.append(f"[{e.section}] {e.module}: {e.authority} 权限缺少判定理由")
    return errors


def validate_immutable_core_coverage(entries: list[AuthorityEntry]) -> list[str]:
    """校验不可变核心覆盖"""
    errors: list[str] = []
    immutable_modules = [e for e in entries if e.authority == "Immutable Core"]
    if len(immutable_modules) < 5:
        errors.append(f"Immutable Core 模块数过少: {len(immutable_modules)} 个（预期 ≥5），可能存在权限标注遗漏")
    return errors


def run_validation(verbose: bool = False) -> tuple[list[str], int]:
    """执行校验"""
    if not REGISTRY_PATH.exists():
        return ([f"注册表文件不存在: {REGISTRY_PATH}"], 0)
    entries = parse_registry_tables(REGISTRY_PATH)
    if not entries:
        return (["未能从注册表解析到任何权限条目"], 0)
    if verbose:
        print(f"[validate_authority_registry] 解析到 {len(entries)} 个权限条目", file=sys.stderr)
    all_errors: list[str] = []
    all_errors.extend(validate_authority_values(entries))
    all_errors.extend(validate_duplicate_modules(entries))
    all_errors.extend(validate_section_coverage(entries))
    all_errors.extend(validate_required_fields(entries))
    all_errors.extend(validate_immutable_core_coverage(entries))
    return (all_errors, len(entries))


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="V-11 AI 自治权限注册表 pre-commit 自校验（Wave 0 终审 R74）")
    parser.add_argument("--ci", action="store_true", help="CI 模式：违规即 exit 1")
    parser.add_argument("--warn-only", action="store_true", help="骨架阶段：只警告不阻塞（exit 0）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()
    errors, count = run_validation(verbose=args.verbose)
    print(f"[validate_authority_registry] 扫描 {count} 个权限条目，发现 {len(errors)} 项违规", file=sys.stderr)
    for err in errors:
        print(f"  - {err}", file=sys.stderr)
    if not errors:
        print("[validate_authority_registry] PASS", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if args.warn_only:
        print("[validate_authority_registry] WARN-ONLY 模式：发现违规但不阻塞", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if args.ci:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
