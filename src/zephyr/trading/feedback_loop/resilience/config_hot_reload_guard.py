# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.resilience.config_hot_reload_guard
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_config_hot_reload_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Config Hot-Reload Guard — v0.40.0 R498

Blindspot: FLE configuration changes at runtime (hot-reload from file watch,
remote config push, or AI session override) create inconsistent internal
state. One subsystem runs on old config, another on new config; thresholds
mismatch between detect and diagnose stages.

Risk: R498 — Mid-cycle config change causes detectors to use new thresholds
while diagnosers still use old; action dispatched based on mismatched
config versions; rollback target unknown.

Mitigation: Track config version per FLE cycle. Detect config changes between
cycles. When config changes mid-cycle, either: (a) defer change to next cycle
boundary, or (b) validate all consumers acknowledge new version before
proceeding. Flag inconsistent config states.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum


class ConfigConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    MID_CYCLE_CHANGE = "MID_CYCLE_CHANGE"
    PARTIAL_ACK = "PARTIAL_ACK"
    CONFLICT = "CONFLICT"


@dataclass
class ConfigHotReloadGuard:
    max_unacknowledged_seconds: float = 30.0
    mandatory_consumers: list[str] = field(default_factory=list)

    current_config_hash: str = ""
    config_timestamp: float = 0.0
    consumer_acks: dict[str, dict] = field(default_factory=dict)
    change_events: list[dict] = field(default_factory=list)
    cycle_active: bool = False

    def compute_config_hash(self, config_dict: dict) -> str:
        canonical = json.dumps(config_dict, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def register_config(self, config_dict: dict) -> dict:
        new_hash = self.compute_config_hash(config_dict)
        now = time.time()

        if self.cycle_active and new_hash != self.current_config_hash:
            self.change_events.append(
                {
                    "ts": now,
                    "type": ConfigConsistency.MID_CYCLE_CHANGE.value,
                    "old_hash": self.current_config_hash[:12],
                    "new_hash": new_hash[:12],
                }
            )
            return {
                "consistency": ConfigConsistency.MID_CYCLE_CHANGE.value,
                "action": "defer_to_cycle_boundary",
                "recommendation": "queue_config_change_for_next_cycle",
            }

        self.current_config_hash = new_hash
        self.config_timestamp = now
        self.consumer_acks = {}
        return {
            "consistency": ConfigConsistency.CONSISTENT.value,
            "config_hash": new_hash[:16],
            "action": "propagate_to_consumers",
        }

    def mark_cycle_start(self) -> None:
        self.cycle_active = True

    def mark_cycle_end(self) -> None:
        self.cycle_active = False

    def consumer_acknowledge(self, consumer_name: str, config_hash: str) -> dict:
        now = time.time()
        self.consumer_acks[consumer_name] = {
            "hash": config_hash,
            "acked_at": now,
        }

        consistent = all(ack["hash"] == self.current_config_hash for ack in self.consumer_acks.values())

        missing = [name for name in self.mandatory_consumers if name not in self.consumer_acks]

        if not consistent:
            self.change_events.append(
                {
                    "ts": now,
                    "type": ConfigConsistency.CONFLICT.value,
                    "consumer": consumer_name,
                    "expected": self.current_config_hash[:12],
                    "received": config_hash[:12],
                }
            )
            return {
                "consistency": ConfigConsistency.CONFLICT.value,
                "consumer": consumer_name,
                "recommendation": "reload_config_for_all_consumers",
            }

        if missing:
            return {
                "consistency": ConfigConsistency.PARTIAL_ACK.value,
                "missing_consumers": missing,
                "recommendation": "wait_for_all_acks_or_timeout",
            }

        return {
            "consistency": ConfigConsistency.CONSISTENT.value,
            "all_acknowledged": True,
            "consumer_count": len(self.consumer_acks),
        }

    def check_stale_acks(self) -> list[str]:
        now = time.time()
        stale = []
        for name, ack in self.consumer_acks.items():
            if now - ack["acked_at"] > self.max_unacknowledged_seconds:
                stale.append(name)
        return stale

    def get_config_lineage(self) -> list[dict]:
        return [
            {
                "hash": self.current_config_hash[:16] if self.current_config_hash else "none",
                "updated_at": self.config_timestamp,
                "consumers_acked": len(self.consumer_acks),
                "cycle_active": self.cycle_active,
            }
        ]

    def overall_config_health(self) -> float:
        mandatory = len(self.mandatory_consumers)
        if mandatory == 0:
            return 1.0
        acked = sum(
            1
            for name in self.mandatory_consumers
            if name in self.consumer_acks and self.consumer_acks[name]["hash"] == self.current_config_hash
        )
        return round(acked / mandatory, 3)
