# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.phase_planner
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_phase_planner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Phase Planner
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any


class PhaseStatus(str, Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    VERIFIED = "verified"
    BLOCKED = "blocked"


class Phase:
    def __init__(
        self, name: str, seq: int, description: str, depends_on: list[str], status: PhaseStatus = PhaseStatus.BACKLOG
    ):
        self.name = name
        self.seq = seq
        self.description = description
        self.depends_on = depends_on
        self.status = status
        self.started_at: datetime | None = None
        self.done_at: datetime | None = None
        self.verified_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "seq": self.seq,
            "description": self.description,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "done_at": self.done_at.isoformat() if self.done_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
        }

    def can_start(self, completed_phases: list[str]) -> bool:
        return all(dep in completed_phases for dep in self.depends_on)


class PhasePlanner:
    PhaseDefinitions = [
        ("scaffold-0", 1, "core model + loader + registry", []),
        ("scaffold-1", 2, "trigger router + executor", ["scaffold-0"]),
        ("scaffold-2", 3, "skill factory + file composition", ["scaffold-1"]),
        ("test-infra", 4, "testing infrastructure and CI", ["scaffold-2"]),
        ("security", 5, "skill security vetting and audit", ["test-infra"]),
        ("integrate", 6, "eight cross-module integrations", ["security"]),
        ("deploy", 7, "deployment automation", ["integrate"]),
        ("lifecycle", 8, "skill lifecycle state machine", ["deploy"]),
        ("autonomy", 9, "autonomous skill execution", ["lifecycle"]),
        ("incident", 10, "incident response and postmortem", ["autonomy"]),
        ("cold-start", 11, "cold start bootstrapping", ["incident"]),
        ("expand", 12, "skill expansion to new modules", ["cold-start"]),
        ("optimize", 13, "skill prompt optimization", ["expand"]),
        ("compliance", 14, "compliance and KYA certification", ["optimize"]),
        ("sandbox", 15, "isolated sandbox execution", ["compliance"]),
        ("verify", 16, "contract validation and verification", ["sandbox"]),
        ("cross-model", 17, "cross-model skill adaptation", ["verify"]),
        ("ontology", 18, "ontology alignment and graph sync", ["cross-model"]),
        ("prompt-eng", 19, "prompt engineering automation", ["ontology"]),
        ("resilience", 20, "idempotency + retry + fallback", ["prompt-eng"]),
        ("model-evolution", 21, "LLM upgrade impact analysis", ["resilience"]),
        ("silent-failure", 22, "silent output degradation detection", ["model-evolution"]),
        ("xai", 23, "explainability and traceability", ["silent-failure"]),
        ("calibration", 24, "confidence-accuracy alignment", ["xai"]),
        ("context-isolation", 25, "cross-skill context isolation", ["calibration"]),
        ("consensus", 26, "multi-agent consensus engine", ["context-isolation"]),
        ("cognitive", 27, "cognitive memory preservation", ["consensus"]),
        ("temperature", 28, "temperature scheduling per task", ["cognitive"]),
        ("workflow", 29, "multi-skill workflow orchestration", ["temperature"]),
        ("cache", 30, "prompt caching and cache provider", ["workflow"]),
        ("knowledge-base", 31, "skill-KB bidirectional pipeline", ["cache"]),
        ("di", 32, "dependency injection framework", ["knowledge-base"]),
        ("guardrails", 33, "runtime safety guardrails", ["di"]),
        ("team-optimization", 34, "optimal skill team selection", ["guardrails"]),
        ("discovery", 35, "automatic skill discovery from blueprints", ["team-optimization"]),
    ]

    LayerExpansion = {
        "L00_foundation": ["configuration", "logging", "health-check"],
        "L01_infrastructure": ["all current blueprints"],
        "L02_factor": ["factor-definition", "factor-computation", "factor-registry", "factor-evaluation"],
        "L04_risk": ["position-limits", "stress-testing", "stop-loss"],
        "L06_execution": ["order-router", "algorithmic-execution", "slippage-control"],
    }

    SkillProjection = {"Phase1": 8, "Phase2": 20, "Phase3": 50, "Final": 100}

    def __init__(self):
        self.phases: dict[str, Phase] = {}
        for name, seq, desc, deps in self.PhaseDefinitions:
            self.phases[name] = Phase(name, seq, desc, deps)

    def get_phase(self, name: str) -> Phase:
        return self.phases[name]

    def set_status(self, name: str, status: PhaseStatus) -> Phase:
        phase = self.phases[name]
        phase.status = status
        now = datetime.now(UTC)
        if status == PhaseStatus.IN_PROGRESS:
            phase.started_at = now
        elif status == PhaseStatus.DONE:
            phase.done_at = now
        elif status == PhaseStatus.VERIFIED:
            phase.verified_at = now
        return phase

    def get_ready_phases(self) -> list[str]:
        done = [n for n, p in self.phases.items() if p.status in (PhaseStatus.DONE, PhaseStatus.VERIFIED)]
        return [n for n, p in self.phases.items() if p.status == PhaseStatus.BACKLOG and p.can_start(done)]

    def all_phases(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self.phases.values()]

    def phase_summary(self) -> dict[str, int]:
        counts = {s.value: 0 for s in PhaseStatus}
        for p in self.phases.values():
            counts[p.status.value] += 1
        return counts

    def current_projection(self) -> dict[str, int]:
        done = sum(1 for p in self.phases.values() if p.status in (PhaseStatus.DONE, PhaseStatus.VERIFIED))
        if done <= 6:
            return self.SkillProjection["Phase1"]
        if done <= 13:
            return self.SkillProjection["Phase2"]
        if done <= 25:
            return self.SkillProjection["Phase3"]
        return self.SkillProjection["Final"]
