# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.state_migration_validator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_state_migration_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""State Migration Validator — v0.40.0 R497

Blindspot: FLE persists runtime state (checkpoints, baselines, event-store)
across restarts and version upgrades. But _v0.39 state -> _v0.40 code path
is never tested. Old persisted state may be incompatible with new code.

Risk: R497 — FLE v0.40 starts, loads v0.39 persisted state, silently fails
or produces corrupted baselines. "We upgraded, now everything is broken."

Mitigation: Validate state migration at upgrade time. Load old persisted state
with new code. Compare computed outputs against pre-upgrade snapshot. Flag
any divergence. Maintain migration compatibility map.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class MigrationResult(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    MIGRATED = "MIGRATED"
    PARTIAL = "PARTIAL"
    INCOMPATIBLE = "INCOMPATIBLE"


@dataclass
class StateMigrationValidator:
    max_divergence_pct: float = 1.0
    min_baseline_samples: int = 100

    state_snapshot_hashes: dict[str, str] = field(default_factory=dict)
    migration_results: list[dict] = field(default_factory=list)
    compatibility_map: dict[str, dict[str, MigrationResult]] = field(default_factory=dict)

    def snapshot(self, name: str, state_bytes: bytes) -> str:
        state_hash = hashlib.sha256(state_bytes).hexdigest()
        self.state_snapshot_hashes[name] = state_hash
        return state_hash[:16]

    def validate_migration(
        self,
        from_version: str,
        to_version: str,
        state_name: str,
        old_output: dict,
        new_output: dict,
    ) -> dict:
        key = f"{from_version}->{to_version}"
        diverged_fields = []

        all_keys = set(old_output.keys()) | set(new_output.keys())
        for field in sorted(all_keys):
            old_val = old_output.get(field)
            new_val = new_output.get(field)
            if old_val != new_val:
                diverged_fields.append(field)

        divergence_pct = 100.0 * len(diverged_fields) / max(len(all_keys), 1)

        if divergence_pct == 0:
            result = MigrationResult.COMPATIBLE
        elif divergence_pct < self.max_divergence_pct:
            result = MigrationResult.MIGRATED
        elif divergence_pct < self.max_divergence_pct * 3:
            result = MigrationResult.PARTIAL
        else:
            result = MigrationResult.INCOMPATIBLE

        self.compatibility_map.setdefault(key, {})[state_name] = result

        entry = {
            "ts": time.time(),
            "from_version": from_version,
            "to_version": to_version,
            "state_name": state_name,
            "result": result.value,
            "divergence_pct": round(divergence_pct, 2),
            "diverged_fields": diverged_fields[:10],
            "total_fields": len(all_keys),
        }
        self.migration_results.append(entry)

        return {
            "from": from_version,
            "to": to_version,
            "state": state_name,
            "result": result.value,
            "divergence_pct": round(divergence_pct, 2),
            "diverged_count": len(diverged_fields),
            "recommendation": (
                "rollback_and_investigate"
                if result == MigrationResult.INCOMPATIBLE
                else "review_diverged_fields"
                if result == MigrationResult.PARTIAL
                else "proceed"
                if result == MigrationResult.COMPATIBLE
                else "proceed_with_caution"
            ),
        }

    def can_migrate_safely(self, from_version: str, to_version: str) -> dict:
        key = f"{from_version}->{to_version}"
        results = self.compatibility_map.get(key, {})
        if not results:
            return {"safe": False, "reason": "no_migration_tested", "recommendation": "run_migration_dry_run"}

        incompatible = sum(1 for r in results.values() if r == MigrationResult.INCOMPATIBLE)
        partial = sum(1 for r in results.values() if r == MigrationResult.PARTIAL)

        return {
            "safe": incompatible == 0,
            "total_states": len(results),
            "incompatible": incompatible,
            "partial": partial,
            "compatible": len(results) - incompatible - partial,
            "recommendation": (
                "block_upgrade" if incompatible > 0 else "upgrade_with_monitoring" if partial > 0 else "safe_to_upgrade"
            ),
        }

    def get_migration_history(self, from_version: str, to_version: str) -> list[dict]:
        key = f"{from_version}->{to_version}"
        return [r for r in self.migration_results if f"{r['from_version']}->{r['to_version']}" == key]

    def overall_migration_health(self) -> float:
        if not self.migration_results:
            return 1.0
        safe = sum(
            1
            for r in self.migration_results
            if r["result"] in (MigrationResult.COMPATIBLE.value, MigrationResult.MIGRATED.value)
        )
        return round(safe / len(self.migration_results), 3)
