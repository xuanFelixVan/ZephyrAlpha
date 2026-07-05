# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.bypass_recorder
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] validator.py; convergence_checker.py; escalation-engine (external)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Bypass entries MUST be deduplicated by (scenario_id, gate_id); 3rd bypass on same scenario=gate pair triggers escalation
# [MODIFY-GUARD] Bypass log format MUST match BypassEntry model; escalation trigger logic per blueprint §6.2
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] YAML write uses atomic os.replace; BypassLogNotFoundError if log dir missing
# [TESTS] tests/red_blue/test_bypass_recorder.py
# [A_module] module_id=MOD-SEC_bypass_recorder | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

import yaml

from zephyr.security.adversarial_validation.models import AttackTier, BypassEntry

logger = logging.getLogger(__name__)

__all__: list[str] = ["BypassRecorder"]

_LOG_DIR: Path = Path("data/red_blue/bypass_logs")


class BypassRecorder:
    def __init__(self, log_dir: Path | None = None) -> None:
        self._log_dir: Path = log_dir or _LOG_DIR
        os.makedirs(self._log_dir, exist_ok=True)
        self._entries: list[BypassEntry] = []

    def record_bypass(
        self,
        scenario_id: str,
        gate_id: str,
        detail: str,
        attack_payload: str = "",
        defense_response: str = "",
        tier: AttackTier = AttackTier.TIER_1,
    ) -> BypassEntry:
        existing = self._find_entry(scenario_id, gate_id)
        if existing:
            existing.count += 1
            if existing.count >= 3 and not existing.escalated:
                existing.escalated = True
                logger.warning(
                    "escalation_triggered scenario_id=%s gate_id=%s count=%d", scenario_id, gate_id, existing.count
                )
            self._write_log(existing)
            return existing

        entry = BypassEntry(
            entry_id=f"BY-{uuid.uuid4().hex[:8]}",
            scenario_id=scenario_id,
            gate_id=gate_id,
            attack_payload=attack_payload,
            defense_response=defense_response,
            root_cause=detail,
            tier=tier,
            count=1,
        )
        self._entries.append(entry)
        self._write_log(entry)
        logger.info("bypass_recorded scenario_id=%s gate_id=%s", scenario_id, gate_id)
        return entry

    def query_bypasses(self, scenario_id: str | None = None) -> list[dict]:
        entries = self._entries
        if scenario_id:
            entries = [e for e in entries if e.scenario_id == scenario_id]
        return [e.model_dump() for e in entries]

    def escalated_entries(self) -> list[BypassEntry]:
        return [e for e in self._entries if e.escalated]

    def total_bypasses(self) -> int:
        return sum(e.count for e in self._entries)

    def _find_entry(self, scenario_id: str, gate_id: str) -> BypassEntry | None:
        for e in self._entries:
            if e.scenario_id == scenario_id and e.gate_id == gate_id:
                return e
        return None

    def _write_log(self, entry: BypassEntry) -> None:
        log_file = self._log_dir / f"bypass_{entry.scenario_id}.yaml"
        existing: list[dict] = []
        if log_file.exists():
            with open(log_file, encoding="utf-8") as f:
                raw = yaml.safe_load(f)
                existing = raw if isinstance(raw, list) else []

        existing.append(
            {
                "entry_id": entry.entry_id,
                "scenario_id": entry.scenario_id,
                "gate_id": entry.gate_id,
                "attack_payload": entry.attack_payload,
                "defense_response": entry.defense_response,
                "root_cause": entry.root_cause,
                "tier": entry.tier.value,
                "count": entry.count,
                "escalated": entry.escalated,
                "occurred_at": entry.occurred_at.isoformat(),
            }
        )

        tmp = log_file.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(existing, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp, log_file)
