# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.anomaly

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.anomaly — MOD-INF-020 · 异常行为检测引擎
=====================================================
蓝图 §5 · 13 种异常签名检测（ANM-001 ~ ANM-013）

异常签名
--------
  ANM-001  UNAUTHORIZED_ACCESS      越权操作
  ANM-002  BULK_DELETE              批量删除
  ANM-003  GATE_BYPASS              门禁跳过
  ANM-004  OFF_HOURS_ACTIVITY       非工作时间操作
  ANM-005  HIGH_FREQUENCY           高频操作
  ANM-006  CROSS_AGENT_CONFLICT     跨 Agent 冲突
  ANM-007  AUDIT_LOG_ANOMALY        审计日志异常
  ANM-008  IMPERSONATION            冒充操作
  ANM-009  DELEGATION_CHAIN_ANOMALY 委托链异常
  ANM-010  COLLUSION_PATTERN        协同规避
  ANM-011  INDIRECT_OPERATION       间接操作
  ANM-012  TRUST_TREND              信任趋势下降
  ANM-013  DRY_RUN_MISMATCH         Dry-Run 差异
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter, defaultdict
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from zephyr.audit_trail.models import AuditEventType

_logger = logging.getLogger(__name__)

DEFAULT_EVENT_LOG: Path = Path("data/audit_trail/events.jsonl")


class AnomalySignature(str, Enum):
    UNAUTHORIZED_ACCESS = "ANM-001"
    BULK_DELETE = "ANM-002"
    GATE_BYPASS = "ANM-003"
    OFF_HOURS_ACTIVITY = "ANM-004"
    HIGH_FREQUENCY = "ANM-005"
    CROSS_AGENT_CONFLICT = "ANM-006"
    AUDIT_LOG_ANOMALY = "ANM-007"
    IMPERSONATION = "ANM-008"
    DELEGATION_CHAIN_ANOMALY = "ANM-009"
    COLLUSION_PATTERN = "ANM-010"
    INDIRECT_OPERATION = "ANM-011"
    TRUST_TREND = "ANM-012"
    DRY_RUN_MISMATCH = "ANM-013"


class AnomalyResult:
    def __init__(
        self,
        signature: AnomalySignature,
        severity: str,
        description: str,
        evidence: dict[str, Any] | None = None,
        score: float = 0.0,
    ) -> None:
        self.signature = signature
        self.severity = severity
        self.description = description
        self.evidence = evidence or {}
        self.score = score
        self.detected_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "signature": self.signature.value,
            "name": self.signature.name,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "score": self.score,
            "detected_at": self.detected_at,
        }


class AnomalyDetector:
    def __init__(self, event_log_path: Path | str = DEFAULT_EVENT_LOG) -> None:
        self._event_log_path = Path(event_log_path)
        self._events: list[dict[str, Any]] | None = None

    def _load_events(self) -> list[dict[str, Any]]:
        if self._events is not None:
            return self._events
        if not self._event_log_path.exists():
            self._events = []
            return self._events
        events: list[dict[str, Any]] = []
        with open(self._event_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        self._events = events
        return self._events

    def scan(self, events: list[dict[str, Any]] | None = None) -> list[AnomalyResult]:
        if events is None:
            events = self._load_events()
        results: list[AnomalyResult] = []
        results.extend(self._detect_unauthorized_access(events))
        results.extend(self._detect_bulk_delete(events))
        results.extend(self._detect_gate_bypass(events))
        results.extend(self._detect_off_hours_activity(events))
        results.extend(self._detect_high_frequency(events))
        results.extend(self._detect_cross_agent_conflict(events))
        results.extend(self._detect_audit_log_anomaly(events))
        results.extend(self._detect_impersonation(events))
        results.extend(self._detect_delegation_chain_anomaly(events))
        results.extend(self._detect_collusion_pattern(events))
        results.extend(self._detect_indirect_operation(events))
        results.extend(self._detect_trust_trend(events))
        results.extend(self._detect_dry_run_mismatch(events))
        return results

    def _detect_unauthorized_access(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            if e.get("event_type") in (
                AuditEventType.PERMISSION_VIOLATION.value,
                AuditEventType.GATE_FAIL.value,
            ) or e.get("status") in ("denied", "blocked", "rejected"):
                results.append(AnomalyResult(
                    signature=AnomalySignature.UNAUTHORIZED_ACCESS,
                    severity="high",
                    description=f"Unauthorized access attempt by {e.get('agent_id', '?')} on {e.get('target_path', '?')}",
                    evidence={"agent_id": e.get("agent_id"), "target": e.get("target_path"), "event_type": e.get("event_type")},
                    score=0.9,
                ))
        return results

    def _detect_bulk_delete(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        delete_events = [e for e in events if e.get("event_type") in (
            AuditEventType.FILE_DELETE.value, "file_delete"
        ) or e.get("operation") == "delete"]
        if len(delete_events) >= 3:
            agents = [e.get("agent_id", "?") for e in delete_events]
            results.append(AnomalyResult(
                signature=AnomalySignature.BULK_DELETE,
                severity="critical",
                description=f"Bulk delete detected: {len(delete_events)} files deleted by {Counter(agents).most_common(1)[0][0]}",
                evidence={"count": len(delete_events), "agents": agents},
                score=1.0,
            ))
        return results

    def _detect_gate_bypass(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            if e.get("event_type") == AuditEventType.GATE_BYPASS.value:
                results.append(AnomalyResult(
                    signature=AnomalySignature.GATE_BYPASS,
                    severity="critical",
                    description=f"Gate bypass by {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id"), "target": e.get("target_path")},
                    score=1.0,
                ))
            elif e.get("event_type") == AuditEventType.DRIFT_TAMPER_PROOF_AUDIT.value and e.get("status") == "bypassed":
                results.append(AnomalyResult(
                    signature=AnomalySignature.GATE_BYPASS,
                    severity="critical",
                    description=f"Drift hotfix bypass by {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id")},
                    score=0.95,
                ))
        return results

    def _detect_off_hours_activity(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            ts = e.get("timestamp", "")
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts)
                hour = dt.hour
                if hour < 6 or hour > 22:
                    results.append(AnomalyResult(
                        signature=AnomalySignature.OFF_HOURS_ACTIVITY,
                        severity="medium",
                        description=f"Off-hours activity at {ts[:19]} by {e.get('agent_id', '?')}",
                        evidence={"timestamp": ts, "agent_id": e.get("agent_id"), "hour": hour},
                        score=0.5,
                    ))
            except (ValueError, TypeError):
                continue
        return results[:10]

    def _detect_high_frequency(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        agent_timestamps: dict[str, list[str]] = defaultdict(list)
        for e in events:
            aid = e.get("agent_id", "")
            ts = e.get("timestamp", "")
            if aid and ts:
                agent_timestamps[aid].append(ts)
        for agent_id, timestamps in agent_timestamps.items():
            if len(timestamps) < 10:
                continue
            sorted_ts = sorted(timestamps)
            window_count = 1
            max_count = 1
            for i in range(1, len(sorted_ts)):
                try:
                    t1 = datetime.fromisoformat(sorted_ts[i - 1])
                    t2 = datetime.fromisoformat(sorted_ts[i])
                    if (t2 - t1).total_seconds() < 60:
                        window_count += 1
                        max_count = max(max_count, window_count)
                    else:
                        window_count = 1
                except (ValueError, TypeError):
                    continue
            if max_count >= 10:
                results.append(AnomalyResult(
                    signature=AnomalySignature.HIGH_FREQUENCY,
                    severity="high",
                    description=f"High-frequency operations by {agent_id}: {max_count} ops in 60s",
                    evidence={"agent_id": agent_id, "max_ops_per_minute": max_count},
                    score=0.8,
                ))
        return results

    def _detect_cross_agent_conflict(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        target_agents: dict[str, list[str]] = defaultdict(list)
        for e in events:
            target = e.get("target_path", e.get("file_path", ""))
            agent = e.get("agent_id", "")
            if target and agent:
                target_agents[target].append(agent)
        for target, agents in target_agents.items():
            unique_agents = set(agents)
            if len(unique_agents) >= 3:
                results.append(AnomalyResult(
                    signature=AnomalySignature.CROSS_AGENT_CONFLICT,
                    severity="medium",
                    description=f"Cross-agent conflict on {target}: {len(unique_agents)} agents",
                    evidence={"target": target, "agents": list(unique_agents)},
                    score=0.6,
                ))
        return results[:5]

    def _detect_audit_log_anomaly(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        if not self._event_log_path.exists():
            return results
        try:
            stat = self._event_log_path.stat()
            if stat.st_size == 0 and len(events) > 0:
                results.append(AnomalyResult(
                    signature=AnomalySignature.AUDIT_LOG_ANOMALY,
                    severity="critical",
                    description="Audit log file is empty but events were provided",
                    evidence={"file_size": 0, "events_count": len(events)},
                    score=1.0,
                ))
        except OSError:
            pass
        prev_hash = ""
        for i, e in enumerate(events):
            current_hash = e.get("entry_hash", "")
            expected_prev = e.get("prev_hash", "")
            if i > 0 and expected_prev != prev_hash:
                results.append(AnomalyResult(
                    signature=AnomalySignature.AUDIT_LOG_ANOMALY,
                    severity="critical",
                    description=f"Hash chain break at event index {i}",
                    evidence={"index": i, "expected_prev": expected_prev, "actual_prev": prev_hash},
                    score=1.0,
                ))
            prev_hash = current_hash
        return results

    def _detect_impersonation(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            if e.get("event_type") == AuditEventType.AGENT_IMPERSONATION.value:
                results.append(AnomalyResult(
                    signature=AnomalySignature.IMPERSONATION,
                    severity="critical",
                    description=f"Agent impersonation detected: {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id"), "details": e.get("metadata", {})},
                    score=1.0,
                ))
        return results

    def _detect_delegation_chain_anomaly(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            depth = e.get("delegation_depth", 0)
            if depth > 5:
                results.append(AnomalyResult(
                    signature=AnomalySignature.DELEGATION_CHAIN_ANOMALY,
                    severity="high",
                    description=f"Excessive delegation depth: {depth} by {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id"), "delegation_depth": depth},
                    score=0.85,
                ))
            if e.get("event_type") == AuditEventType.DELEGATION_CHAIN_ISSUE.value:
                results.append(AnomalyResult(
                    signature=AnomalySignature.DELEGATION_CHAIN_ANOMALY,
                    severity="high",
                    description=f"Delegation chain issue: {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id")},
                    score=0.9,
                ))
        return results

    def _detect_collusion_pattern(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            if e.get("event_type") == AuditEventType.COLLUSION_PATTERN.value:
                results.append(AnomalyResult(
                    signature=AnomalySignature.COLLUSION_PATTERN,
                    severity="critical",
                    description=f"Collusion pattern detected: {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id"), "metadata": e.get("metadata", {})},
                    score=0.95,
                ))
        return results

    def _detect_indirect_operation(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            if e.get("indirect_operation", False):
                results.append(AnomalyResult(
                    signature=AnomalySignature.INDIRECT_OPERATION,
                    severity="medium",
                    description=f"Indirect operation via {e.get('indirect_method', '?')} by {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id"), "method": e.get("indirect_method"), "target": e.get("indirect_target")},
                    score=0.6,
                ))
            elif e.get("event_type") == AuditEventType.INDIRECT_OPERATION.value:
                results.append(AnomalyResult(
                    signature=AnomalySignature.INDIRECT_OPERATION,
                    severity="medium",
                    description=f"Indirect operation by {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id")},
                    score=0.6,
                ))
        return results

    def _detect_trust_trend(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        agent_scores: dict[str, list[float]] = defaultdict(list)
        for e in events:
            score = e.get("trust_score")
            if score is not None:
                agent_scores[e.get("agent_id", "")].append(float(score))
        for agent_id, scores in agent_scores.items():
            if len(scores) < 3:
                continue
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:3]) / min(3, len(scores))
            if older_avg > 0 and recent_avg < older_avg * 0.5:
                results.append(AnomalyResult(
                    signature=AnomalySignature.TRUST_TREND,
                    severity="high",
                    description=f"Trust score declining for {agent_id}: {older_avg:.2f} -> {recent_avg:.2f}",
                    evidence={"agent_id": agent_id, "older_avg": older_avg, "recent_avg": recent_avg},
                    score=0.8,
                ))
        return results

    def _detect_dry_run_mismatch(self, events: list[dict[str, Any]]) -> list[AnomalyResult]:
        results: list[AnomalyResult] = []
        for e in events:
            if e.get("dry_run", False) and e.get("dry_run_real_diff"):
                diff_score = e.get("dry_run_real_diff_score", 0.0)
                if diff_score > 0.3:
                    results.append(AnomalyResult(
                        signature=AnomalySignature.DRY_RUN_MISMATCH,
                        severity="high",
                        description=f"Dry-run mismatch by {e.get('agent_id', '?')}: score={diff_score}",
                        evidence={"agent_id": e.get("agent_id"), "diff_score": diff_score},
                        score=diff_score,
                    ))
            elif e.get("event_type") == AuditEventType.DRY_RUN_MISMATCH.value:
                results.append(AnomalyResult(
                    signature=AnomalySignature.DRY_RUN_MISMATCH,
                    severity="high",
                    description=f"Dry-run mismatch by {e.get('agent_id', '?')}",
                    evidence={"agent_id": e.get("agent_id")},
                    score=0.8,
                ))
        return results
