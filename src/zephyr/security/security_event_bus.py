# [BLUEPRINT] MOD-SEC-EVENTBUS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/16_ai_security_ops.md | §4.2 P0-1/P0-3
# [MODULE] zephyr.security.security_event_bus
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.utils.time_utils; zephyr.shared.security.secrets
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 单adapter异常MUST独立降级不阻塞总线;高危告警MUST本地持久化不丢;schema校验失败MUST拒收
# [MODIFY-GUARD] 16_ai_security_ops.md §4.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SecurityEventValidationError
# [TESTS] tests/security/test_security_event_bus.py
# [A_module] module_id=MOD-SEC-security_event_bus | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
统一安全事件总线（16号文 Phase 0：P0-1 事件 schema + P0-3 高危告警通道）。

目的：四域安全检测（LSG 安全栈 / 自治边界 gate / 治理门禁 / 运行时检测器与
ai_agent_monitor）各自产出格式各异的安全事件，无统一出口 = 无可观测性。
本模块提供：

1. 统一事件 schema（``SecurityEvent``，pydantic 严格校验）：
   event_id / ts / source_domain / threat_category / severity / evidence_ref /
   session_ref / schema_version。缺字段、非法枚举、schema_version 不匹配一律拒收
   （``SecurityEventValidationError``）。schema_version 承载 16号文 §3.19
   Event Schema Versioning 治理口径。
2. 落盘协议：事件以 JSONL 追加写入 ``.runtime/security_events/security_events.jsonl``
   （运行时区，gitignored），``iter_events()`` 支持机器遍历消费。
3. 四域 adapter：把各域既有事件 dict 转换为统一 schema 后写入总线。
   不变量：单 adapter 异常独立降级（记录 ``degraded`` 留痕），绝不阻塞总线与其他 adapter。
4. 高危告警通道（P0-3）：severity >= high 的事件推送飞书 webhook
   （secret 机制读取 ``ZEPHYR_FEISHU_WEBHOOK``）。webhook 未配置/不可达时
   写入本地持久化队列 ``alerts_pending.jsonl`` 不丢事件，``retry_pending()``
   提供重试语义；``dry_run=True`` 时只留痕 ``alerts_dryrun.jsonl`` 不真发
   （周六演练口径）。

边界：本模块只收口事件，不改动 LSG / access_control / FBL 检测器 /
auto_fix_engine 任何本体逻辑（16号文 §5 第 6 条）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: pending_path 参数
#   fields: 参数 pending_path（无注解）
#   code: security_event_bus.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: dry_run_path 参数
#   fields: 参数 dry_run_path（无注解）
#   code: security_event_bus.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: dry_run 参数
#   fields: 参数 dry_run（无注解）
#   code: security_event_bus.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: timeout_sec 参数
#   fields: 参数 timeout_sec（无注解）
#   code: security_event_bus.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DomainEventAdapter
#   name_en: DomainEventAdapter
#   intro: 域事件 adapter 基类：把本域既有事件 dict 转成统一 schema。
#   desc: 域事件 adapter 基类：把本域既有事件 dict 转成统一 schema。 子类只需实现 ``raw_mapping`` 返回 schema 字段 dict；``adapt…；公共方法（定义序）: raw_map…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② LsgSecurityStackAdapter
#   name_en: LsgSecurityStackAdapter
#   intro: LSG 安全栈（L0~L8 / L6 审计事件）adapter。
#   desc: LSG 安全栈（L0~L8 / L6 审计事件）adapter。 消费 behavior_audit_logger / gateway 判决风格事件： {layer, rule,…；公共方法（定义序）: raw_map…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ AutonomyGateAdapter
#   name_en: AutonomyGateAdapter
#   intro: 自治边界 gate（access_control 守卫/门禁拦截）adapter。
#   desc: 自治边界 gate（access_control 守卫/门禁拦截）adapter。 消费 {gate, decision, blocked, reason, agent_id,…；公共方法（定义序）: raw_mapp…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ GovernanceGateAdapter
#   name_en: GovernanceGateAdapter
#   intro: 治理门禁（governance / security_governance 判决）adapter。
#   desc: 治理门禁（governance / security_governance 判决）adapter。 消费 {policy_id, verdict, finding, severi…；公共方法（定义序）: raw_map…
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ RuntimeDetectorAdapter
#   name_en: RuntimeDetectorAdapter
#   intro: 运行时域（FBL 检测器 / ai_agent_monitor 风险评分）adapter。
#   desc: 运行时域（FBL 检测器 / ai_agent_monitor 风险评分）adapter。 消费 {detector, state?, risk_score?, is_breac…；公共方法（定义序）: raw_map…
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ FeishuAlertChannel
#   name_en: FeishuAlertChannel
#   intro: 高危事件飞书 webhook 告警通道（16号文 §4.2 P0-3）。
#   desc: 高危事件飞书 webhook 告警通道（16号文 §4.2 P0-3）。 不变量「告警不丢」：webhook 未配置 / 不可达 / 非 200 一律写入本地持久化 队列 ``a…；公共方法（定义序）: format_…
#   inputs: pending_path dry_run_path dry_run timeout_sec webhook_url
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ SecurityEventBus
#   name_en: SecurityEventBus
#   intro: 统一安全事件总线：校验 → 落盘 JSONL → 高危告警。
#   desc: 统一安全事件总线：校验 → 落盘 JSONL → 高危告警。 不变量： - schema 校验失败 MUST 拒收（SecurityEventValidationError），不…；公共方法（定义序）: events_…
#   inputs: event_dir alert_threshold dry_run_alert alerter
#   outputs: 返回值
#   （注：A7 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（12 定义）
#   name_en: public defs
#   intro: DomainEventAdapter, LsgSecurityStackAdapter, AutonomyGateAdapter, GovernanceGat…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import json
import logging
import os
import urllib.request
import uuid
from collections.abc import Iterator, Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

__all__ = [
    "SCHEMA_VERSION",
    "AutonomyGateAdapter",
    "DomainEventAdapter",
    "FeishuAlertChannel",
    "GovernanceGateAdapter",
    "LsgSecurityStackAdapter",
    "RuntimeDetectorAdapter",
    "SecurityEvent",
    "SecurityEventBus",
    "SecurityEventValidationError",
    "Severity",
    "SourceDomain",
    "ThreatCategory",
]

SCHEMA_VERSION: Final[str] = "1.0"
DEFAULT_EVENT_DIR: Final[Path] = REPO_ROOT / ".runtime" / "security_events"
EVENTS_FILENAME: Final[str] = "security_events.jsonl"
ALERTS_PENDING_FILENAME: Final[str] = "alerts_pending.jsonl"
ALERTS_DRYRUN_FILENAME: Final[str] = "alerts_dryrun.jsonl"
FEISHU_WEBHOOK_ENV: Final[str] = "ZEPHYR_FEISHU_WEBHOOK"
FEISHU_WEBHOOK_SERVICE: Final[str] = "feishu"
ALERT_TIMEOUT_SEC: Final[float] = 5.0
MAX_ALERT_RETRY: Final[int] = 5


class SourceDomain(str, Enum):
    """安全事件来源域（16号文 §4.2 P0-1 四域事件源）。"""

    LSG_SECURITY_STACK = "lsg_security_stack"
    AUTONOMY_GATE = "autonomy_gate"
    GOVERNANCE_GATE = "governance_gate"
    RUNTIME = "runtime"


class ThreatCategory(str, Enum):
    """威胁类别（16号文 §3.2 四威胁 + 越权/注入/策略违规收口）。"""

    INJECTION = "injection"
    COLLUSION = "collusion"
    EMERGENCE = "emergence"
    HALLUCINATION = "hallucination"
    MEMORY_POISONING = "memory_poisoning"
    PRIVILEGE_VIOLATION = "privilege_violation"
    POLICY_VIOLATION = "policy_violation"
    RESOURCE_ABUSE = "resource_abuse"
    OTHER = "other"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_SEVERITY_ORDER: Final[dict[Severity, int]] = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


class SecurityEventValidationError(ValueError):
    """统一安全事件 schema 校验失败（缺字段/非法枚举/版本不匹配）。"""


class SecurityEvent(BaseModel):
    """统一安全事件 schema（16号文 §4.2 P0-1 + §3.19 版本治理）。

    严格校验：未知字段拒收（extra="forbid"）、必填缺失拒收、非法枚举拒收、
    schema_version 不等于当前版本拒收、evidence_ref 空串拒收、ts 非 ISO8601 拒收。
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=False)

    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    ts: str = Field(default_factory=now_iso)
    source_domain: SourceDomain
    threat_category: ThreatCategory
    severity: Severity
    evidence_ref: str = Field(min_length=1)
    session_ref: str = ""
    schema_version: str = SCHEMA_VERSION
    detail: dict[str, Any] = Field(default_factory=dict)

    @field_validator("schema_version")
    @classmethod
    def _check_schema_version(cls, v: str) -> str:
        if v != SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version: {v!r} (supported: {SCHEMA_VERSION})")
        return v

    @field_validator("ts")
    @classmethod
    def _check_ts(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"ts is not ISO8601: {v!r}") from exc
        return v

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any]) -> SecurityEvent:
        """从 dict 构造并校验；任何校验失败统一抛 SecurityEventValidationError。"""
        try:
            return cls(**dict(raw))
        except ValidationError as exc:
            raise SecurityEventValidationError(str(exc)) from exc

    def to_jsonl(self) -> str:
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"))

    def severity_at_least(self, threshold: Severity) -> bool:
        return _SEVERITY_ORDER[self.severity] >= _SEVERITY_ORDER[threshold]


class DomainEventAdapter:
    """域事件 adapter 基类：把本域既有事件 dict 转成统一 schema。

    子类只需实现 ``raw_mapping`` 返回 schema 字段 dict；``adapt`` 统一走
    ``SecurityEvent.from_raw`` 严格校验，校验失败抛 SecurityEventValidationError。
    """

    name: str = "base"
    domain: SourceDomain = SourceDomain.RUNTIME

    def raw_mapping(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def adapt(self, raw: Mapping[str, Any]) -> SecurityEvent:
        if not isinstance(raw, Mapping):
            raise SecurityEventValidationError(f"adapter {self.name}: raw event must be a mapping")
        mapped = self.raw_mapping(raw)
        mapped.setdefault("source_domain", self.domain.value)
        mapped.setdefault("schema_version", SCHEMA_VERSION)
        return SecurityEvent.from_raw(mapped)


class LsgSecurityStackAdapter(DomainEventAdapter):
    """LSG 安全栈（L0~L8 / L6 审计事件）adapter。

    消费 behavior_audit_logger / gateway 判决风格事件：
    {layer, rule, action, target, result, model, session_id, severity?, threat_category?, detail?}
    判级口径：显式 severity 优先；result 含 block/deny → high；否则 medium。
    """

    name: str = "lsg_security_stack"
    domain: SourceDomain = SourceDomain.LSG_SECURITY_STACK

    def raw_mapping(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        layer = str(raw.get("layer", "l?"))
        rule = str(raw.get("rule") or raw.get("action") or "unspecified")
        target = str(raw.get("target", ""))
        result = str(raw.get("result", "")).lower()
        severity = raw.get("severity")
        if severity is None:
            severity = Severity.HIGH.value if ("block" in result or "deny" in result) else Severity.MEDIUM.value
        return {
            "threat_category": raw.get("threat_category", ThreatCategory.INJECTION.value),
            "severity": severity,
            "evidence_ref": f"lsg://{layer}/{rule}/{target}",
            "session_ref": str(raw.get("session_id", "")),
            "detail": {"layer": layer, "rule": rule, "result": result, "model": raw.get("model", "")},
        }


class AutonomyGateAdapter(DomainEventAdapter):
    """自治边界 gate（access_control 守卫/门禁拦截）adapter。

    消费 {gate, decision, blocked, reason, agent_id, session_id, severity?, threat_category?}。
    判级口径：blocked/拦截 → high；显式 severity 优先。
    """

    name: str = "autonomy_gate"
    domain: SourceDomain = SourceDomain.AUTONOMY_GATE

    def raw_mapping(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        gate = str(raw.get("gate", "unknown_gate"))
        blocked = bool(raw.get("blocked", False)) or str(raw.get("decision", "")).lower() in {
            "block",
            "deny",
            "denied",
        }
        severity = raw.get("severity")
        if severity is None:
            severity = Severity.HIGH.value if blocked else Severity.LOW.value
        return {
            "threat_category": raw.get("threat_category", ThreatCategory.PRIVILEGE_VIOLATION.value),
            "severity": severity,
            "evidence_ref": f"gate://{gate}/{raw.get('agent_id', '')}",
            "session_ref": str(raw.get("session_id", "")),
            "detail": {"gate": gate, "decision": raw.get("decision", ""), "reason": raw.get("reason", "")},
        }


class GovernanceGateAdapter(DomainEventAdapter):
    """治理门禁（governance / security_governance 判决）adapter。

    消费 {policy_id, verdict, finding, severity?, threat_category?, session_id?}。
    判级口径：verdict RED → high；YELLOW → medium；PASS → low；显式 severity 优先。
    """

    name: str = "governance_gate"
    domain: SourceDomain = SourceDomain.GOVERNANCE_GATE
    _VERDICT_SEVERITY: Final[dict[str, str]] = {
        "red": Severity.HIGH.value,
        "yellow": Severity.MEDIUM.value,
        "pass": Severity.LOW.value,
    }

    def raw_mapping(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        policy = str(raw.get("policy_id", "unknown_policy"))
        verdict = str(raw.get("verdict", "")).lower()
        severity = raw.get("severity")
        if severity is None:
            severity = self._VERDICT_SEVERITY.get(verdict, Severity.MEDIUM.value)
        return {
            "threat_category": raw.get("threat_category", ThreatCategory.POLICY_VIOLATION.value),
            "severity": severity,
            "evidence_ref": f"gov://{policy}/{raw.get('finding', '')}",
            "session_ref": str(raw.get("session_id", "")),
            "detail": {"policy_id": policy, "verdict": verdict},
        }


class RuntimeDetectorAdapter(DomainEventAdapter):
    """运行时域（FBL 检测器 / ai_agent_monitor 风险评分）adapter。

    消费 {detector, state?, risk_score?, is_breached?, threat_category?, severity?, session_id?}。
    判级口径：state=CRITICAL → critical；is_breached=True → high；
    risk_score>=0.6 → high（MOD-RK-14 阈值口径）；否则 medium；显式 severity 优先。
    """

    name: str = "runtime"
    domain: SourceDomain = SourceDomain.RUNTIME

    def raw_mapping(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        detector = str(raw.get("detector", "unknown_detector"))
        state = str(raw.get("state", "")).upper()
        breached = bool(raw.get("is_breached", False))
        score = raw.get("risk_score")
        severity = raw.get("severity")
        if severity is None:
            if state == "CRITICAL":
                severity = Severity.CRITICAL.value
            elif breached or (isinstance(score, (int, float)) and score >= 0.6):
                severity = Severity.HIGH.value
            else:
                severity = Severity.MEDIUM.value
        return {
            "threat_category": raw.get("threat_category", ThreatCategory.EMERGENCE.value),
            "severity": severity,
            "evidence_ref": f"runtime://{detector}",
            "session_ref": str(raw.get("session_id", "")),
            "detail": {"detector": detector, "state": state, "risk_score": score, "is_breached": breached},
        }


class FeishuAlertChannel:
    """高危事件飞书 webhook 告警通道（16号文 §4.2 P0-3）。

    不变量「告警不丢」：webhook 未配置 / 不可达 / 非 200 一律写入本地持久化
    队列 ``alerts_pending.jsonl``；``retry_pending()`` 重试，成功出队、失败
    累计 retry_count，超过 MAX_ALERT_RETRY 保留为死信（不丢）。dry_run 模式
    只留痕 ``alerts_dryrun.jsonl``，不发任何网络请求（演练口径）。
    """

    def __init__(
        self,
        *,
        pending_path: Path,
        dry_run_path: Path | None = None,
        dry_run: bool = False,
        timeout_sec: float = ALERT_TIMEOUT_SEC,
        webhook_url: str | None = None,
    ) -> None:
        self._pending_path = pending_path
        self._dry_run_path = dry_run_path or pending_path.with_name(ALERTS_DRYRUN_FILENAME)
        self._dry_run = dry_run
        self._timeout = timeout_sec
        self._webhook_override = webhook_url
        self._pending_path.parent.mkdir(parents=True, exist_ok=True)

    def _resolve_webhook(self) -> str:
        if self._webhook_override is not None:
            return self._webhook_override
        # 先走 secret 机制（service 未登记会抛 SecretsError → 捕获降级到环境变量）
        try:
            from zephyr.shared.security.secrets import get_service_secret

            url = get_service_secret(FEISHU_WEBHOOK_ENV, FEISHU_WEBHOOK_SERVICE, required=False)
            if url:
                return url
        except Exception:  # noqa: BLE001 — secret 机制不可用时降级环境变量，绝不阻断告警通道
            logger.debug("get_service_secret 不可用，降级环境变量读取", exc_info=True)
        return os.environ.get(FEISHU_WEBHOOK_ENV, "")

    @staticmethod
    def format_alert_text(event: SecurityEvent) -> str:
        return (
            f"[ZephyrAlpha 安全告警] severity={event.severity.value} "
            f"domain={event.source_domain.value} threat={event.threat_category.value} "
            f"event_id={event.event_id} ts={event.ts} evidence={event.evidence_ref}"
        )

    def _append_jsonl(self, path: Path, record: Mapping[str, Any]) -> None:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    def _post_webhook(self, webhook: str, text: str) -> bool:
        payload = json.dumps({"msg_type": "text", "content": {"text": text}}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return bool(resp.status == 200)
        except Exception:  # noqa: BLE001 — webhook 不可达属预期降级路径，调用方落本地队列
            logger.warning("飞书 webhook 发送失败，转入本地持久化队列", exc_info=True)
            return False

    def send(self, event: SecurityEvent) -> bool:
        """发送告警；失败/未配置持久化不丢。返回 True=已送达（含 dry_run 留痕）。"""
        text = self.format_alert_text(event)
        if self._dry_run:
            self._append_jsonl(
                self._dry_run_path,
                {"status": "dry_run", "ts": now_iso(), "text": text, "event": event.model_dump(mode="json")},
            )
            return True
        webhook = self._resolve_webhook()
        if not webhook:
            self._persist_pending(event, "webhook_not_configured")
            return False
        if self._post_webhook(webhook, text):
            return True
        self._persist_pending(event, "webhook_unreachable")
        return False

    def _persist_pending(self, event: SecurityEvent, reason: str) -> None:
        self._append_jsonl(
            self._pending_path,
            {
                "status": "pending",
                "reason": reason,
                "retry_count": 0,
                "enqueued_ts": now_iso(),
                "event": event.model_dump(mode="json"),
            },
        )

    def pending_count(self) -> int:
        if not self._pending_path.exists():
            return 0
        with open(self._pending_path, encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())

    def retry_pending(self) -> dict[str, int]:
        """重试本地队列：成功出队，失败 retry_count+1，超 MAX_ALERT_RETRY 转死信保留。"""
        stats = {"retried": 0, "delivered": 0, "dead": 0}
        if not self._pending_path.exists():
            return stats
        if self._dry_run:
            return stats  # dry_run 模式不做任何网络重试
        webhook = self._resolve_webhook()
        with open(self._pending_path, encoding="utf-8") as fh:
            records = [json.loads(line) for line in fh if line.strip()]
        remaining: list[dict[str, Any]] = []
        for rec in records:
            stats["retried"] += 1
            event = SecurityEvent.from_raw(rec["event"])
            delivered = bool(webhook) and self._post_webhook(webhook, self.format_alert_text(event))
            if delivered:
                stats["delivered"] += 1
                continue
            rec["retry_count"] = int(rec.get("retry_count", 0)) + 1
            rec["last_retry_ts"] = now_iso()
            if rec["retry_count"] >= MAX_ALERT_RETRY:
                rec["status"] = "dead_letter"
                stats["dead"] += 1
            remaining.append(rec)
        tmp = self._pending_path.with_suffix(self._pending_path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            for rec in remaining:
                fh.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
        os.replace(tmp, self._pending_path)
        return stats


class SecurityEventBus:
    """统一安全事件总线：校验 → 落盘 JSONL → 高危告警。

    不变量：
    - schema 校验失败 MUST 拒收（SecurityEventValidationError），不落盘不告警；
    - 单 adapter 异常 MUST 独立降级（``degraded`` 留痕），不阻塞总线与其他 adapter；
    - severity >= alert_threshold 的事件 MUST 走告警通道，通道失败本地持久化不丢。
    """

    def __init__(
        self,
        *,
        event_dir: Path | None = None,
        alert_threshold: Severity = Severity.HIGH,
        dry_run_alert: bool = False,
        alerter: FeishuAlertChannel | None = None,
    ) -> None:
        self._event_dir = event_dir or DEFAULT_EVENT_DIR
        self._event_dir.mkdir(parents=True, exist_ok=True)
        self._events_path = self._event_dir / EVENTS_FILENAME
        self._alert_threshold = alert_threshold
        self._alerter = alerter or FeishuAlertChannel(
            pending_path=self._event_dir / ALERTS_PENDING_FILENAME,
            dry_run=dry_run_alert,
        )
        self._adapters: dict[str, DomainEventAdapter] = {}
        self._degraded: list[dict[str, Any]] = []

    @property
    def events_path(self) -> Path:
        return self._events_path

    @property
    def alerter(self) -> FeishuAlertChannel:
        return self._alerter

    @property
    def degraded(self) -> list[dict[str, Any]]:
        """adapter 降级留痕（只读拷贝）。"""
        return list(self._degraded)

    def register_adapter(self, adapter: DomainEventAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def register_default_adapters(self) -> None:
        for adapter in (
            LsgSecurityStackAdapter(),
            AutonomyGateAdapter(),
            GovernanceGateAdapter(),
            RuntimeDetectorAdapter(),
        ):
            self.register_adapter(adapter)

    def emit(self, event: SecurityEvent | Mapping[str, Any]) -> SecurityEvent:
        """校验并写入总线；severity 达阈值触发告警（告警失败不传播）。"""
        if not isinstance(event, SecurityEvent):
            event = SecurityEvent.from_raw(event)
        with open(self._events_path, "a", encoding="utf-8") as fh:
            fh.write(event.to_jsonl() + "\n")
        if event.severity_at_least(self._alert_threshold):
            try:
                self._alerter.send(event)
            except Exception:  # noqa: BLE001 — 告警通道异常绝不阻塞事件落盘主流程
                logger.error("告警通道异常（事件已落盘） event_id=%s", event.event_id, exc_info=True)
        return event

    def emit_via_adapter(self, adapter_name: str, raw: Mapping[str, Any]) -> SecurityEvent | None:
        """经指定 adapter 转换并写入；adapter 异常独立降级返回 None。"""
        adapter = self._adapters.get(adapter_name)
        if adapter is None:
            self._record_degraded(adapter_name, f"adapter not registered: {adapter_name}")
            return None
        try:
            event = adapter.adapt(raw)
        except Exception as exc:  # noqa: BLE001 — adapter 独立降级不变量：捕获一切不传播
            self._record_degraded(adapter_name, f"{type(exc).__name__}: {exc}")
            return None
        return self.emit(event)

    def _record_degraded(self, adapter_name: str, error: str) -> None:
        record = {"adapter": adapter_name, "error": error, "ts": now_iso()}
        self._degraded.append(record)
        logger.warning("安全事件 adapter 降级: %s", record)

    def iter_events(self) -> Iterator[SecurityEvent]:
        """机器遍历消费落盘事件（坏行跳过不阻断，与审计日志读取同口径）。"""
        if not self._events_path.exists():
            return
        with open(self._events_path, encoding="utf-8") as fh:
            lines = fh.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                yield SecurityEvent.from_raw(json.loads(line))
            except (json.JSONDecodeError, SecurityEventValidationError):
                continue

    def count_events(self) -> int:
        return sum(1 for _ in self.iter_events())
