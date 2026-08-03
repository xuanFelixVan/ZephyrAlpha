# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_blueprint_provenance.py | §
# [MODULE] scripts.governance.d3_metadata.validate_blueprint_provenance
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Blueprint Provenance Gate - V-12: validate provenance triples in blueprint frontmatter
Task: T-V2-001 (Wave 0 final review R73)
"""

from __future__ import annotations

import re
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
args: []
description: Blueprint provenance triple validation (origin_drafts + audit_chain + arbitration) + node_id/edge_id hardcode lint
dimensions:
- D3
- D4
priority: P0
timeout_seconds: 30
warn_only: false
"""

# 文档引用铁律（2026-08-04）：禁止蓝图/文档硬编码 node_id/edge_id（PostgreSQL 自增主键，删除重建即变）
# 蓝图引用 depgraph 时只写稳定逻辑标识（module_id/blueprint_id/path）
_NODE_ID_HARDCODE_RE = re.compile(r"\b(node_id|edge_id)\s*=\s*(\d+)\b")


def _check_node_id_hardcode(fpath: Path, text: str) -> int:
    """检查蓝图正文中是否硬编码 node_id/edge_id（文档引用铁律）。

    违规示例：``> **depgraph**: MOD-EX-049 (node_id=8005442)`` → 应改为仅 module_id。
    合法引用标识：module_id / blueprint_id / path（稳定逻辑标识）。
    """
    matches = _NODE_ID_HARDCODE_RE.findall(text)
    if not matches:
        return 0
    try:
        rel = fpath.relative_to(REPO_ROOT)
    except ValueError:
        rel = fpath
    for kind, num in matches:
        print(
            f"  ERROR: {rel} 硬编码 {kind}={num}"
            f"（文档引用铁律：禁止 node_id/edge_id 硬编码，改用 module_id/blueprint_id/path）"
        )
    return len(matches)


def main() -> int:
    """Validate provenance fields + node_id/edge_id hardcode in blueprint files."""

    errors = 0
    # 扫描范围：docs/03_modules（仅 blueprint.md）+ docs/04_construction_plans + docs/01_policies_and_standards
    scan_dirs = [
        REPO_ROOT / "docs" / "03_modules",
        REPO_ROOT / "docs" / "04_construction_plans",
        REPO_ROOT / "docs" / "01_policies_and_standards",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        is_modules_dir = scan_dir.name == "03_modules"
        for fpath in scan_dir.rglob("*.md"):
            # docs/03_modules 下只扫描 blueprint.md（索引/说明文档不含 depgraph 引用）
            if is_modules_dir and fpath.name != "blueprint.md":
                continue
            try:
                text = fpath.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # ── 文档引用铁律（2026-08-04）：禁止 node_id/edge_id 硬编码 ──
            errors += _check_node_id_hardcode(fpath, text)

            # ── provenance 三件套校验（原逻辑）──
            in_frontmatter = False
            provenance = {}
            for line in text.split("\n"):
                stripped = line.strip()
                if stripped == "---":
                    in_frontmatter = not in_frontmatter
                    if not in_frontmatter:
                        break
                    continue
                if in_frontmatter and ":" in stripped:
                    key, _, val = stripped.partition(":")
                    provenance[key.strip()] = val.strip()

            if not provenance:
                continue

            origin = provenance.get("origin_drafts", "")
            arbitration = provenance.get("arbitration", "")
            if not origin:
                continue

            if not arbitration:
                rel = fpath.relative_to(REPO_ROOT)
                print(f"  WARN: {rel} missing arbitration field in provenance")
                errors += 1

    if errors:
        print(f"\nFAIL: {errors} blueprint issue(s) [provenance + node_id hardcode]")
        return EXIT_FINDINGS

    print("OK: Blueprint provenance + node_id hardcode validation passed")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
