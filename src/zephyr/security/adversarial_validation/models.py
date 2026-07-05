# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.2
# [MODULE] zephyr.security.adversarial_validation.models
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] scenario_loader.py; validator.py; defense_runner.py; bypass_recorder.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AttackScenario fields MUST align with _scenario-registry.yaml keys; RedBlueReport fields per blueprint §4.2 contract
# [MODIFY-GUARD] Adding fields to RedBlueReport is BREAKING — must follow blueprint §4.6 contract version rules
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] Pydantic ValidationError on malformed scenarios; ValueError on invalid tier/severity
# [TESTS] tests/red_blue/test_models.py
# [A_module] module_id=MOD-SEC_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field

__all__: list[str] = [
    "AttackScenario",
    "AttackTier",
    "BlastRadiusLevel",
    "BypassEntry",
    "ConvergenceResult",
    "DefenseResult",
    "DefenseSpec",
    "GameDayResult",
    "InjectionResult",
    "InjectionSpec",
    "InjectionType",
    "RedBlueReport",
    "ResultClass",
    "ScenarioResult",
    "ScenarioSource",
    "Severity",
    "SteadyStateSpec",
    "SteadyStateSummary",
]


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AttackTier(str, Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"
    TIER_4 = "TIER_4"
    TIER_5 = "TIER_5"
    TIER_6 = "TIER_6"
    TIER_7 = "TIER_7"

    @classmethod
    def from_label(cls, label: str) -> AttackTier:
        mapping: dict[str, AttackTier] = {
            "L1": cls.TIER_1,
            "L2": cls.TIER_2,
            "L3": cls.TIER_3,
            "L4": cls.TIER_4,
            "L5": cls.TIER_5,
            "L6": cls.TIER_6,
            "L7": cls.TIER_7,
        }
        if label.upper() in mapping:
            return mapping[label.upper()]
        raise ValueError(f"Unknown tier label: {label}")


class BlastRadiusLevel(str, Enum):
    FILE = "FILE"
    MODULE = "MODULE"
    CROSS_MODULE = "CROSS_MODULE"
    SYSTEM = "SYSTEM"

    @property
    def risk_rank(self) -> int:
        _rank = {self.FILE: 1, self.MODULE: 2, self.CROSS_MODULE: 3, self.SYSTEM: 4}
        return _rank[self]


class ResultClass(str, Enum):
    BLOCKED = "BLOCKED"
    BYPASSED = "BYPASSED"
    INFRA_COMPROMISED = "INFRA_COMPROMISED"
    TEST_ERROR = "TEST_ERROR"


class ScenarioSource(str, Enum):
    BUILTIN = "builtin"
    AI_GENERATED = "ai_generated"
    COMMUNITY = "community"
    BYPASS_DERIVED = "bypass_derived"


class InjectionType(str, Enum):
    LATENCY = "latency"
    ERROR = "error"
    CRASH = "crash"
    EXIT_CODE = "exit_code"


class InjectionSpec(BaseModel):
    vector: str = ""
    target_module: str = ""
    payload: str = ""
    parameters: dict = Field(default_factory=dict)


class DefenseSpec(BaseModel):
    gate_id: str = ""
    expected: str = ""
    check_runner: str = ""


class SteadyStateSpec(BaseModel):
    domain: str = "compliance"
    metric: str = ""
    baseline: float = 0.0
    threshold_pct: float = 5.0
    verify_command: str = ""


class SteadyStateSummary(BaseModel):
    total_metrics: int = 0
    within_threshold: int = 0
    drifted: int = 0
    drift_rate: float = 0.0


class AttackScenario(BaseModel):
    scenario_id: str
    name: str
    description: str = ""
    tier: AttackTier = AttackTier.TIER_1
    severity: Severity = Severity.MEDIUM
    owasp_asi_mapping: str | None = None
    mitre_atlas_mapping: str | None = None
    injection: InjectionSpec = Field(default_factory=InjectionSpec)
    expected_defense: DefenseSpec = Field(default_factory=DefenseSpec)
    steady_state: SteadyStateSpec = Field(default_factory=SteadyStateSpec)
    blast_radius: BlastRadiusLevel = BlastRadiusLevel.FILE
    auto_cleanup: bool = True
    realism_score: float = Field(default=1.0, ge=0.0, le=1.0)
    constitution_ref: str | None = None
    source: ScenarioSource = ScenarioSource.BUILTIN
    status: str = "active"


class ScenarioResult(BaseModel):
    scenario_id: str
    name: str
    tier: AttackTier
    result: ResultClass
    gate_id: str = ""
    detail: str = ""
    duration_ms: float = 0.0
    bypass_entry: str | None = None
    steady_state_ok: bool = True


class BypassEntry(BaseModel):
    entry_id: str
    scenario_id: str
    gate_id: str
    attack_payload: str = ""
    defense_response: str = ""
    root_cause: str = ""
    tier: AttackTier = AttackTier.TIER_1
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    count: int = 1
    escalated: bool = False


class RedBlueReport(BaseModel):
    session_id: str
    total: int = 0
    blocked: int = 0
    bypassed: int = 0
    blocked_rate: float = 0.0
    scenarios: list[ScenarioResult] = Field(default_factory=list)
    new_bypass_entries: int = 0
    new_constitution_articles: int = 0
    cleanup_verified: bool = False
    steady_state_summary: SteadyStateSummary = Field(default_factory=SteadyStateSummary)
    blast_radius_used: BlastRadiusLevel = BlastRadiusLevel.FILE
    duration_ms: float = 0.0
    circuit_breaker_open: bool = False

    def compute_blocked_rate(self) -> float:
        if self.total == 0:
            return 0.0
        self.blocked_rate = round(self.blocked / self.total, 4)
        return self.blocked_rate


class ConvergenceResult(BaseModel):
    status: str = "CONTINUE"
    bypass_count: int = 0
    total_attacks: int = 0
    previous_bypass_count: int = 0
    trend: str = "stable"
    rounds_since_improvement: int = 0


class DefenseResult(BaseModel):
    passed: bool
    gate_id: str
    detail: str


class GameDayResult(BaseModel):
    total_attacks: int = 0
    bypasses: int = 0
    passed: int = 0
    report: RedBlueReport | None = None


class InjectionResult(BaseModel):
    injection_type: InjectionType
    target: str = ""
    effect: str = "injected"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    error: str | None = None
    recovered: bool = False
