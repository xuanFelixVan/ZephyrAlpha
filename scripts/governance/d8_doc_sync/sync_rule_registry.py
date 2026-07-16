# [BLUEPRINT] MOD-INF-005 | scripts/governance/sync_rule_registry.py | §
# [MODULE] scripts.governance.sync_rule_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
Checks that every RULE-ZERO through RULE-N in .trae/rules/project_rules.md
has a corresponding TRAE-* entry in the _index.yaml TRAE domain.

Exit codes: 0 = synced, 1 = drift detected, 2 = error
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

__manifest__ = """
args: []
description: >
  TRAE 规则登记同步校验 —— 扫描 .trae/rules/project_rules.md 中所有 RULE-* 条目，
  检查是否已在 _index.yaml 的 TRAE 域中登记。RULE-FOUR（创建即注册协议）的执行验证。
  Exit 0 = CLEAN, Exit 1 = DRIFT（缺失/孤儿登记）。
dimensions:
- D3
- D8
priority: P1
timeout_seconds: 15
warn_only: false
"""

import re
import sys
from pathlib import Path

ROOT = REPO_ROOT
PROJECT_RULES = ROOT / ".trae" / "rules" / "project_rules.md"
RULE_REGISTRY = ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "_index.yaml"


def extract_rules_from_project() -> dict[str, str]:
    """Parse project_rules.md → {rule_id: one-line summary}."""
    if not PROJECT_RULES.exists():
        print(f"ERROR: {PROJECT_RULES} not found")
        sys.exit(EXIT_ERROR)

    content = PROJECT_RULES.read_text(encoding="utf-8")
    rules: dict[str, str] = {}

    # Match: ## RULE-xxx：title  (supports merged entries like "## RULE-SIX + RULE-ZERO-TASK：title")
    pattern = re.compile(
        r"^##\s+(RULE-[\w-]+)(?:\s*\+\s*RULE-[\w-]+)?[：:]\s*(.+)$",
        re.MULTILINE,
    )
    for m in pattern.finditer(content):
        rule_id = m.group(1)
        title = m.group(2).strip()
        rules[rule_id] = title

    return rules


def extract_trae_from_registry() -> dict[str, str]:
    """Parse _index.yaml → {TRAE-NNN: description text}."""
    if not RULE_REGISTRY.exists():
        print(f"ERROR: {RULE_REGISTRY} not found")
        sys.exit(EXIT_ERROR)

    content = RULE_REGISTRY.read_text(encoding="utf-8")
    entries: dict[str, str] = {}

    pattern = re.compile(
        r"^\|\s*(TRAE-\d+)\s*\|\s*(.+?)\s*\|",
        re.MULTILINE,
    )
    for m in pattern.finditer(content):
        trae_id = m.group(1)
        desc = m.group(2).strip()
        entries[trae_id] = desc

    return entries


def build_mapping(rules: dict[str, str], trae_entries: dict[str, str]) -> dict[str, str]:
    """Build {RULE-XXX: TRAE-NNN} mapping by parsing TRAE descriptions.

    Parses each TRAE entry's description to extract the corresponding RULE-XXX,
    rather than assuming a fixed RULE-N → TRAE-(N+1) mapping. This handles
    non-sequential registrations (e.g., TRAE-012 = RULE-SEVENTEEN).
    """
    mapping: dict[str, str] = {}
    rule_pattern = re.compile(r"\b(RULE-[\w-]+)\b")
    for trae_id, desc in trae_entries.items():
        m = rule_pattern.search(desc)
        if m:
            rule_id = m.group(1)
            mapping[rule_id] = trae_id
    return mapping


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    rules = extract_rules_from_project()
    trae_entries = extract_trae_from_registry()
    mapping = build_mapping(rules, trae_entries)

    if not rules:
        print("[WARN] No RULE-* entries found in project_rules.md")
        return EXIT_PASS

    missing: list[str] = []
    orphaned: list[str] = []

    for rule_id, summary in sorted(rules.items()):
        trae_id = mapping.get(rule_id)
        if trae_id is None:
            missing.append(f"  {rule_id} (unmappable: {summary})")
        elif trae_id not in trae_entries:
            missing.append(f"  {rule_id} → {trae_id} (missing in _index.yaml): {summary}")

    for trae_id in sorted(trae_entries):
        # Reverse lookup: which RULE maps to this TRAE?
        mapped_from = None
        for rid, tid in mapping.items():
            if tid == trae_id:
                mapped_from = rid
                break
        if mapped_from is None:
            orphaned.append(f"  {trae_id} ({trae_entries[trae_id][:80]}) — no corresponding RULE-* in project_rules.md")

    print(f"project_rules.md: {len(rules)} RULE-* entries")
    print(f"_index.yaml:  {len(trae_entries)} TRAE-* entries")

    if missing:
        print(f"\n[MISSING] {len(missing)} RULE-* not registered in _index.yaml:")
        for m in missing:
            print(m)

    if orphaned:
        print(f"\n[ORPHANED] {len(orphaned)} TRAE-* entries with no corresponding RULE-*:")
        for o in orphaned:
            print(o)

    if not missing and not orphaned:
        print("\n[PASS] All RULE-* entries are registered. CLEAN.")
        return EXIT_PASS
    else:
        print(f"\n[DRIFT] {len(missing)} missing + {len(orphaned)} orphaned. Fix required.")
        return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
