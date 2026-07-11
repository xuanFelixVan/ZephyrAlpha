# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.cross_blueprint_contract_drift
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_cross_blueprint_contract_drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Cross-Blueprint Contract Drift Monitor — v0.39.0 R490

Blindspot: Blueprints define interface contracts (CT-FLE-* series), but actual
implementations drift away from declared contracts. Import paths change, function
signatures evolve, data schemas diverge — and FLE doesn't notice until runtime.

Risk: R490 — MOD-FEEDBACK_LOOP FLE depends on contracts from other blueprints that
silently changed. FLE calls fail with cryptic errors; cascading failures across
blueprint boundaries with no early warning.

Mitigation: Monitor declared vs actual interface contracts. Periodically validate
that downstream blueprints still satisfy their declared contracts. Detect when
contract signature changes without corresponding YAML update.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ContractStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    DRIFTED = "DRIFTED"
    BROKEN = "BROKEN"
    UNMONITORED = "UNMONITORED"


@dataclass
class CrossBlueprintContractDrift:
    max_staleness_days: float = 30.0
    drift_alert_threshold: int = 3

    contracts: dict[str, dict] = field(default_factory=dict)
    contract_versions: dict[str, list[dict]] = field(default_factory=dict)
    drift_events: list[dict] = field(default_factory=list)

    def register_contract(
        self,
        contract_id: str,
        source_blueprint: str,
        target_blueprint: str,
        declared_signature: str,
        interface_path: str,
    ) -> None:
        self.contracts[contract_id] = {
            "source": source_blueprint,
            "target": target_blueprint,
            "declared_signature": declared_signature,
            "interface_path": interface_path,
            "last_validated": time.time(),
            "status": ContractStatus.UNMONITORED,
        }

    def record_actual_signature(self, contract_id: str, actual_signature: str) -> dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            return {"error": "unknown_contract"}

        if contract_id not in self.contract_versions:
            self.contract_versions[contract_id] = []

        entry = {
            "ts": time.time(),
            "declared": contract["declared_signature"],
            "actual": actual_signature,
            "match": contract["declared_signature"] == actual_signature,
        }
        self.contract_versions[contract_id].append(entry)
        if len(self.contract_versions[contract_id]) > 50:
            self.contract_versions[contract_id] = self.contract_versions[contract_id][-50:]

        contract["last_validated"] = time.time()

        if entry["match"]:
            contract["status"] = ContractStatus.COMPLIANT
            return {"contract_id": contract_id, "status": ContractStatus.COMPLIANT.value, "match": True}

        contract["status"] = ContractStatus.DRIFTED
        self.drift_events.append(
            {
                "ts": time.time(),
                "contract_id": contract_id,
                "source": contract["source"],
                "target": contract["target"],
                "declared": contract["declared_signature"],
                "actual": actual_signature,
            }
        )

        return {
            "contract_id": contract_id,
            "status": ContractStatus.DRIFTED.value,
            "match": False,
            "declared": contract["declared_signature"],
            "actual": actual_signature,
            "recommendation": "update_blueprint_contract_or_fix_implementation",
        }

    def check_staleness(self) -> list[dict]:
        now = time.time()
        stale = []
        for cid, contract in self.contracts.items():
            days_since = (now - contract["last_validated"]) / 86400.0
            if days_since > self.max_staleness_days:
                stale.append(
                    {
                        "contract_id": cid,
                        "source": contract["source"],
                        "target": contract["target"],
                        "days_since_validation": round(days_since, 1),
                        "recommendation": "trigger_contract_revalidation",
                    }
                )
        return stale

    def get_drifted_contracts(self) -> list[dict]:
        return [
            {
                "contract_id": cid,
                "source": c["source"],
                "target": c["target"],
                "status": c["status"].value,
            }
            for cid, c in self.contracts.items()
            if c["status"] == ContractStatus.DRIFTED
        ]

    def get_contract_health_summary(self) -> dict:
        total = len(self.contracts)
        if total == 0:
            return {"health": 1.0, "total": 0}

        compliant = sum(1 for c in self.contracts.values() if c["status"] == ContractStatus.COMPLIANT)
        drifted = sum(1 for c in self.contracts.values() if c["status"] == ContractStatus.DRIFTED)
        unmonitored = sum(1 for c in self.contracts.values() if c["status"] == ContractStatus.UNMONITORED)
        stale = len(self.check_staleness())

        return {
            "health": round(compliant / total, 3),
            "total": total,
            "compliant": compliant,
            "drifted": drifted,
            "unmonitored": unmonitored,
            "stale_validations": stale,
            "alert": drifted >= self.drift_alert_threshold,
            "recommendation": "freeze_interface_and_sync" if drifted >= self.drift_alert_threshold else "monitor",
        }

    def force_revalidate_all(self) -> None:
        for cid in self.contracts:
            self.contracts[cid]["status"] = ContractStatus.UNMONITORED
