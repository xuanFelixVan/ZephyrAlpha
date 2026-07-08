# [BLUEPRINT] (migrated from MOD-INF-021 by ARCH-039 P1, target domain=D_GOVERNANCE)
# [MODULE] zephyr.governance.intelligence_governance.continuous_trust
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
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
# [A_module] module_id=MOD-INF_continuous_trust | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Continuous Trust Ledger — 持续信任评估引擎。

依据：
    蓝图 MOD-INF-021 §6.15 B95 + 决策 D-021-26 + Risks R15-R20
    任务卡 TASK-INF-0263

功能：
    - continuous_trust_ledger 记录 trust_delta (±0.1)
    - trust-score -> tier 分级自主 (tier 0/1/2)
    - trust > 0.8 -> tier 2 auto-revert
    - trust < 0.5 -> tier 1 propose-only
    - trust < -0.3 -> tier 0 read-only + human
    - 涵盖 R15-R20 AI agent 信任安全风险
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TrustEntry:
    entry_id: str
    timestamp_utc: str
    trust_delta: float
    reason: str
    operation: str
    commit_sha: str = ""
    execution_id: str = ""


@dataclass
class TrustScore:
    score: float
    tier: int
    total_entries: int
    positive_deltas: int
    negative_deltas: int
    last_updated: str

    @classmethod
    def from_ledger(cls, entries: list[TrustEntry]) -> TrustScore:
        if not entries:
            return cls(
                score=0.5,
                tier=1,
                total_entries=0,
                positive_deltas=0,
                negative_deltas=0,
                last_updated=datetime.now(UTC).isoformat(),
            )

        score = 0.5
        positive = 0
        negative = 0

        for entry in entries:
            score += entry.trust_delta
            if entry.trust_delta > 0:
                positive += 1
            elif entry.trust_delta < 0:
                negative += 1

        score = max(-1.0, min(1.0, score))

        if score > 0.8:
            tier = 2
        elif score > 0.5 or score > -0.3:
            tier = 1
        else:
            tier = 0

        return cls(
            score=round(score, 4),
            tier=tier,
            total_entries=len(entries),
            positive_deltas=positive,
            negative_deltas=negative,
            last_updated=entries[-1].timestamp_utc,
        )


@dataclass
class TrustTierPerms:
    tier: int
    can_auto_revert: bool = False
    can_propose_rollback: bool = False
    can_discard_uncommitted: bool = False
    can_read_state: bool = True
    needs_human_approval: bool = True

    @classmethod
    def from_tier(cls, tier: int) -> TrustTierPerms:
        if tier == 2:
            return cls(
                tier=2,
                can_auto_revert=True,
                can_propose_rollback=True,
                can_discard_uncommitted=True,
                can_read_state=True,
                needs_human_approval=False,
            )
        if tier == 1:
            return cls(
                tier=1,
                can_auto_revert=False,
                can_propose_rollback=True,
                can_discard_uncommitted=True,
                can_read_state=True,
                needs_human_approval=True,
            )
        return cls(
            tier=0,
            can_auto_revert=False,
            can_propose_rollback=False,
            can_discard_uncommitted=False,
            can_read_state=True,
            needs_human_approval=True,
        )


class ContinuousTrust:
    POSITIVE_DELTA = 0.1
    NEGATIVE_DELTA = -0.1
    CRITICAL_FAILURE_DELTA = -0.3
    FALSE_POSITIVE_DELTA = -0.05
    SUCCESSFUL_RECOVERY_DELTA = 0.15

    def __init__(self, ledger_dir: Path | None = None) -> None:
        self._ledger_dir = ledger_dir or Path("data/rollback/trust")
        self._ledger_path = self._ledger_dir / "continuous_trust_ledger.jsonl"
        self._score_path = self._ledger_dir / "trust-score.json"

    def record_trust_event(
        self,
        trust_delta: float,
        reason: str,
        operation: str = "rollback",
        commit_sha: str = "",
        execution_id: str = "",
    ) -> TrustEntry:
        entry = TrustEntry(
            entry_id=f"TRUST-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{os.urandom(4).hex()}",
            timestamp_utc=datetime.now(UTC).isoformat(),
            trust_delta=trust_delta,
            reason=reason,
            operation=operation,
            commit_sha=commit_sha,
            execution_id=execution_id,
        )

        self._ledger_dir.mkdir(parents=True, exist_ok=True)

        line = json.dumps(
            {
                "entry_id": entry.entry_id,
                "timestamp_utc": entry.timestamp_utc,
                "trust_delta": entry.trust_delta,
                "reason": entry.reason,
                "operation": entry.operation,
                "commit_sha": entry.commit_sha,
                "execution_id": entry.execution_id,
            },
            ensure_ascii=False,
        )

        with open(self._ledger_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        self._recompute_score()

        return entry

    def successful_rollback(self, operation: str = "rollback", commit_sha: str = "") -> TrustEntry:
        return self.record_trust_event(
            trust_delta=self.POSITIVE_DELTA,
            reason=f"Successful {operation} operation",
            operation=operation,
            commit_sha=commit_sha,
        )

    def failed_rollback(self, operation: str = "rollback", commit_sha: str = "") -> TrustEntry:
        return self.record_trust_event(
            trust_delta=self.NEGATIVE_DELTA,
            reason=f"Failed {operation} operation",
            operation=operation,
            commit_sha=commit_sha,
        )

    def critical_failure(self, operation: str = "rollback", reason: str = "") -> TrustEntry:
        return self.record_trust_event(
            trust_delta=self.CRITICAL_FAILURE_DELTA,
            reason=f"CRITICAL: {reason}" if reason else f"Critical failure in {operation}",
            operation=operation,
        )

    def false_positive_trigger(self) -> TrustEntry:
        return self.record_trust_event(
            trust_delta=self.FALSE_POSITIVE_DELTA,
            reason="False positive rollback trigger",
            operation="false_positive",
        )

    def successful_recovery(self, operation: str = "recovery") -> TrustEntry:
        return self.record_trust_event(
            trust_delta=self.SUCCESSFUL_RECOVERY_DELTA,
            reason=f"Successful recovery via {operation}",
            operation=operation,
        )

    def get_score(self) -> TrustScore:
        if self._score_path.exists():
            try:
                data = json.loads(self._score_path.read_text(encoding="utf-8"))
                return TrustScore(
                    score=data["score"],
                    tier=data["tier"],
                    total_entries=data["total_entries"],
                    positive_deltas=data.get("positive_deltas", 0),
                    negative_deltas=data.get("negative_deltas", 0),
                    last_updated=data.get("last_updated", ""),
                )
            except (json.JSONDecodeError, KeyError):
                pass

        return self._recompute_score()

    def get_permissions(self) -> TrustTierPerms:
        score = self.get_score()
        return TrustTierPerms.from_tier(score.tier)

    def can_auto_revert(self) -> bool:
        return self.get_permissions().can_auto_revert

    def needs_human_approval(self) -> bool:
        return self.get_score().tier < 2

    def trust_ledger_summary(self) -> dict[str, Any]:
        entries = self._load_entries()
        score = TrustScore.from_ledger(entries)
        perms = TrustTierPerms.from_tier(score.tier)

        return {
            "trust-score": score.score,
            "tier": score.tier,
            "total_entries": score.total_entries,
            "positive_events": score.positive_deltas,
            "negative_events": score.negative_deltas,
            "can_auto_revert": perms.can_auto_revert,
            "can_propose": perms.can_propose_rollback,
            "needs_human": perms.needs_human_approval,
            "last_updated": score.last_updated,
            "risk_coverage": ["R15", "R16", "R17", "R18", "R19", "R20"],
        }

    def _load_entries(self) -> list[TrustEntry]:
        entries: list[TrustEntry] = []
        if not self._ledger_path.exists():
            return entries

        try:
            for line in self._ledger_path.read_text(encoding="utf-8").strip().split("\n"):
                if not line:
                    continue
                data = json.loads(line)
                entries.append(
                    TrustEntry(
                        entry_id=data["entry_id"],
                        timestamp_utc=data["timestamp_utc"],
                        trust_delta=data["trust_delta"],
                        reason=data["reason"],
                        operation=data.get("operation", ""),
                        commit_sha=data.get("commit_sha", ""),
                        execution_id=data.get("execution_id", ""),
                    )
                )
        except (json.JSONDecodeError, KeyError):
            pass

        return entries

    def _recompute_score(self) -> TrustScore:
        entries = self._load_entries()
        score = TrustScore.from_ledger(entries)

        self._ledger_dir.mkdir(parents=True, exist_ok=True)

        self._score_path.write_text(
            json.dumps(
                {
                    "score": score.score,
                    "tier": score.tier,
                    "total_entries": score.total_entries,
                    "positive_deltas": score.positive_deltas,
                    "negative_deltas": score.negative_deltas,
                    "last_updated": score.last_updated,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return score
