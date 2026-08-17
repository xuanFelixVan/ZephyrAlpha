# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §6

# [MODULE] zephyr.gov_audit.anomaly

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES]

# [CONSUMERS] audit-orchestrator.pipeline_runner ; integrity

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] 双 API: (1) scan(events) 规则引擎 + detect(float) z-score 统计; (2) detect(dict) 桥接式可疑权限检测 (G-CT-002); 误报率低于10%

# [MODIFY-GUARD] 检测算法变更必须同步 self_monitor.py

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 检测失败返回空结果; detect(dict) 无匹配返回 None

# [TESTS] tests/audit/test_audit_anomaly.py; tests/bridges/test_bridges_anomaly.py

# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [TTL] permanent

# 治本（裁定#18 G3 + G-CT-002）：本文件原为桩实现——AnomalyDetector 仅有 feed/detect/scan_series

# （统计 z-score），无 scan 方法、无 _event_log_path；AnomalySignature 是普通类（非 Enum），

# 缺 UNAUTHORIZED_ACCESS/BULK_DELETE/GATE_BYPASS 等成员；AnomalyResult 无 to_dict。

# 现按 tests/audit/test_audit_anomaly.py 契约重写：AnomalySignature 转 Enum（ANM-XXX 编码），

# AnomalyResult 支持 to_dict + detected_at，AnomalyDetector 实现 scan(events) 规则引擎。

# 旧 feed/detect/scan_series 保留以向后兼容（bridges 可能使用）。

#

# 治本（G-CT-002 双 API）：AnomalyEvent 从普通类升级为 pydantic BaseModel（必填

# agent_id/operation_signature/resource_path）。AnomalyDetector.detect() 现按输入类型分派：

#   - dict 输入 → 桥接式可疑权限检测（_SUSPICIOUS_OPERATIONS + granted=True → AnomalyEvent|None）

#   - float/int 输入 → 旧 z-score 统计检测（返回 dict，向后兼容）

# 对齐 tests/bridges/test_bridges_anomaly.py 与 tests/governance/security/test_adversarial_contract_attacks.py。

import json

import logging

from datetime import datetime, timezone

from enum import Enum

from pathlib import Path

from typing import Any



from pydantic import BaseModel, Field, model_validator



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

    HIGH_FREQUENCY = "ANM-010"

    CROSS_AGENT_CONFLICT = "ANM-011"

    COLLUSION_PATTERN = "ANM-012"

    PRIVILEGE_ESCALATION = "ANM-013"





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





class AnomalyEvent(BaseModel):

    """审计异常事件 — 双 API 兼容（G-CT-002 + bridges）。



    API 1 (bridges/test_bridges_anomaly.py):

        AnomalyEvent(agent_id=..., operation_signature=..., resource_path=...)

    API 2 (test_gct_002_audit_to_rollback.py):

        AnomalyEvent(signature=AnomalySignature.X, severity=..., description=...,

                     evidence={...}, score=...)



    必须提供至少 ``signature`` 或 ``(agent_id + operation_signature + resource_path)``

    之一，否则 ValidationError。``detected_at`` 自动填充 ISO 时间戳。

    """



    # API 1 fields (bridges)

    agent_id: str = ""

    operation_signature: str = ""

    resource_path: str = ""



    # API 2 fields (G-CT-002)

    signature: AnomalySignature | None = None

    description: str = ""

    evidence: dict[str, Any] = Field(default_factory=dict)

    score: float = 0.0



    # Shared fields

    severity: str = "WARN"

    event_type: str = "anomaly_detected"

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    session_id: str = ""

    detail: str = ""



    @model_validator(mode="after")

    def _require_minimum_fields(self):

        """必须提供 signature 或 (agent_id+operation_signature+resource_path) 之一。"""

        has_api1 = bool(self.agent_id or self.operation_signature or self.resource_path)

        has_api2 = self.signature is not None

        if not has_api1 and not has_api2:

            raise ValueError(

                "AnomalyEvent requires either signature or "

                "(agent_id+operation_signature+resource_path)"

            )

        return self





class AnomalyDetector:

    """异常检测器——治本（裁定#18 G3 + G-CT-002）：双 API 检测器。



    旧桩仅有 feed/detect/scan_series（统计 z-score），无 scan/_event_log_path。

    现新增 scan(events) 基于事件规则的异常检测，并保留旧统计 API 向后兼容。



    构造：AnomalyDetector() 默认 _event_log_path=AUDIT_DATA_DIR/"events.jsonl"（路径真源 SSoT）；

    AnomalyDetector(path) 指定事件日志路径。旧 AnomalyDetector(window_size=50) 仍兼容

    （首参为 int 时视为 window_size）。



    双 API（G-CT-002）：

        - ``detect(audit_record: dict) -> AnomalyEvent | None`` —— 桥接式可疑权限检测

        - ``detect(value: float, threshold: float = 2.0) -> dict`` —— z-score 统计检测

        - ``scan(events) -> list[AnomalyResult]`` —— 事件规则引擎

    """



    # G-CT-002 桥接 API：可疑操作权限白名单（lowercase）。granted=True 且 permission

    # 命中此集合时返回 AnomalyEvent；delete/truncate → HIGH，其余 → WARN。

    _SUSPICIOUS_OPERATIONS: set[str] = {

        "delete",

        "truncate",

        "drop",

        "revoke",

        "sudo",

        "root",

    }



    def __init__(self, event_log_path: int | Path | None = None, window_size: int = 50) -> None:

        # 向后兼容：旧调用 AnomalyDetector(50) 将 int 位置参视为 window_size

        if isinstance(event_log_path, int):

            window_size = event_log_path

            event_log_path = None

        if event_log_path is None:

            # 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 AUDIT_DATA_DIR 真源。
            from zephyr.shared.io.paths import AUDIT_DATA_DIR

            self._event_log_path: Path = AUDIT_DATA_DIR / "events.jsonl"

        else:

            self._event_log_path = Path(event_log_path)

        # 旧统计 API 状态

        self._window_size = window_size

        self._values: list[float] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def event_log_path(self) -> Path:
        """只读：event_log_path（Stage 4 公共化）。"""
        return self._event_log_path

    @event_log_path.setter
    def event_log_path(self, value):
        """写入：event_log_path（Stage 4 公共化）。"""
        self._event_log_path = value




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

        freq_buckets: dict[str, dict[str, int]] = {}

        cross_agent: dict[str, set[str]] = {}

        for event in events:

            self._detect_per_event(event, results, delete_counts, trust_scores, freq_buckets, cross_agent)

        self._detect_aggregated(delete_counts, trust_scores, freq_buckets, cross_agent, results)

        return results



    def _detect_per_event(

        self,

        event: dict[str, Any],

        results: list[AnomalyResult],

        delete_counts: dict[str, int],

        trust_scores: dict[str, list[float]],

        freq_buckets: dict[str, dict[str, int]],

        cross_agent: dict[str, set[str]],

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

            hour = self._extract_hour(ts)

            results.append(AnomalyResult(

                signature=AnomalySignature.OFF_HOURS_ACTIVITY, severity="medium",

                description=f"Off-hours activity by {agent_id}",

                evidence={"timestamp": ts, "agent_id": agent_id, "hour": hour}))

        self._check_delegation(event, agent_id, results)

        self._check_indirect(event, et, agent_id, results)

        self._check_collusion(et, agent_id, results)

        self._check_dry_run(event, et, agent_id, results)

        score = event.get("trust-score")

        if score is not None:

            trust_scores.setdefault(agent_id, []).append(float(score))

        ts = event.get("timestamp")

        if ts and agent_id:

            minute_key = self._minute_key(ts)

            if minute_key:

                freq_buckets.setdefault(agent_id, {})

                freq_buckets[agent_id][minute_key] = freq_buckets[agent_id].get(minute_key, 0) + 1

        target = event.get("target_path")

        if target and agent_id:

            cross_agent.setdefault(target, set()).add(agent_id)



    def _check_unauthorized(

        self, event: dict[str, Any], et: str, agent_id: str,

        results: list[AnomalyResult],

    ) -> None:

        """检测 UNAUTHORIZED_ACCESS（permission_violation/gate_fail/status in denied/blocked/rejected）。"""

        if et in ("permission_violation", "gate_fail") or event.get("status") in ("denied", "blocked", "rejected"):

            results.append(AnomalyResult(

                signature=AnomalySignature.UNAUTHORIZED_ACCESS, severity="high",

                description=f"Unauthorized access by {agent_id}",

                evidence={"event_type": et, "agent_id": agent_id},

                score=0.9))



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

        self, event: dict[str, Any], et: str, agent_id: str,

        results: list[AnomalyResult],

    ) -> None:

        """检测 INDIRECT_OPERATION（indirect_operation 标志或 event_type=indirect_operation）。"""

        if event.get("indirect_operation") or et == "indirect_operation":

            results.append(AnomalyResult(

                signature=AnomalySignature.INDIRECT_OPERATION, severity="high",

                description=f"Indirect operation via {event.get('indirect_method', 'unknown')}",

                evidence={"indirect_method": event.get("indirect_method"), "agent_id": agent_id}))



    def _check_dry_run(

        self, event: dict[str, Any], et: str, agent_id: str,

        results: list[AnomalyResult],

    ) -> None:

        """检测 DRY_RUN_MISMATCH（dry_run 标志 + diff_score > 0.3，或 event_type=dry_run_mismatch）。"""

        diff_score = event.get("dry_run_real_diff_score", 0.0)

        if et == "dry_run_mismatch":

            results.append(AnomalyResult(

                signature=AnomalySignature.DRY_RUN_MISMATCH, severity="high",

                description="Dry-run/real mismatch detected",

                evidence={"diff_score": diff_score, "agent_id": agent_id}))

        elif event.get("dry_run") and event.get("dry_run_real_diff") and diff_score > 0.3:

            results.append(AnomalyResult(

                signature=AnomalySignature.DRY_RUN_MISMATCH, severity="high",

                description="Dry-run/real mismatch detected",

                evidence={"diff_score": diff_score, "agent_id": agent_id}))



    def _check_collusion(

        self, et: str, agent_id: str,

        results: list[AnomalyResult],

    ) -> None:

        """检测 COLLUSION_PATTERN（event_type=collusion_pattern）。"""

        if et == "collusion_pattern":

            results.append(AnomalyResult(

                signature=AnomalySignature.COLLUSION_PATTERN, severity="high",

                description=f"Collusion pattern by {agent_id}",

                evidence={"agent_id": agent_id}))



    def _detect_aggregated(

        self,

        delete_counts: dict[str, int],

        trust_scores: dict[str, list[float]],

        freq_buckets: dict[str, dict[str, int]],

        cross_agent: dict[str, set[str]],

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

        for agent_id, buckets in freq_buckets.items():

            max_ops = max(buckets.values()) if buckets else 0

            if max_ops >= 10:

                results.append(AnomalyResult(

                    signature=AnomalySignature.HIGH_FREQUENCY, severity="high",

                    description=f"High frequency operations by {agent_id}",

                    evidence={"max_ops_per_minute": max_ops, "agent_id": agent_id}))

        for target, agents in cross_agent.items():

            if len(agents) >= 3:

                results.append(AnomalyResult(

                    signature=AnomalySignature.CROSS_AGENT_CONFLICT, severity="high",

                    description=f"Cross-agent conflict on {target}",

                    evidence={"agents": list(agents), "target_path": target}))



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

        """判定时间戳是否为非工作时间（UTC 06:00-22:00 之外，含 06 和 22）。"""

        try:

            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

            hour = dt.hour

            return hour < 6 or hour > 22

        except (ValueError, TypeError):

            return False



    @staticmethod

    def _extract_hour(ts: str) -> int:

        """从时间戳提取小时（失败返回 -1）。"""

        try:

            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

            return dt.hour

        except (ValueError, TypeError):

            return -1



    @staticmethod

    def _minute_key(ts: str) -> str:

        """从时间戳提取分钟级 key（YYYY-MM-DDTHH:MM），失败返回空串。"""

        try:

            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

            return dt.strftime("%Y-%m-%dT%H:%M")

        except (ValueError, TypeError):

            return ""



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



    def detect(self, value: dict[str, Any] | float | int, threshold: float = 2.0) -> AnomalyEvent | dict[str, Any] | None:

        """检测异常——双 API 类型分派（G-CT-002）。



        本方法根据 ``value`` 的类型分派到两条独立的检测路径：



        1. **桥接 API**（``value`` 为 ``dict``）：基于权限规则检测可疑操作。

           当 ``permission`` (lowercase) 命中 ``_SUSPICIOUS_OPERATIONS`` 且

           ``granted is True`` 时返回 ``AnomalyEvent``；否则返回 ``None``。

           ``delete``/``truncate`` → ``severity="HIGH"``，

           ``drop``/``revoke``/``sudo``/``root`` → ``severity="WARN"``。

           对齐 ``tests/bridges/test_bridges_anomaly.py`` 契约。



        2. **统计 API**（``value`` 为 ``float``/``int``）：旧 z-score 统计异常检测。

           维护滑动窗口，返回包含 ``is_anomaly``/``z_score``/``mean``/``std_dev``/

           ``threshold`` 的 dict。向后兼容旧 ``scan_series`` 调用方。



        Args:

            value: 审计记录 dict（桥接 API）或数值（统计 API）。

            threshold: 统计 API 的 z-score 阈值，默认 2.0（仅 float 输入时生效）。



        Returns:

            桥接 API: ``AnomalyEvent | None``。

            统计 API: ``dict[str, Any]``。

        """

        if isinstance(value, dict):

            return self._detect_audit_record(value)

        return self._detect_zscore(value, threshold)



    def _detect_audit_record(self, audit_record: dict[str, Any]) -> "AnomalyEvent | None":

        """桥接 API：检测审计记录中的可疑操作签名（G-CT-002）。



        - ``permission`` 不在 ``_SUSPICIOUS_OPERATIONS`` → 返回 None

        - ``granted`` 非 True → 返回 None

        - ``permission`` 为空或字段缺失 → 返回 None

        - 命中且 granted=True → 返回 AnomalyEvent，operation_signature="permission={perm}"

        - severity: delete/truncate → HIGH；drop/revoke/sudo/root → WARN

        - 大小写不敏感：permission 先 lower() 再匹配

        """

        permission = str(audit_record.get("permission", "")).lower()

        granted = audit_record.get("granted", False)



        if permission and permission in self._SUSPICIOUS_OPERATIONS and granted:

            resource = audit_record.get("resource", "")

            return AnomalyEvent(

                agent_id=audit_record.get("agent_id", "unknown"),

                operation_signature=f"permission={permission}",

                resource_path=resource,

                severity="HIGH" if permission in {"delete", "truncate"} else "WARN",

                session_id=audit_record.get("session_id", ""),

                detail=f"Suspicious operation: {permission} on {resource or '?'}",

            )

        return None



    def _detect_zscore(self, value: float, threshold: float = 2.0) -> dict[str, Any]:

        """统计 API：z-score 异常检测（向后兼容旧 detect(float) 调用方）。"""

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

