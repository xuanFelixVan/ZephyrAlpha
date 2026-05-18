# [BLUEPRINT] MOD-INF-005 | scripts/governance/sync_rule_registry.py | §
"""
Checks that every RULE-ZERO through RULE-N in .trae/rules/project_rules.md
has a corresponding TRAE-* entry in the rule-registry.md TRAE domain.

Exit codes: 0 = synced, 1 = drift detected, 2 = error
"""

from __future__ import annotations
from _shared.encoding import ensure_utf8_stdout
ensure_utf8_stdout()
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS


__manifest__ = """
args: []
description: >
  TRAE 规则登记同步校验 —— 扫描 .trae/rules/project_rules.md 中所有 RULE-* 条目，
  检查是否已在 rule-registry.md 的 TRAE 域中登记。RULE-FOUR（创建即注册协议）的执行验证。
  Exit 0 = CLEAN, Exit 1 = DRIFT（缺失/孤儿登记）。
dimensions:
- D3
- D8
priority: P1
timeout_seconds: 15
warn_only: false
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_RULES = ROOT / ".trae" / "rules" / "project_rules.md"
RULE_REGISTRY = ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule-registry.md"


def extract_rules_from_project() -> dict[str, str]:
    """Parse project_rules.md → {rule_id: one-line summary}."""
    if not PROJECT_RULES.exists():
        print(f"ERROR: {PROJECT_RULES} not found")
        sys.exit(EXIT_ERROR)

    content = PROJECT_RULES.read_text(encoding="utf-8")
    rules: dict[str, str] = {}

    # Match: ## 🔴 RULE-xxx：title
    pattern = re.compile(
        r"^##\s+🔴\s+(RULE-\w+)[：:]\s*(.+)$",
        re.MULTILINE,
    )
    for m in pattern.finditer(content):
        rule_id = m.group(1)
        title = m.group(2).strip()
        rules[rule_id] = title

    return rules


def extract_trae_from_registry() -> dict[str, str]:
    """Parse rule-registry.md → {TRAE-NNN: description text}."""
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


def build_mapping(rules: dict[str, str]) -> dict[str, str]:
    """Map RULE-ZERO → TRAE-001, RULE-ONE → TRAE-002, ..."""
    mapping: dict[str, str] = {}
    number_words = {
        "ZERO": "001", "ONE": "002", "TWO": "003", "THREE": "004",
        "FOUR": "005", "FIVE": "006", "SIX": "007", "SEVEN": "008",
        "EIGHT": "009", "NINE": "010", "TEN": "011",
    }
    for rule_id in rules:
        suffix = rule_id.replace("RULE-", "")
        trae_num = number_words.get(suffix)
        if trae_num:
            mapping[rule_id] = f"TRAE-{trae_num}"
        else:
            # Try numeric: RULE-10 → TRAE-010, RULE-11 → TRAE-011
            try:
                num = int(suffix)
                mapping[rule_id] = f"TRAE-{num:03d}"
            except ValueError:
                print(f"  WARN: Cannot map {rule_id} to TRAE-* (non-standard suffix: {suffix})")
    return mapping


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    rules = extract_rules_from_project()
    trae_entries = extract_trae_from_registry()
    mapping = build_mapping(rules)

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
            missing.append(f"  {rule_id} → {trae_id} (missing in rule-registry.md): {summary}")

    for trae_id in sorted(trae_entries):
        # Reverse lookup: which RULE maps to this TRAE?
        mapped_from = None
        for rid, tid in mapping.items():
            if tid == trae_id:
                mapped_from = rid
                break
        if mapped_from is None:
            orphaned.append(
                f"  {trae_id} ({trae_entries[trae_id][:80]}) — no corresponding RULE-* in project_rules.md"
            )

    print(f"project_rules.md: {len(rules)} RULE-* entries")
    print(f"rule-registry.md:  {len(trae_entries)} TRAE-* entries")

    if missing:
        print(f"\n[MISSING] {len(missing)} RULE-* not registered in rule-registry.md:")
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
