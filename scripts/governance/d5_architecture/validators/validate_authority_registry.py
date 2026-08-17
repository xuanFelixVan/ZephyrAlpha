# [A_module] module_id=MOD-GOV_SCRIPTS_ARCH | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Module docstring — see module-level docstring for details."""
from __future__ import annotations

__manifest__ = """
args: []
description: AI 自治权限注册表校验器——校验 authority 注册表的完整性和一致性。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

# [BLUEPRINT] MOD-GOV_SCRIPTS_ARCH
# [MODULE] scripts.governance.d5_architecture.validators.validate_authority_registry
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""AI 自治权限注册表校验器.

校验 authority registry markdown 文件的:
- authority 值有效性（Immutable Core / Human-Gated / AI-Modifiable）
- 模块名重复检测（case-insensitive）
- section 覆盖（2.1 / 2.2 / 2.3）
- 必填字段（Immutable Core 必须有 rationale）
- Immutable Core 覆盖度（至少 3 个）
"""

import re
from pathlib import Path

VALID_AUTHORITIES = {"Immutable Core", "Human-Gated", "AI-Modifiable"}
REQUIRED_SECTIONS = {"2.1", "2.2", "2.3"}
IMMUTABLE_CORE_MIN = 3

REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "docs"
    / "01_policies_and_standards"
    / "policies"
    / "ai_autonomy_authority_registry.md"
)


class AuthorityEntry:
    """权限注册表条目."""

    def __init__(self, module="", authority="", rationale="", section=""):
        """__init__ implementation."""
        self.module = module
        self.authority = authority
        self.rationale = rationale
        self.section = section

    def is_valid_authority(self) -> bool:
        """is_valid_authority implementation."""
        return self.authority in VALID_AUTHORITIES


def parse_registry_tables(path) -> list[AuthorityEntry]:
    """从 markdown 文件解析权限注册表表格."""
    p = Path(path)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8")
    entries: list[AuthorityEntry] = []
    current_section = ""
    for line in text.splitlines():
        section_match = re.match(r"^###\s+(\S+)\s", line)
        if section_match:
            current_section = section_match.group(1)
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^[-:\s]*$", c) for c in cells):
            continue
        if cells and cells[0] == "模块":
            continue
        if len(cells) >= 3:
            full_module = cells[0]
            authority = cells[1]
            rationale = cells[2]
            parts = full_module.split()
            module = parts[0] if parts else full_module
            entries.append(
                AuthorityEntry(
                    module=module,
                    authority=authority,
                    rationale=rationale,
                    section=current_section,
                )
            )
    return entries


def validate_authority_values(entries: list[AuthorityEntry]) -> list[str]:
    """Validate target against rules and report findings."""
    errors: list[str] = []
    for e in entries:
        if not e.authority:
            errors.append(f"模块 {e.module}: 缺少权限标注")
        elif e.authority not in VALID_AUTHORITIES:
            errors.append(f"模块 {e.module}: 无效权限值 \'{e.authority}\'")
    return errors


def validate_duplicate_modules(entries: list[AuthorityEntry]) -> list[str]:
    """Validate target against rules and report findings."""
    errors: list[str] = []
    seen: dict[str, str] = {}
    for e in entries:
        key = e.module.lower()
        if key in seen:
            errors.append(f"重复模块: {e.module} (sections {seen[key]} 与 {e.section})")
        else:
            seen[key] = e.section
    return errors


def validate_section_coverage(entries: list[AuthorityEntry]) -> list[str]:
    """Validate target against rules and report findings."""
    sections = {e.section for e in entries if e.section}
    missing = sorted(s for s in REQUIRED_SECTIONS if s not in sections)
    if missing:
        return [f"缺少 section: {', '.join(missing)}"]
    return []


def validate_required_fields(entries: list[AuthorityEntry]) -> list[str]:
    """Validate target against rules and report findings."""
    errors: list[str] = []
    for e in entries:
        if not e.module.strip():
            errors.append(f"模块名为空 (section {e.section})")
        if e.authority == "Immutable Core" and not e.rationale:
            errors.append(f"模块 {e.module}: 缺少判定理由 (Immutable Core 必须填写)")
    return errors


def validate_immutable_core_coverage(entries: list[AuthorityEntry]) -> list[str]:
    """Validate target against rules and report findings."""
    immutable_count = sum(1 for e in entries if e.authority == "Immutable Core")
    if immutable_count < IMMUTABLE_CORE_MIN:
        return [
            f"Immutable Core 模块数过少: {immutable_count} < {IMMUTABLE_CORE_MIN}"
        ]
    return []


def run_validation(path=None):
    """运行完整校验，返回 (errors, count)."""
    registry_path = path if path is not None else REGISTRY_PATH
    if not Path(registry_path).exists():
        return [f"注册表文件不存在: {registry_path}"], 0
    entries = parse_registry_tables(registry_path)
    errors: list[str] = []
    errors.extend(validate_authority_values(entries))
    errors.extend(validate_duplicate_modules(entries))
    errors.extend(validate_section_coverage(entries))
    errors.extend(validate_required_fields(entries))
    errors.extend(validate_immutable_core_coverage(entries))
    return errors, len(entries)
