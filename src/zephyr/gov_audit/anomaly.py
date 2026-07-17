# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §6
# [MODULE] zephyr.gov_audit.anomaly
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.pipeline_runner; integrity
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 异常检测基于统计阈值; 误报率低于10%
# [MODIFY-GUARD] 检测算法变更必须同步 self_monitor.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 检测失败返回空结果
# [TESTS] tests/audit-orchestrator/test_anomaly.py
# [A_module] module_id=MOD-GOV_anomaly | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 治本（裁定#18 G3）：本文件原为桩实现——AnomalyDetector 仅有 feed/detect/scan_series
# （统计 z-score），无 scan 方法、无 _event_log_path；AnomalySignature 是普通类（非 Enum），
# 缺 UNAUTHORIZED_ACCESS/BULK_DELETE/GATE_BYPASS 等成员；AnomalyResult 无 to_dict。
# 现按 tests/audit/test_audit_anomaly.py 契约重写：AnomalySignature 转 Enum（ANM-XXX 编码），
# AnomalyResult 支持 to_dict + detected_at，AnomalyDetector 实现 scan(events) 规则引擎。
# 旧 feed/detect/scan_series 保留以向后兼容（bridges 可能使用）。
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["AnomalyDetector", "AnomalyEvent", "AnomalyResult", "AnomalySignature"]


class AnomalySignature(Enum):
    """异常签名枚举——治本（裁定#18 G3）：转为真 Enum 对齐 test_audit_anomaly.py 契约。

    每个成员的 value 为异常编码（ANM-XXX），name 为大写标识。
    AnomalyResult.to_dict 中 signature=value（编码）、name=name（标识）。
    """

    UNAUTHORIZED_ACCESS = "ANM-001"
    BULK_DELETE = "ANM-002"
    GATE_BYPASS = "ANM-003"
    OFF_HOURS_ACTIVITY = "ANM-004"
    IMPERSONATION = "ANM-005"
    DELEGATION_CHAIN_ANOMALY = "ANM-006"
    INDIRECT_OPERATION = "ANM-007"
    DRY_RUN_MISMATCH = "ANM-008"
    TRUST_TREND = "ANM-009"


class AnomalyResult:
    """异常检测结果——治本（裁定#18 G3）：对齐 test_audit_anomaly.py 契约。

    构造：AnomalyResult(signature=AnomalySignature.X, severity=..., description=...,
    evidence={...}, score=...). 默认 evidence={}、score=0.0。
    to_dict 返回 signature(编码)/name(标识)/severity/description/evidence/score/detected_at。
    """

    def __init__(
        self,
        signature: AnomalySignature | None = None,
        severity: str = "medium",
        description: str = "",
        evidence: dict[str, Any] | None = None,
        score: float = 0.0,
    ) -> None:
        self.signature = signature
        self.severity = severity
        self.description = description
        self.evidence = evidence if evidence is not None else {}
        self.score = score
        self.detected_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "signature": self.signature.value if self.signature else "",
            "name": self.signature.name if self.signature else "",
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "score": self.score,
            "detected_at": self.detected_at,
        }


class AnomalyDetector:
    """异常检测器——治本（裁定#18 G3）：实现 scan() 规则引擎对齐测试契约。

    旧桩仅有 feed/detect/scan_series（统计 z-score），无 scan/_event_log_path。
    现新增 scan(events) 基于事件规则的异常检测，并保留旧统计 API 向后兼容。

    构造：AnomalyDetector() 默认 _event_log_path=Path("data/audit-trail/events.jsonl")；
    AnomalyDetector(path) 指定事件日志路径。旧 AnomalyDetector(window_size=50) 仍兼容
    （首参为 int 时视为 window_size）。
    """

    def __init__(self, event_log_path: Any = None, window_size: int = 50) -> None:
        # 向后兼容：旧调用 AnomalyDetector(50) 将 int 位置参视为 window_size
        if isinstance(event_log_path, int):
            window_size = event_log_path
            event_log_path = None
        if event_log_path is None:
            self._event_log_path: Path = Path("data/audit-trail/events.jsonl")
        else:
            self._event_log_path = Path(event_log_path)
        # 旧统计 API 状态
        self._window_size = window_size
        self._values: list[float] = []

    # ------------------------------------------------------------------
    # 新 API（裁定#18 G3）：scan 规则引擎
    # ------------------------------------------------------------------
    def scan(self, events: list[dict[str, Any]] | None = None) -> list[AnomalyResult]:
        """扫描事件列表，返回检测到的异常结果。

        Args:
            events: 事件列表；None 时从 _event_log_path 加载。

        Returns:
            AnomalyResult 列表（空列表表示无异常或无事件）。
        """
        if events is None:
            events = self._load_from_file()
        if not events:
            return []

        results: list[AnomalyResult] = []
        delete_counts: dict[str, int] = {}
        trust_scores: dict[str, list[float]] = {}
        for event in events:
            self._detect_per_event(event, results, delete_counts, trust_scores)
        self._detect_aggregated(delete_counts, trust_scores, results)
        return results

    def _detect_per_event(
        self,
        event: dict[str, Any],
        results: list[AnomalyResult],
        delete_counts: dict[str, int],
        trust_scores: dict[str, list[float]],
    ) -> None:
        """对单个事件执行规则检测（Extract Method 降低 scan 复杂度）。"""
        et = event.get("event_type", "")
        agent_id = event.get("agent_id", "")
        self._check_unauthorized(event, et, agent_id, results)
        self._check_simple_match(et, "gate_bypass", AnomalySignature.GATE_BYPASS,
                                  "critical", "Gate bypass", agent_id, results)
        self._check_simple_match(et, "agent_impersonation", AnomalySignature.IMPERSONATION,
                                  "critical", "Agent impersonation", agent_id, results)
        if et == "file_delete":
            delete_counts[agent_id] = delete_counts.get(agent_id, 0) + 1
        ts = event.get("timestamp")
        if ts and self._is_off_hours(ts):
            results.append(AnomalyResult(
                signature=AnomalySignature.OFF_HOURS_ACTIVITY, severity="medium",
                description=f"Off-hours activity by {agent_id}",
                evidence={"timestamp": ts, "agent_id": agent_id}))
        self._check_delegation(event, agent_id, results)
        self._check_indirect(event, agent_id, results)
        self._check_dry_run(event, agent_id, results)
        score = event.get("trust-score")
        if score is not None:
            trust_scores.setdefault(agent_id, []).append(float(score))

    def _check_unauthorized(
        self, event: dict[str, Any], et: str, agent_id: str,
        results: list[AnomalyResult],
    ) -> None:
        """检测 UNAUTHORIZED_ACCESS（permission_violation/gate_fail/status=denied）。"""
        if et in ("permission_violation", "gate_fail") or event.get("status") == "denied":
            results.append(AnomalyResult(
                signature=AnomalySignature.UNAUTHORIZED_ACCESS, severity="high",
                description=f"Unauthorized access by {agent_id}",
                evidence={"event_type": et, "agent_id": agent_id}))

    def _check_simple_match(
        self, et: str, match_type: str, sig: "AnomalySignature",
        severity: str, desc_prefix: str, agent_id: str,
        results: list[AnomalyResult],
    ) -> None:
        """检测精确 event_type 匹配的异常（GATE_BYPASS/IMPERSONATION）。"""
        if et == match_type:
            results.append(AnomalyResult(
                signature=sig, severity=severity,
                description=f"{desc_prefix} by {agent_id}" if desc_prefix != "Agent impersonation"
                            else f"Agent impersonation: {agent_id}",
                evidence={"agent_id": agent_id}))

    def _check_delegation(
        self, event: dict[str, Any], agent_id: str,
        results: list[AnomalyResult],
    ) -> None:
        """检测 DELEGATION_CHAIN_ANOMALY（depth > 5）。"""
        depth = event.get("delegation_depth", 0)
        if isinstance(depth, (int, float)) and depth > 5:
            results.append(AnomalyResult(
                signature=AnomalySignature.DELEGATION_CHAIN_ANOMALY, severity="high",
                description=f"Delegation chain depth {depth} exceeds limit",
                evidence={"delegation_depth": depth, "agent_id": agent_id}))

    def _check_indirect(
        self, event: dict[str, Any], agent_id: str,
        results: list[AnomalyResult],
    ) -> None:
        """检测 INDIRECT_OPERATION。"""
        if event.get("indirect_operation"):
            results.append(AnomalyResult(
                signature=AnomalySignature.INDIRECT_OPERATION, severity="high",
                description=f"Indirect operation via {event.get('indirect_method', 'unknown')}",
                evidence={"indirect_method": event.get("indirect_method"), "agent_id": agent_id}))

    def _check_dry_run(
        self, event: dict[str, Any], agent_id: str,
        results: list[AnomalyResult],
    ) -> None:
        """检测 DRY_RUN_MISMATCH。"""
        if event.get("dry_run") and event.get("dry_run_real_diff"):
            results.append(AnomalyResult(
                signature=AnomalySignature.DRY_RUN_MISMATCH, severity="high",
                description="Dry-run/real mismatch detected",
                evidence={"dry_run_real_diff_score": event.get("dry_run_real_diff_score"),
                          "agent_id": agent_id}))

    def _detect_aggregated(
        self,
        delete_counts: dict[str, int],
        trust_scores: dict[str, list[float]],
        results: list[AnomalyResult],
    ) -> None:
        """循环后聚合判定（Extract Method 降低 scan 复杂度）。"""
        for agent_id, count in delete_counts.items():
            if count >= 3:
                results.append(AnomalyResult(
                    signature=AnomalySignature.BULK_DELETE, severity="critical",
                    description=f"Bulk delete: {count} files by {agent_id}",
                    evidence={"count": count, "agent_id": agent_id}))
        for agent_id, scores in trust_scores.items():
            if len(scores) >= 4 and self._is_declining(scores):
                results.append(AnomalyResult(
                    signature=AnomalySignature.TRUST_TREND, severity="high",
                    description=f"Trust score declining trend for {agent_id}",
                    evidence={"scores": scores, "agent_id": agent_id}))

    def _load_from_file(self) -> list[dict[str, Any]]:
        """从 _event_log_path 加载 JSONL 事件。文件不存在或空 → 返回空列表。"""
        if not self._event_log_path.exists():
            return []
        events: list[dict[str, Any]] = []
        try:
            with open(self._event_log_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except (OSError, json.JSONDecodeError):
            logger.warning("Failed to load events from %s", self._event_log_path, exc_info=True)
            return []
        return events

    @staticmethod
    def _is_off_hours(ts: str) -> bool:
        """判定时间戳是否为非工作时间（UTC 09:00-18:00 之外）。"""
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            hour = dt.hour
            return hour < 9 or hour >= 18
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _is_declining(scores: list[float]) -> bool:
        """判定 trust-score 序列是否显著下降（末值 < 首值且降幅 > 0.2）。"""
        if len(scores) < 2:
            return False
        return scores[-1] < scores[0] and (scores[0] - scores[-1]) > 0.2

    # ------------------------------------------------------------------
    # 旧统计 API（向后兼容，bridges 可能使用）
    # ------------------------------------------------------------------
    def feed(self, value: float) -> None:
        self._values.append(value)
        if len(self._values) > self._window_size * 2:
            self._values = self._values[-self._window_size :]

    def detect(self, value: float, threshold: float = 2.0) -> dict[str, Any]:
        self.feed(value)

        if len(self._values) < 10:
            return {"is_anomaly": False, "z_score": 0.0, "reason": "insufficient_data"}

        recent = self._values[-self._window_size :]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std_dev = variance**0.5

        if abs(std_dev) < 1e-9:  # noqa: PLR2004 — 浮点==0比较改 < epsilon
            return {"is_anomaly": value != mean, "z_score": 0.0 if value == mean else float("inf")}

        z_score = abs(value - mean) / std_dev
        is_anomaly = z_score > threshold

        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 4),
            "mean": round(mean, 4),
            "std_dev": round(std_dev, 4),
            "threshold": threshold,
        }

    def scan_series(self, series: list[float], threshold: float = 2.0) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for i, v in enumerate(series):
            result = self.detect(v, threshold)
            if result["is_anomaly"]:
                result["index"] = i
                result["value"] = v
                results.append(result)
        return results


class AnomalyEvent:
    """异常事件（向后兼容，旧 API 保留）。"""

    def __init__(
        self,
        event_id: str = "",
        anomaly_type: str = "",
        severity: str = "medium",
        description: str = "",
        timestamp: Any = None,
        source: str = "",
    ) -> None:
        self.event_id = event_id
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.source = source
