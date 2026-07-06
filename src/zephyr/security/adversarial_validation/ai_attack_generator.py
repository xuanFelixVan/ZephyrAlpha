# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §5.2 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.ai_attack_generator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] game_day_runner.py; cold_start.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Generates new attack payloads from bypass history; mutation strategies: payload_variation/scenario_combination/vector_permutation
# [MODIFY-GUARD] Adding mutation strategies MUST update MUTATION_STRATEGIES; generated scenarios MUST validate against AttackScenario model
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AttackGenerationError on invalid payload generation
# [TESTS] tests/red_blue/test_ai_attack_generator.py
# [A_module] module_id=MOD-SEC_ai_attack_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import os
import uuid
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

__all__: list[str] = ["AIAttackGenerator", "AttackGenerationError"]

_REGISTRY_PATH: Path = Path(__file__).parent / "_scenario-registry.yaml"

MUTATION_STRATEGIES: Final[list[str]] = [
    "payload_variation",
    "scenario_combination",
    "vector_permutation",
    "blast_radius_escalation",
]

VECTOR_POOL: Final[list[str]] = [
    "prompt_injection_filter.scan",
    "immutable_core.verify_roles",
    "circuit_breaker.hard_check",
    "drift_engine.reconcile",
    "audit-trail.verify_chain",
    "budget_engine.pre_flight",
    "freeze_manifest.validate",
    "mcp_auth.verify_tool_access",
    "session_audit.verify",
    "kb.verify_provenance",
    "gates_registry.verify_all",
    "route_manifest.validate",
    "lock_registry.verify_atomicity",
    "secrets.scan_all",
]


class AttackGenerationError(RuntimeError):
    error_code = "ZA-SC-0014"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class AIAttackGenerator:
    def __init__(self) -> None:
        self._registry_path = _REGISTRY_PATH
        self._generated: list[str] = []

    def generate_from_bypasses(self, bypasses: list[dict]) -> list[str]:
        if not bypasses:
            return []

        scenario_ids: list[str] = []
        strategies = self._select_strategies(len(bypasses))

        for bypass in bypasses:
            scenario_id = self._mutate_scenario(bypass)
            if scenario_id:
                scenario_ids.append(scenario_id)
                self._generated.append(scenario_id)

        logger.info("ai_attack_generated count=%d strategies=%s", len(scenario_ids), strategies)
        return scenario_ids

    def _select_strategies(self, bypass_count: int) -> list[str]:
        if bypass_count <= 1:
            return ["payload_variation"]
        elif bypass_count <= 3:
            return ["payload_variation", "scenario_combination"]
        else:
            return MUTATION_STRATEGIES

    def _mutate_scenario(self, bypass: dict) -> str | None:
        scenario_id = f"RB-AI-{uuid.uuid4().hex[:8]}"
        original_vector = bypass.get("attack_payload", "")
        gate_id = bypass.get("gate_id", "")

        mutated_vector = f"{original_vector}.v2.{uuid.uuid4().hex[:4]}"

        new_scenario = {
            "scenario_id": scenario_id,
            "name": f"AI-Generated: Bypass variant of {gate_id}",
            "description": f"Auto-generated from bypass {bypass.get('entry_id', '')} at gate {gate_id}",
            "tier": "L2",
            "severity": bypass.get("tier", "L1") if bypass.get("tier") != "TIER_1" else "HIGH",
            "injection_vector": mutated_vector,
            "defense": gate_id,
            "blast_radius": "MODULE",
            "auto_cleanup": True,
            "realism_score": 0.8,
            "source": "ai_generated",
            "status": "active",
            "constitution_ref": "CONST-001",
        }

        self._append_to_registry(new_scenario)
        return scenario_id

    def generate_from_known_patterns(self) -> list[str]:
        scenario_ids: list[str] = []
        used_vectors = self._existing_vectors()

        for vector in VECTOR_POOL:
            if vector in used_vectors:
                continue
            scenario_id = f"RB-AI-{uuid.uuid4().hex[:8]}"
            new_scenario = {
                "scenario_id": scenario_id,
                "name": f"AI-Generated: Variation of {vector}",
                "description": f"Auto-generated scenario targeting {vector}",
                "tier": "L1",
                "severity": "MEDIUM",
                "injection_vector": f"{vector}.ai_variant",
                "defense": vector,
                "blast_radius": "FILE",
                "auto_cleanup": True,
                "realism_score": 0.6,
                "source": "ai_generated",
                "status": "active",
            }
            self._append_to_registry(new_scenario)
            scenario_ids.append(scenario_id)
            self._generated.append(scenario_id)
            if len(scenario_ids) >= 5:
                break

        return scenario_ids

    def _existing_vectors(self) -> set[str]:
        if not self._registry_path.exists():
            return set()
        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return {s.get("injection_vector", "") for s in raw.get("scenarios", [])}

    def _append_to_registry(self, scenario: dict) -> None:
        if self._registry_path.exists():
            with open(self._registry_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        else:
            raw = {"scenarios": []}

        raw.setdefault("scenarios", []).append(scenario)

        tmp = self._registry_path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(raw, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp, self._registry_path)

    def generated_scenarios(self) -> list[str]:
        return list(self._generated)
