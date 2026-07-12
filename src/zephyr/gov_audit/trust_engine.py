# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] zephyr.gov_audit.trust_engine
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.integrity; pipeline_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 信任评分基于历史审计结果和Merkle校验
# [MODIFY-GUARD] 评分算法变更必须同步 trust_bridge.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 评分失败返回trust_level=UNKNOWN
# [TESTS] tests/audit-orchestrator/test_trust_engine.py
# [A_module] module_id=MOD-GOV_trust_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["TrustEngine", "TrustLevel"]


class TrustLevel(str, Enum):
    UNKNOWN = "UNKNOWN"
    UNTRUSTED = "UNTRUSTED"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERIFIED = "VERIFIED"


class TrustEngine:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self._baseline: dict[str, Any] = {}

    def calculate(self, audit_results: list[dict[str, Any]]) -> dict[str, Any]:
        if not audit_results:
            return {"trust_level": TrustLevel.UNKNOWN.value, "score": 0.0, "confidence": 0.0}

        total = len(audit_results)
        passed = sum(1 for r in audit_results if r.get("pass", False))
        pass_rate = passed / total if total > 0 else 0.0

        severity_scores = {"RED": -2, "YELLOW": -1, "GREEN": 1}
        issue_score = sum(severity_scores.get(r.get("severity", "GREEN"), 0) for r in audit_results) / max(1, total)

        raw_score = (pass_rate * 0.6) + ((issue_score + 2) / 4 * 0.4)
        clamped_score = max(0.0, min(1.0, raw_score))

        if clamped_score >= 0.9:
            level = TrustLevel.VERIFIED
        elif clamped_score >= 0.7:
            level = TrustLevel.HIGH
        elif clamped_score >= 0.5:
            level = TrustLevel.MEDIUM
        elif clamped_score >= 0.3:
            level = TrustLevel.LOW
        else:
            level = TrustLevel.UNTRUSTED

        return {
            "trust_level": level.value,
            "score": round(clamped_score, 4),
            "confidence": round(pass_rate, 4),
            "total_checks": total,
            "passed": passed,
        }

    def update_history(self, result: dict[str, Any]) -> None:
        self._history.append(result)
        if len(self._history) > 100:
            self._history = self._history[-100:]

    def trend(self) -> dict[str, Any]:
        if len(self._history) < 2:
            return {"direction": "stable", "change": 0.0}

        recent = self._history[-10:]
        older = self._history[-20:-10]
        recent_avg = sum(r.get("score", 0) for r in recent) / max(1, len(recent))
        older_avg = sum(r.get("score", 0) for r in older) / max(1, len(older)) if older else recent_avg

        change = recent_avg - older_avg
        if change > 0.1:
            direction = "improving"
        elif change < -0.1:
            direction = "degrading"
        else:
            direction = "stable"

        return {"direction": direction, "change": round(change, 4)}


class TrustAdjustment:
    def __init__(self, entity: str = "", delta: float = 0.0, reason: str = "", timestamp: str | None = None) -> None:
        self.entity = entity
        self.delta = delta
        self.reason = reason
        self.timestamp = timestamp


class TrustRecord:
    def __init__(self, entity: str = "", trust_score: float = 1.0, last_updated: str | None = None, history: list[dict[str, Any]] | None = None) -> None:
        self.entity = entity
        self.trust_score = trust_score
        self.last_updated = last_updated
        self.history = history or []


class TrustScoreEngine:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def compute_score(self, entity: str, history: list[dict[str, Any]] | None = None) -> float:
        return 1.0

    def adjust(self, entity: str, delta: float) -> TrustAdjustment:
        return TrustAdjustment(entity=entity, delta=delta)
