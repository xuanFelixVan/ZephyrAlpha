# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.security_governance.poison_cascade_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-RES_poison_cascade_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class PoisonEvent:
    source: str
    target: str
    infection_type: str
    tokens_transferred: int
    suspicion_score: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class PoisonReport:
    total_events: int
    confirmed_poison: int
    suspicion_score: float
    root_causes: list[str]
    advice: str


class PoisonCascadeDetector:
    POISON_SIGNATURES: list[str] = [
        "ignore_previous_instructions",
        "system_role_new",
        "budget_policy_override",
        "degradation_bypass",
        "trust_ring_disable",
    ]

    def __init__(self, suspicion_threshold: float = 0.7):
        self._suspicion_threshold = suspicion_threshold
        self._events: list[PoisonEvent] = []
        self._infections: dict[str, int] = defaultdict(int)

    def scan(self, source: str, target: str, content: str, tokens: int = 0) -> PoisonEvent:
        score = self._compute_suspicion(content)
        sig_found = self._detect_signature(content)

        event = PoisonEvent(
            source=source,
            target=target,
            infection_type=sig_found or "generic",
            tokens_transferred=tokens,
            suspicion_score=score,
        )
        self._events.append(event)

        if score > self._suspicion_threshold:
            self._infections[source] += 1

        return event

    def _compute_suspicion(self, content: str) -> float:
        text = content.lower()
        hits = sum(1 for sig in self.POISON_SIGNATURES if sig in text)
        if hits >= 3:
            return 0.95
        if hits >= 2:
            return 0.8
        if hits >= 1:
            return 0.5

        if "override" in text or "bypass" in text:
            if "budget" in text or "policy" in text:
                return 0.7
        return 0.1

    def _detect_signature(self, content: str) -> str:
        for sig in self.POISON_SIGNATURES:
            if sig in content.lower():
                return sig
        return ""

    def report(self) -> PoisonReport:
        confirmed = sum(1 for e in self._events if e.suspicion_score > self._suspicion_threshold)
        avg_score = sum(e.suspicion_score for e in self._events) / max(len(self._events), 1)

        root_causes = sorted(self._infections, key=lambda k: self._infections[k], reverse=True)[:3]

        if confirmed > 0:
            advice = f"检测到 {confirmed} 次疑似投毒事件，来源: {', '.join(root_causes)}"
        else:
            advice = "未检测到投毒事件"

        return PoisonReport(
            total_events=len(self._events),
            confirmed_poison=confirmed,
            suspicion_score=round(avg_score, 4),
            root_causes=root_causes,
            advice=advice,
        )

    def recent_events(self, n: int = 20) -> list[PoisonEvent]:
        return self._events[-n:]

    def clear(self) -> None:
        self._events.clear()
        self._infections.clear()
