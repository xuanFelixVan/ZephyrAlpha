# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.trackers.consequence_tracker
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/delegation/test_consequence_tracker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_consequence_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""后果追踪——记录每次修复操作对依赖方的影响."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Consequence:
    fix_id: str
    target_file: str
    impacted_files: list[str]
    timestamp: str
    rollback_available: bool = True
    status: str = "APPLIED"


@dataclass
class ConsequenceTracker:
    history: list[Consequence] = field(default_factory=list)
    rollback_stack: list[Consequence] = field(default_factory=list)

    def record(self, fix_id: str, target_file: str, impacted_files: list[str]) -> Consequence:
        c = Consequence(
            fix_id=fix_id,
            target_file=target_file,
            impacted_files=impacted_files,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self.history.append(c)
        self.rollback_stack.append(c)
        return c

    def rollback_last(self) -> dict[str, Any]:
        if not self.rollback_stack:
            return {"rolled_back": False, "reason": "stack_empty"}

        last = self.rollback_stack.pop()
        last.status = "ROLLED_BACK"
        return {
            "rolled_back": True,
            "fix_id": last.fix_id,
            "target_file": last.target_file,
            "impacted_files": last.impacted_files,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "total_fixes": len(self.history),
            "rollback_count": sum(1 for c in self.history if c.status == "ROLLED_BACK"),
            "pending_rollback": len(self.rollback_stack),
        }
