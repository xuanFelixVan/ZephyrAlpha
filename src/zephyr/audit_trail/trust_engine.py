# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.trust_engine

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.trust_engine — MOD-INF-020 · 渐进信任评分引擎
===========================================================
蓝图 D-020-17 · 连续信任分数 + 时间衰减 + 行为调整 + 自动降级

评分规则
--------
  - 分数范围: 0.0 ~ 1.0
  - 初始分数: 0.5
  - 正向行为: 微增 (0.01~0.05)
  - 负向行为: 微减 (0.05~0.20)
  - 时间衰减: 每天衰减 DECAY_RATE，最低不低于 FLOOR
"""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)

DEFAULT_INITIAL_SCORE: float = 0.5
DECAY_RATE: float = 0.005
FLOOR_SCORE: float = 0.1
CEILING_SCORE: float = 1.0


class TrustAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    delta: float = 0.0
    reason: str = ""
    adjusted_at: str = ""


class TrustRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    score: float = DEFAULT_INITIAL_SCORE
    last_adjusted_at: str = ""
    adjustment_count: int = 0
    history: list[TrustAdjustment] = Field(default_factory=list)


class TrustScoreEngine:
    def __init__(
        self,
        initial_score: float = DEFAULT_INITIAL_SCORE,
        decay_rate: float = DECAY_RATE,
        floor: float = FLOOR_SCORE,
        ceiling: float = CEILING_SCORE,
    ) -> None:
        self._initial_score = initial_score
        self._decay_rate = decay_rate
        self._floor = floor
        self._ceiling = ceiling
        self._records: dict[str, TrustRecord] = {}

    def compute_score(self, agent_id: str) -> float:
        record = self._get_or_create(agent_id)
        score = record.score
        if record.last_adjusted_at:
            try:
                last = datetime.fromisoformat(record.last_adjusted_at)
                if last.tzinfo is None:
                    last = last.replace(tzinfo=UTC)
                days_elapsed = (datetime.now(UTC) - last).total_seconds() / 86400.0
                if days_elapsed > 0:
                    decay = self._decay_rate * days_elapsed
                    score = max(self._floor, score - decay)
            except (ValueError, TypeError):
                pass
        return round(score, 4)

    def adjust(self, agent_id: str, delta: float, reason: str = "") -> float:
        record = self._get_or_create(agent_id)
        current = self.compute_score(agent_id)
        new_score = max(self._floor, min(self._ceiling, current + delta))
        new_score = round(new_score, 4)

        adjustment = TrustAdjustment(
            agent_id=agent_id,
            delta=delta,
            reason=reason,
            adjusted_at=datetime.now(UTC).isoformat(),
        )
        record.score = new_score
        record.last_adjusted_at = adjustment.adjusted_at
        record.adjustment_count += 1
        record.history.append(adjustment)

        self._records[agent_id] = record
        _logger.info(
            "TrustScoreEngine: %s adjusted by %+.4f (%s), %.4f -> %.4f",
            agent_id, delta, reason, current, new_score,
        )
        return new_score

    def get_score(self, agent_id: str) -> float:
        return self.compute_score(agent_id)

    def get_record(self, agent_id: str) -> TrustRecord | None:
        return self._records.get(agent_id)

    def decay_all(self) -> dict[str, float]:
        results: dict[str, float] = {}
        for agent_id in list(self._records.keys()):
            old_score = self._records[agent_id].score
            new_score = self.compute_score(agent_id)
            if new_score < old_score:
                self._records[agent_id].score = new_score
                self._records[agent_id].last_adjusted_at = datetime.now(UTC).isoformat()
            results[agent_id] = new_score
        return results

    def _get_or_create(self, agent_id: str) -> TrustRecord:
        if agent_id not in self._records:
            self._records[agent_id] = TrustRecord(
                agent_id=agent_id,
                score=self._initial_score,
                last_adjusted_at=datetime.now(UTC).isoformat(),
            )
        return self._records[agent_id]
