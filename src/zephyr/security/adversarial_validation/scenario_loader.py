# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.2 + §16 Phase 0
# [MODULE] zephyr.security.adversarial_validation.scenario_loader
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] validator.py; attack_registry.py; game_day_runner.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MUST load from _scenario-registry.yaml; parsed scenarios MUST validate against AttackScenario model
# [MODIFY-GUARD] Adding new fields to _scenario-registry.yaml MUST update AttackScenario model and this loader
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FileNotFoundError if _scenario-registry.yaml missing; Pydantic ValidationError on malformed scenarios
# [TESTS] tests/red_blue/test_scenario_loader.py
# [A_module] module_id=MOD-SEC_scenario_loader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from zephyr.security.adversarial_validation.models import (
    AttackScenario,
    AttackTier,
    BlastRadiusLevel,
    DefenseSpec,
    InjectionSpec,
    ScenarioSource,
    Severity,
    SteadyStateSpec,
)

logger = logging.getLogger(__name__)

__all__: list[str] = ["ScenarioLoader"]

_REGISTRY_PATH: Path = Path(__file__).parent / "_scenario-registry.yaml"


def _map_tier(raw: str) -> AttackTier:
    return AttackTier.from_label(raw)


def _map_severity(raw: str) -> Severity:
    raw_upper = raw.upper()
    for s in Severity:
        if s.value == raw_upper:
            return s
    return Severity.MEDIUM


def _map_blast_radius(raw: str | None) -> BlastRadiusLevel:
    if not raw:
        return BlastRadiusLevel.FILE
    mapping: dict[str, BlastRadiusLevel] = {
        "FILE": BlastRadiusLevel.FILE,
        "MODULE": BlastRadiusLevel.MODULE,
        "CROSS_MODULE": BlastRadiusLevel.CROSS_MODULE,
        "SYSTEM": BlastRadiusLevel.SYSTEM,
    }
    return mapping.get(raw.upper(), BlastRadiusLevel.FILE)


class ScenarioLoader:
    def __init__(self, registry_path: Path | None = None) -> None:
        self._registry_path: Path = registry_path or _REGISTRY_PATH
        self._scenarios: list[AttackScenario] = []
        self._by_id: dict[str, AttackScenario] = {}
        self._loaded: bool = False

    @property
    def scenario_count(self) -> int:
        if not self._loaded:
            self.load()
        return len(self._scenarios)

    def load(self) -> list[AttackScenario]:
        if self._loaded:
            return self._scenarios

        if not self._registry_path.exists():
            raise FileNotFoundError(f"Scenario registry not found: {self._registry_path}")

        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        raw_scenarios: list[dict] = raw.get("scenarios", [])
        self._scenarios = []
        self._by_id = {}

        for entry in raw_scenarios:
            scenario = AttackScenario(
                scenario_id=entry.get("scenario_id", ""),
                name=entry.get("name", ""),
                description=entry.get("description", ""),
                tier=_map_tier(entry.get("tier", "L1")),
                severity=_map_severity(entry.get("severity", "MEDIUM")),
                injection=InjectionSpec(
                    vector=entry.get("injection_vector", ""),
                    target_module=entry.get("target_module", ""),
                    payload=entry.get("payload", ""),
                ),
                expected_defense=DefenseSpec(
                    gate_id=entry.get("defense", ""),
                    expected=entry.get("defense", ""),
                ),
                steady_state=SteadyStateSpec(
                    verify_command=entry.get("steady_state_verification", ""),
                ),
                blast_radius=_map_blast_radius(entry.get("blast_radius")),
                auto_cleanup=entry.get("auto_cleanup", True),
                realism_score=float(entry.get("realism_score", 1.0)),
                constitution_ref=entry.get("constitution_ref"),
                source=ScenarioSource.BUILTIN,
                status=entry.get("status", "active"),
            )
            self._scenarios.append(scenario)
            self._by_id[scenario.scenario_id] = scenario

        self._loaded = True
        logger.info("scenarios_loaded count=%d", len(self._scenarios))
        return self._scenarios

    def get(self, scenario_id: str) -> AttackScenario | None:
        if not self._loaded:
            self.load()
        return self._by_id.get(scenario_id)

    def list_by_tier(self, tier: AttackTier) -> list[AttackScenario]:
        if not self._loaded:
            self.load()
        return [s for s in self._scenarios if s.tier == tier]

    def list_by_target(self, target_module: str) -> list[AttackScenario]:
        if not self._loaded:
            self.load()
        return [s for s in self._scenarios if s.injection.target_module == target_module]

    def list_by_severity(self, severity: Severity) -> list[AttackScenario]:
        if not self._loaded:
            self.load()
        return [s for s in self._scenarios if s.severity == severity]

    def list_active(self) -> list[AttackScenario]:
        if not self._loaded:
            self.load()
        return [s for s in self._scenarios if s.status == "active"]

    def list_all(self) -> list[AttackScenario]:
        if not self._loaded:
            self.load()
        return list(self._scenarios)

    def tier_counts(self) -> dict[AttackTier, int]:
        if not self._loaded:
            self.load()
        counts: dict[AttackTier, int] = {}
        for s in self._scenarios:
            counts[s.tier] = counts.get(s.tier, 0) + 1
        return counts

    def reload(self) -> list[AttackScenario]:
        self._loaded = False
        self._scenarios = []
        self._by_id = {}
        return self.load()
