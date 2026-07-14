# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_ssot_uniqueness.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_ssot_uniqueness
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
# [TTL] task_bound
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_ssot_uniqueness
[INVARIANTS] 扫描所有蓝图 ssot_claims 字段; 检测跨蓝图 SSoT 冲突
[MODIFY-GUARD] script_manifest.yaml; blueprint-construction-template.md
[CONSUMERS] CI pipeline; AI session 冷启动
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=CLEAN, exit 1=CONFLICT, exit 2=ERROR
[TESTS] tests/governance/test_check_ssot_uniqueness.py
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

import argparse

from _shared.constants import BLUEPRINTS_DIR, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.walk import iter_files

__manifest__ = """
args: [--warn-only]
description: 跨蓝图SSoT唯一性检测——检测两个蓝图是否claim了相同scope的SSoT
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""



def extract_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    fm_text = content[3:end]
    result = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("-"):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def extract_ssot_claims(blueprint_path: Path) -> list[dict]:
    content = blueprint_path.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)
    claims_raw = fm.get("ssot_claims", "")
    if not claims_raw:
        return []
    claims = []
    in_claims = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("ssot_claims:"):
            in_claims = True
            continue
        if in_claims:
            if stripped.startswith("- claim:"):
                claim_val = stripped[len("- claim:") :].strip().strip('"').strip("'")
                claims.append({"claim": claim_val, "scope": "global"})
            elif stripped.startswith("scope:"):
                scope_val = stripped[len("scope:") :].strip().strip('"').strip("'")
                if claims:
                    claims[-1]["scope"] = scope_val
            elif (
                stripped
                and not stripped.startswith("-")
                and not stripped.startswith("scope:")
                and not stripped.startswith("claim:")
                and not stripped.startswith("#")
                and not stripped.startswith("description:")
                and not stripped.startswith("type:")
                and not stripped.startswith("items:")
                and not stripped.startswith("properties:")
                and not stripped.startswith("example:")
            ):
                in_claims = False
    return claims


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SSoT uniqueness across blueprints")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even if conflicts found")
    args = parser.parse_args()

    if not BLUEPRINTS_DIR.exists():
        print("ERROR: blueprints directory not found")
        return EXIT_ERROR

    all_claims: dict[str, list[tuple[str, dict]]] = {}
    for bp in iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md"):
        claims = extract_ssot_claims(bp)
        module_id = bp.parent.name
        for claim in claims:
            key = f"{claim['claim']}|{claim['scope']}"
            if key not in all_claims:
                all_claims[key] = []
            all_claims[key].append((module_id, claim))

    conflicts = []
    for key, entries in all_claims.items():
        if len(entries) > 1:
            claim_text, scope = key.split("|")
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    conflicts.append((entries[i][0], entries[j][0], claim_text, scope))

    if conflicts:
        print(f"SSoT CONFLICTS: {len(conflicts)}")
        print(f"{'蓝图A':<30} {'蓝图B':<30} {'冲突claim':<30} {'scope':<10}")
        print("-" * 100)
        for a, b, claim, scope in conflicts:
            print(f"{a:<30} {b:<30} {claim:<30} {scope:<10}")
        if args.warn_only:
            print("WARN: conflicts found but --warn-only mode")
            return EXIT_PASS
        return EXIT_FINDINGS

    print("SSoT UNIQUENESS: CLEAN — no conflicts found")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
