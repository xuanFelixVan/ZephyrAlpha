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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["TrustEngine", "TrustLevel", "TrustScoreEngine", "TrustAdjustment", "TrustRecord"]


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
    """信任评分调整记录（补全测试期望接口）。"""

    def __init__(
        self,
        agent_id: str = "",
        delta: float = 0.0,
        reason: str = "",
        timestamp: str | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.delta = delta
        self.reason = reason
        self.timestamp = timestamp


class TrustRecord:
    """Agent 信任评分记录（补全测试期望接口）。"""

    def __init__(
        self,
        agent_id: str = "",
        score: float = 0.5,
        adjustment_count: int = 0,
        history: list[TrustAdjustment] | None = None,
        last_adjusted_at: str | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.score = score
        self.adjustment_count = adjustment_count
        self.history: list[TrustAdjustment] = history if history is not None else []
        self.last_adjusted_at = last_adjusted_at or datetime.now(UTC).isoformat()


class TrustScoreEngine:
    """信任评分引擎（补全测试期望接口）。

    维护 agent -> TrustRecord 映射，支持评分调整、衰减和查询。
    """

    def __init__(
        self,
        initial_score: float = 0.5,
        decay_rate: float = 0.005,
        floor: float = 0.1,
        ceiling: float = 1.0,
    ) -> None:
        self._initial_score = initial_score
        self._decay_rate = decay_rate
        self._floor = floor
        self._ceiling = ceiling
        self._records: dict[str, TrustRecord] = {}

    @property
    def records(self) -> dict[str, TrustRecord]:
        """只读：records（Stage 4 公共化）。"""
        return self._records

    @records.setter
    def records(self, value):
        """写入：records（Stage 4 公共化）。"""
        self._records = value

    def get_or_create(self, agent_id) -> TrustRecord:
        """公共接口：get_or_create（Stage 4 公共化）。"""
        return self._get_or_create(agent_id)

    @property
    def initial_score(self):
        """只读：initial_score（Stage 4 公共化）。"""
        return self._initial_score

    @initial_score.setter
    def initial_score(self, value):
        """写入：initial_score（Stage 4 公共化）。"""
        self._initial_score = value

    @property
    def decay_rate(self):
        """只读：decay_rate（Stage 4 公共化）。"""
        return self._decay_rate

    @decay_rate.setter
    def decay_rate(self, value):
        """写入：decay_rate（Stage 4 公共化）。"""
        self._decay_rate = value

    def _get_or_create(self, agent_id: str) -> TrustRecord:
        if agent_id not in self._records:
            self._records[agent_id] = TrustRecord(
                agent_id=agent_id,
                score=self._initial_score,
                adjustment_count=0,
                history=[],
                last_adjusted_at=datetime.now(UTC).isoformat(),
            )
        return self._records[agent_id]

    def compute_score(self, agent_id: str) -> float:
        record = self._get_or_create(agent_id)
        try:
            last = datetime.fromisoformat(record.last_adjusted_at)
        except (TypeError, ValueError):
            last = datetime.now(UTC)
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        days = max(0, (datetime.now(UTC) - last).days)
        decayed = record.score * ((1 - self._decay_rate) ** days)
        return max(self._floor, min(self._ceiling, decayed))

    def adjust(self, agent_id: str, delta: float, reason: str = "") -> float:
        record = self._get_or_create(agent_id)
        current = self.compute_score(agent_id)
        new_score = max(self._floor, min(self._ceiling, current + delta))
        record.score = new_score
        record.adjustment_count += 1
        record.history.append(TrustAdjustment(agent_id=agent_id, delta=delta, reason=reason))
        record.last_adjusted_at = datetime.now(UTC).isoformat()
        return new_score

    def get_score(self, agent_id: str) -> float:
        if agent_id not in self._records:
            return self._initial_score
        return self.compute_score(agent_id)

    def get_record(self, agent_id: str) -> TrustRecord | None:
        return self._records.get(agent_id)

    def decay_all(self) -> dict[str, float]:
        results: dict[str, float] = {}
        for agent_id in list(self._records.keys()):
            results[agent_id] = self.compute_score(agent_id)
        return results
