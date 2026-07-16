# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/audit_agent_spec.py | §
# [MODULE] scripts.governance.d5_architecture.audit_agent_spec
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
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
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.audit_agent_spec
[INVARIANTS] agent-spec 审计完整性
[MODIFY-GUARD] __init__.py;script_manifest.yaml
[CONSUMERS] CI pipeline;governance gate
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] sys.exit(1)
[TESTS] tests/governance/test_d5_architecture.py
"""

__manifest__ = """
args: []
description: '[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md
  | §'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from zephyr.autonomy_core.agent_lifecycle.engine import SpecEngine
from zephyr.autonomy_core.agent_lifecycle.skill_loader import SkillLoader

e = SpecEngine()
r = e.drift_check()
loader = SkillLoader()

print("=" * 70)
print("HEALTHY SKILLS (24) - Content Quality Audit")
print("=" * 70)

total_real = 0
total_template = 0
healthy_ids = sorted(r["healthy_ids"])

for sid in healthy_ids:
    try:
        data = loader.progressive_load(sid)
        l1 = data.get("l1", {})
        l2 = data.get("l2", "")
        name = l1.get("name", sid)
        freshness = l1.get("freshness_score", 0)
        version = l1.get("version", "?")

        # Check if content looks real
        body_words = len(re.findall(r"\b\w+\b", l2))
        has_template = any(
            kw in l2
            for kw in [
                "待填写",
                "TODO",
                "TBD",
                "PLACEHOLDER",
                "此技能仍在构建中",
                "Coming soon",
                "generated from blueprint",
            ]
        )
        has_real_sections = any(
            kw in l2
            for kw in [
                "CRITICAL",
                "关键",
                "MUST",
                "Core Operations",
                "Allowed Tools",
                "Unique Constraints",
                "Common Errors",
                "Checklist",
                "References",
                "前置条件",
                "核心操作",
            ]
        )

        quality = "REAL" if (body_words > 200 and not has_template and has_real_sections) else "WEAK"
        if quality == "REAL":
            total_real += 1
            print(f"[REAL] {name} ({sid}) v{version} freshness={freshness} body_words={body_words}")
            # Show a sample of the content
            sample_lines = [l.strip() for l in l2.split("\n") if l.strip() and not l.strip().startswith("#")][:3]
            for sl in sample_lines:
                print(f"       > {sl[:100]}")
        else:
            total_template += 1
            flags = []
            if has_template:
                flags.append("TEMPLATE_KW")
            if body_words < 200:
                flags.append(f"LOW_WORDS({body_words})")
            if not has_real_sections:
                flags.append("NO_REAL_SECTIONS")
            print(f"[WEAK] {name} ({sid}) v{version} - {' '.join(flags)}")
    except Exception as exc:
        print(f"[ERR] {sid}: {exc}")

print(f"\nReal: {total_real}/{len(healthy_ids)}, Template/Weak: {total_template}/{len(healthy_ids)}")

print()
print("=" * 70)
print("DRIFTED SKILLS (47) - Summary by category")
print("=" * 70)

placeholder_count = 0
missing_count = 0
other_count = 0
for d in r["drifted_details"]:
    issues = d.get("issues", [d.get("reason", "")])
    iss_str = "; ".join(issues)
    if "placeholder" in iss_str.lower() or "待填写" in iss_str:
        placeholder_count += 1
    elif "missing" in iss_str.lower():
        missing_count += 1
    else:
        other_count += 1
        print(f"  [OTHER] {d['name']}: {iss_str}")

print(f"Placeholder: {placeholder_count}, Missing: {missing_count}, Other: {other_count}")
