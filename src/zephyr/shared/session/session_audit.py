# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.session.session_audit
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


session_audit.py —— Session 审计轨迹（Phase 12 | 盲点 B32）

痛点修复：每次 AI session 的记录——prompts/decisions/tool_calls/costs/errors/outcomes。
1人+AI 维护下唯一的学习来源。

设计对标：
  - PydanticAI Logfire audit: 结构化审计日志
  - LangChain callback system: 事件追踪
  - Session Log Schema (GOV-AI-007 v2.2.0): 字段对齐

AI 施工约定：
  - 每个 session MUST 通过 SessionAuditTrail 记录
  - JSONL 格式追加写入——不可变审计
  - 与 session_logs/ YAML 互补（此模块负责运行时实时记录）

SSoT: MOD-INF-016 §12 盲点 B32 + GOV-AI-007 Session Log Schema

依赖倒置（5.174-M6）：全局审计写入由 governance 层经 register_audit_writer_provider()
依赖注入——本模块不 import gov_audit（shared 层禁止向上依赖 L2 governance）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 会话事件数据 六类记录入参
#   fields: prompts(role/content/token_count)、decisions、tool_calls、costs(provider/model/tokens/cost_usd)、errors、outcomes
#   code: SessionRecord.add_* L183-L253
# - id: I2
#   name: 审计目录 audit_dir 路径
#   fields: JSONL 审计文件根目录，默认 logs/session_audit/，构造时自动建目录
#   code: audit_dir L337
# - id: I3
#   name: 全局审计写入器工厂 可选注入
#   fields: governance 层经 register_audit_writer_provider 注入的 AuditWriter 工厂；未注册则跳过全局事件
#   code: _audit_writer_provider L69
# 层: 算法
# - id: A1
#   name_zh: ① 会话事件采集
#   name_en: SessionRecord.add_prompt/add_decision/add_tool_call/add_cost/add_error/set_outcomes
#   intro: 把六类会话事件逐条追加进内存 SessionRecord，长文本截200字预览
#   desc: 每个 add_* 构造对应 Record（UTC时间戳），content/params/result 超200字截断；to_dict 汇总 counts 与 total_cost_usd=Σcost、total_tokens=Σ(input+output)、error_count、recovered_count=Σrecovered
#   inputs: I1
#   outputs: SessionRecord（内存态）
# - id: A2
#   name_zh: ② JSONL追加写入与全局事件转发
#   name_en: append_record/_sanitize_session_id
#   intro: session_id 消毒后定位 jsonl 文件，加锁追加一行，再经注入的 provider 转发全局审计
#   desc: _sanitize_session_id 把 \ / .. 换成 _ 防路径穿越；to_dict 序列化后 RLock 保护下 append 一行 JSON；随后查 _audit_writer_provider，注册则 provider().write(session_record 事件)，未注册记 debug 跳过，写异常被吞仅 warning（best-effort）
#   inputs: I2 I3
#   outputs: jsonl 文件路径 + 全局审计事件
#   invariant: JSONL 只追加不改写（不可变审计）
# - id: A3
#   name_zh: ③ 审计查询与汇总
#   name_en: query/get_summary/list_sessions/export_jsonl
#   intro: 按 session 读回全部 JSONL 行，聚合成本/token/错误/决策计数
#   desc: query 逐行 json.loads；get_summary 对记录做 Σtotal_cost_usd/Σtotal_tokens/Σerror_count/Σdecisions_count 聚合；list_sessions 列目录 *.jsonl stem 排序；export_jsonl 原文返回
#   inputs: I2
#   outputs: list[dict] / summary dict
# 层: 输出
# - id: O1
#   name_zh: 会话审计JSONL文件
#   name_en: {session_id}.jsonl
#   intro: audit_dir 下按消毒后 session_id 命名的不可变追加式审计日志文件
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 查询与汇总结果
#   name_en: query/get_summary 返回字典
#   intro: 读回的审计记录列表与按会话聚合的成本/token/错误/决策统计
#   downstream: 无下游/内部使用
# - id: O3
#   name_zh: 全局审计事件
#   name_en: AuditWriterProtocol.write
#   intro: 经依赖注入 registry 转发给 L2 governance 审计写入器的 session_record 事件（best-effort）
#   downstream: governance 层 zephyr.gov_audit.writer（运行时注入，非 import 依赖）
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# I3 --> A2
# A2 --> O1
# A2 --> O3
# A2 --> A3
# I2 --> A3
# A3 --> O2
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class AuditWriterProtocol(Protocol):
    """全局审计写入器协议（5.174-M6 依赖倒置）。

    shared 层禁止向上 import governance（NO-UPWARD-IMPORT）——全局审计写入能力
    由 L2 `zephyr.gov_audit.writer` 实现，并在其模块 import 时经
    `register_audit_writer_provider()` 注入本模块；运行时通过 registry 查找，
    未注册时跳过全局审计事件（best-effort，对齐原 ImportError 容错语义）。
    """

    def write(self, record: dict[str, Any]) -> None:
        """写入一条审计事件。"""
        ...


# 运行时 registry：governance 层注入的 AuditWriter 工厂（签名对齐 get_audit_writer）
_audit_writer_provider: Callable[[], AuditWriterProtocol] | None = None


def register_audit_writer_provider(provider: Callable[[], AuditWriterProtocol] | None) -> None:
    """注册/注销全局审计写入器工厂——由 governance 层（gov_audit.writer）import 时调用。"""
    global _audit_writer_provider
    _audit_writer_provider = provider


@dataclass
class PromptRecord:
    """单次 prompt 记录。"""

    timestamp: str
    role: str
    content_preview: str
    token_count: int = 0


@dataclass
class DecisionRecord:
    """单次决策记录。"""

    timestamp: str
    decision_id: str
    summary: str
    rationale: str
    alternatives: list[str] = field(default_factory=list)


@dataclass
class ToolCallRecord:
    """单次工具调用记录。"""

    timestamp: str
    tool_name: str
    parameters_preview: str
    result_summary: str
    duration_ms: float = 0.0
    success: bool = True


@dataclass
class CostRecord:
    """单次成本记录。"""

    timestamp: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class ErrorRecord:
    """单次错误记录。"""

    timestamp: str
    error_type: str
    message: str
    recovery_action: str = ""
    recovered: bool = False


@dataclass
class OutcomeRecord:
    """最终产出记录。"""

    timestamp: str
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    tests_run: int = 0
    tests_passed: int = 0
    knowledge_extracted: int = 0
    deviations_found: int = 0


@dataclass
class SessionRecord:
    """一次 AI session 的完整审计记录。

    与 GOV-AI-007 Session Log Schema 字段对齐。
    """

    session_id: str
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    ended_at: str | None = None

    prompts: list[PromptRecord] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    costs: list[CostRecord] = field(default_factory=list)
    errors: list[ErrorRecord] = field(default_factory=list)
    outcomes: OutcomeRecord | None = None

    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def total_cost_usd(self) -> float:
        return sum(c.cost_usd for c in self.costs)

    @property
    def total_tokens(self) -> int:
        return sum(c.input_tokens + c.output_tokens for c in self.costs)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def recovered_count(self) -> int:
        return sum(1 for e in self.errors if e.recovered)

    def add_prompt(self, role: str, content: str, token_count: int = 0) -> PromptRecord:
        preview = content[:200] + "..." if len(content) > 200 else content
        record = PromptRecord(
            timestamp=datetime.now(UTC).isoformat(),
            role=role,
            content_preview=preview,
            token_count=token_count,
        )
        self.prompts.append(record)
        return record

    def add_decision(
        self, decision_id: str, summary: str, rationale: str, alternatives: list[str] | None = None
    ) -> DecisionRecord:
        record = DecisionRecord(
            timestamp=datetime.now(UTC).isoformat(),
            decision_id=decision_id,
            summary=summary,
            rationale=rationale,
            alternatives=alternatives or [],
        )
        self.decisions.append(record)
        return record

    def add_tool_call(
        self, tool_name: str, params: str, result: str, duration_ms: float = 0.0, success: bool = True
    ) -> ToolCallRecord:
        record = ToolCallRecord(
            timestamp=datetime.now(UTC).isoformat(),
            tool_name=tool_name,
            parameters_preview=params[:200],
            result_summary=result[:200],
            duration_ms=duration_ms,
            success=success,
        )
        self.tool_calls.append(record)
        return record

    def add_cost(
        self, provider: str, model: str, input_tokens: int = 0, output_tokens: int = 0, cost_usd: float = 0.0
    ) -> CostRecord:
        record = CostRecord(
            timestamp=datetime.now(UTC).isoformat(),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
        self.costs.append(record)
        return record

    def add_error(
        self, error_type: str, message: str, recovery_action: str = "", recovered: bool = False
    ) -> ErrorRecord:
        record = ErrorRecord(
            timestamp=datetime.now(UTC).isoformat(),
            error_type=error_type,
            message=message,
            recovery_action=recovery_action,
            recovered=recovered,
        )
        self.errors.append(record)
        return record

    def set_outcomes(self, **kwargs: Any) -> OutcomeRecord:
        self.outcomes = OutcomeRecord(
            timestamp=datetime.now(UTC).isoformat(),
            **kwargs,
        )
        return self.outcomes

    def finish(self) -> None:
        self.ended_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "prompts_count": len(self.prompts),
            "decisions_count": len(self.decisions),
            "tool_calls_count": len(self.tool_calls),
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_tokens": self.total_tokens,
            "error_count": self.error_count,
            "recovered_count": self.recovered_count,
            "prompts": [
                {"ts": p.timestamp, "role": p.role, "preview": p.content_preview, "tokens": p.token_count}
                for p in self.prompts
            ],
            "decisions": [
                {"ts": d.timestamp, "id": d.decision_id, "summary": d.summary, "rationale": d.rationale}
                for d in self.decisions
            ],
            "tool_calls": [
                {
                    "ts": t.timestamp,
                    "tool": t.tool_name,
                    "params": t.parameters_preview,
                    "result": t.result_summary,
                    "duration_ms": t.duration_ms,
                    "success": t.success,
                }
                for t in self.tool_calls
            ],
            "costs": [
                {
                    "ts": c.timestamp,
                    "provider": c.provider,
                    "model": c.model,
                    "input": c.input_tokens,
                    "output": c.output_tokens,
                    "cost_usd": c.cost_usd,
                }
                for c in self.costs
            ],
            "errors": [
                {
                    "ts": e.timestamp,
                    "type": e.error_type,
                    "message": e.message,
                    "recovery": e.recovery_action,
                    "recovered": e.recovered,
                }
                for e in self.errors
            ],
        }
        if self.outcomes:
            result["outcomes"] = {
                "files_created": self.outcomes.files_created,
                "files_modified": self.outcomes.files_modified,
                "tests_run": self.outcomes.tests_run,
                "tests_passed": self.outcomes.tests_passed,
                "knowledge_extracted": self.outcomes.knowledge_extracted,
                "deviations_found": self.outcomes.deviations_found,
            }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class SessionAuditTrail:
    """Session 审计轨迹管理器——JSONL 格式追加写入。

    Usage::

        trail = SessionAuditTrail(audit_dir="logs/audit/")
        record = trail.start_session("session-20260507-001")
        record.add_decision("D1", "Use SQLite", "Lightweight, zero-config")
        trail.append_record(record)
        results = trail.query("session-20260507-001")
    """

    def __init__(self, audit_dir: str = "logs/session_audit/"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    @staticmethod
    def _sanitize_session_id(session_id: str) -> str:
        return session_id.replace("\\", "_").replace("/", "_").replace("..", "_")

    def _session_path(self, session_id: str) -> Path:
        safe_id = self._sanitize_session_id(session_id)
        return self.audit_dir / f"{safe_id}.jsonl"

    def start_session(self, session_id: str) -> SessionRecord:
        return SessionRecord(session_id=session_id)

    def append_record(self, record: SessionRecord) -> Path:
        filepath = self._session_path(record.session_id)
        record_dict = record.to_dict()
        with self._lock, open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_dict, ensure_ascii=False) + "\n")
        # 5.174-M6：全局审计事件经注入的 provider 写入（runtime registry 查找），
        # 不再延迟 import zephyr.gov_audit.writer——L0→L2 向上依赖已消除。
        provider = _audit_writer_provider
        if provider is None:
            logger.debug("session_audit: no audit writer provider registered, skipping global audit event")
        else:
            try:
                provider().write(
                    {
                        "event_type": "session_record",
                        "action_type": "session_record",
                        "agent_id": record_dict.get("session_id", "unknown"),
                        "session_id": record_dict.get("session_id", ""),
                        "target_path": str(filepath),
                        "operation": "append_record",
                    }
                )
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in session_audit", exc_info=True)
        return filepath

    def query(self, session_id: str) -> list[dict[str, Any]]:
        filepath = self._session_path(session_id)
        if not filepath.exists():
            return []
        results: list[dict[str, Any]] = []
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
        return results

    def export_jsonl(self, session_id: str) -> str:
        filepath = self._session_path(session_id)
        if not filepath.exists():
            return ""
        with open(filepath, encoding="utf-8") as f:
            return f.read()

    def list_sessions(self) -> list[str]:
        sessions: list[str] = []
        for f in self.audit_dir.glob("*.jsonl"):
            sessions.append(f.stem)
        return sorted(sessions)

    def get_summary(self, session_id: str) -> dict[str, Any]:
        records = self.query(session_id)
        if not records:
            return {"session_id": session_id, "record_count": 0}
        total_cost = sum(r.get("total_cost_usd", 0) for r in records)
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        total_errors = sum(r.get("error_count", 0) for r in records)
        total_decisions = sum(r.get("decisions_count", 0) for r in records)
        return {
            "session_id": session_id,
            "record_count": len(records),
            "total_cost_usd": round(total_cost, 6),
            "total_tokens": total_tokens,
            "total_errors": total_errors,
            "total_decisions": total_decisions,
        }


__all__ = [
    "AuditWriterProtocol",
    "CostRecord",
    "DecisionRecord",
    "ErrorRecord",
    "OutcomeRecord",
    "PromptRecord",
    "SessionAuditTrail",
    "SessionRecord",
    "ToolCallRecord",
    "register_audit_writer_provider",
]
