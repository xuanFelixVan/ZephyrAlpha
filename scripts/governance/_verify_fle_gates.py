# [BLUEPRINT] MOD-INF-005 | scripts/governance/_verify_fle_gates.py | §
# [MODULE] scripts.governance._verify_fle_gates
# [DOMAIN] D_GOVERNANCE
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

import importlib
from pathlib import Path

import yaml

registry_path = Path("src/zephyr/gates/_registry.yaml")
with open(registry_path, encoding="utf-8") as f:
    registry = yaml.safe_load(f)

fle_entries = [e for e in registry.get("gates", []) if e.get("category") == "fle_self_defense"]
print(f"Total FLE entries: {len(fle_entries)}")

loadable = 0
failed = []
for entry in fle_entries:
    gate_id = entry.get("gate_id", "")
    gate_file = entry.get("file", "")
    if not gate_file:
        failed.append(f"{gate_id}: no file path in registry")
        continue
    rel_path = gate_file.replace("../", "").replace("/", ".").replace(".py", "")
    module_path = f"zephyr.{rel_path}"
    try:
        mod = importlib.import_module(module_path)
        candidates = [a for a in dir(mod) if isinstance(getattr(mod, a), type) and not a.startswith("_")]
        if candidates:
            loadable += 1
        else:
            failed.append(f"{gate_id}: no class found in {module_path}")
    except Exception as e:
        failed.append(f"{gate_id}: import error: {type(e).__name__}: {str(e)[:80]}")

print(f"Loadable: {loadable}/{len(fle_entries)}")
if failed:
    print(f"Failed ({len(failed)}):")
    for f in failed:
        print(f"  {f}")
else:
    print("All FLE gates loadable!")
