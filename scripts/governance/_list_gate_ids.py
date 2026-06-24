# [BLUEPRINT]
# [MODULE] scripts.governance._list_gate_ids
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""Get all gate IDs from the gate_engine._GATE_FILES."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from zephyr.governance.rule_enforcement.gate_engine import GateEngine

gate_ids = sorted(GateEngine._GATE_FILES.keys())
print(f"Total: {len(gate_ids)}")
for gid in gate_ids:
    print(f'    "{gid}",')
