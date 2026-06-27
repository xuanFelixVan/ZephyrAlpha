# [BLUEPRINT] MOD-INF-005 | scripts/governance/_verify_yaml.py | §
# [MODULE] scripts.governance._verify_yaml
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
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
# [TTL] task_bound
"""Module docstring — see module-level docstring for details."""

import yaml

with open("src/zephyr/gates/_registry.yaml", encoding="utf-8") as f:
    r = yaml.safe_load(f)
gates = r.get("gates", [])
fle = [g for g in gates if g.get("category") == "fle_self_defense"]
print(f"YAML OK, {len(gates)} total gates, {len(fle)} FLE gates")
