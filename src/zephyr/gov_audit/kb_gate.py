# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.kb_gate
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_kb_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit-trail.kb_gate — MOD-INF-020 · KB 审计门控
=================================================
蓝图 D-020-28 · KB 投毒检测 + 写入来源验证

特性
----
  - KB 投毒检测: 检测知识库写入中的投毒尝试
  - 写入来源验证: 验证 KB 写入操作的来源可信度
  - 异常模式识别: 识别可疑的 KB 修改模式
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.governance.rule_patterns import POISONING_INDICATORS  # SSoT (ARCH-033 Phase 7 修正: 合并进 rule_patterns)

_logger = logging.getLogger(__name__)

# _POISONING_INDICATORS 已迁移到 zephyr.governance.rule_patterns（ARCH-033 Phase 7 修正: 合并进 rule_patterns）


class KBWriteCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool = True
    agent_id: str = ""
    trust_score: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    risk_score: float = 0.0
    checked_at: str = ""


class PoisoningScanResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_poisoned: bool = False
    indicators_found: list[str] = Field(default_factory=list)
    risk_score: float = 0.0
    content_hash: str = ""
    scanned_at: str = ""


class KBAuditGate:
    def __init__(
        self,
        min_trust_score: float = 0.3,
        max_writes_per_hour: int = 50,
    ) -> None:
        self._min_trust_score = min_trust_score
        self._max_writes_per_hour = max_writes_per_hour
        self._write_timestamps: dict[str, list[str]] = {}

    def check_write(
        self,
        agent_id: str,
        content: str,
        trust_score: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> KBWriteCheckResult:
        reasons: list[str] = []
        risk_score = 0.0

        if trust_score < self._min_trust_score:
            reasons.append(f"Trust score {trust_score:.2f} below minimum {self._min_trust_score:.2f}")
            risk_score += 0.4

        recent_writes = self._count_recent_writes(agent_id)
        if recent_writes >= self._max_writes_per_hour:
            reasons.append(f"Write rate {recent_writes}/hr exceeds limit {self._max_writes_per_hour}/hr")
            risk_score += 0.3

        poisoning_scan = self.scan_for_poisoning(content)
        if poisoning_scan.is_poisoned:
            reasons.append(f"Poisoning indicators detected: {', '.join(poisoning_scan.indicators_found)}")
            risk_score += 0.5

        if metadata and metadata.get("source") == "external_untrusted":
            reasons.append("Write from untrusted external source")
            risk_score += 0.2

        allowed = len(reasons) == 0 and risk_score < 0.5
        now = datetime.now(UTC).isoformat()

        if allowed:
            self._record_write(agent_id, now)

        result = KBWriteCheckResult(
            allowed=allowed,
            agent_id=agent_id,
            trust_score=trust_score,
            reasons=reasons,
            risk_score=round(min(1.0, risk_score), 4),
            checked_at=now,
        )
        if not allowed:
            _logger.warning("KBAuditGate: write blocked for %s: %s", agent_id, reasons)
        return result

    def scan_for_poisoning(self, content: str) -> PoisoningScanResult:
        indicators: list[str] = []
        for pattern in POISONING_INDICATORS:
            matches = pattern.findall(content)
            if matches:
                indicators.append(pattern.pattern[:80])

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        risk_score = min(1.0, len(indicators) * 0.3)

        return PoisoningScanResult(
            is_poisoned=len(indicators) > 0,
            indicators_found=indicators,
            risk_score=round(risk_score, 4),
            content_hash=content_hash,
            scanned_at=datetime.now(UTC).isoformat(),
        )

    def _count_recent_writes(self, agent_id: str) -> int:
        now = datetime.now(UTC)
        timestamps = self._write_timestamps.get(agent_id, [])
        recent = []
        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                if (now - dt).total_seconds() < 3600:
                    recent.append(ts)
            except (ValueError, TypeError):
                continue
        self._write_timestamps[agent_id] = recent
        return len(recent)

    def _record_write(self, agent_id: str, timestamp: str) -> None:
        if agent_id not in self._write_timestamps:
            self._write_timestamps[agent_id] = []
        self._write_timestamps[agent_id].append(timestamp)
