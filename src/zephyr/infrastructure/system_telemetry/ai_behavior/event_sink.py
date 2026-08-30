# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.ai_behavior.event_sink
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ai_behavior字段命名MUST可映射到OTel gen_ai.*属性;独立ring buffer+独立SQLite表;FeatureFlag控制
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/system-telemetry/blueprint.md;src/zephyr/system-telemetry/facade.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeatureFlag OFF->noop;ring buffer满->丢弃最旧
# [TESTS] tests/infrastructure/
# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
遥测 · ai_behavior/event_sink — AI 行为遥测事件管道。

蓝图 §7: 7 大监测维度 + B37 Error Taxonomy + OTel GenAI Semantic Conventions 对齐。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ctx 参数
#   fields: 参数 ctx，类型注解 ErrorContext
#   code: event_sink.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: model_name 参数
#   fields: 参数 model_name，类型注解 str
#   code: event_sink.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: task_type 参数
#   fields: 参数 task_type，类型注解 str
#   code: event_sink.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: module_id 参数
#   fields: 参数 module_id，类型注解 str
#   code: event_sink.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ErrorContext
#   name_en: ErrorContext
#   intro: class ErrorContext 源码 L118-L137
#   desc: 公共方法（定义序）: snapshot；源码 L118-L137
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② validate_error_context
#   name_en: validate_error_context
#   intro: validate_error_context(ctx) 源码 L146-L156
#   desc: 源码 L146-L156
#   inputs: ctx
#   outputs: list[str]
# - id: A3
#   name_zh: ③ AIBehaviorEvent
#   name_en: AIBehaviorEvent
#   intro: class AIBehaviorEvent 源码 L160-L274
#   desc: 公共方法（定义序）: total_tokens, token_efficiency, is_suspicious, snapshot；源码 L160-L274
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ emit_ai_behavior_event
#   name_en: emit_ai_behavior_event
#   intro: emit_ai_behavior_event(model_name, task_type, module_id, in…
#   desc: 源码 L277-L321
#   inputs: model_name task_type module_id input_tokens output_tokens cost_usd de…
#   outputs: AIBehaviorEvent
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# - id: O2
#   name_zh: AIBehaviorEvent
#   name_en: AIBehaviorEvent
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
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
# A4 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

_ring_lock = threading.Lock()
ring_lock = _ring_lock  # public alias（Stage 4 公共化）

_event_ring: list[dict[str, Any]] = []
event_ring = _event_ring  # public alias（Stage 4 公共化）

_EVENT_RING_MAX = 1000


@dataclass
class ErrorContext:
    error_type: str
    persistence: str
    source: str
    expectation: str = "unexpected"
    severity: str = "blocking"
    retries: int = 0
    backoff_ms: float = 0.0
    detail: str = ""

    def snapshot(self) -> dict[str, Any]:
        return {
            "error_type": self.error_type,
            "persistence": self.persistence,
            "source": self.source,
            "expectation": self.expectation,
            "severity": self.severity,
            "retries": self.retries,
            "backoff_ms": self.backoff_ms,
        }


_VALID_PERSISTENCE: frozenset[str] = frozenset({"transient", "permanent", "intermittent"})  # noqa: gate-vocab  无对应词表真源（无 error-persistence 词表），错误持续性分类为本地常量
_VALID_SOURCE: frozenset[str] = frozenset({"client", "server", "dependency", "internal"})  # noqa: gate-vocab  无对应词表真源（无 error-source 词表），错误来源分类为本地常量
_VALID_EXPECTATION: frozenset[str] = frozenset({"expected", "unexpected", "unknown"})  # noqa: gate-vocab  无对应词表真源（无 error-expectation 词表），错误预期性分类为本地常量
_VALID_SEVERITY: frozenset[str] = frozenset({"degraded", "blocking", "fatal"})  # noqa: gate-vocab  无对应词表真源（无 error-severity 词表），错误严重度分类为本地常量，非 safety_level 词表域


def validate_error_context(ctx: ErrorContext) -> list[str]:
    issues: list[str] = []
    if ctx.persistence not in _VALID_PERSISTENCE:
        issues.append(f"persistence={ctx.persistence}")
    if ctx.source not in _VALID_SOURCE:
        issues.append(f"source={ctx.source}")
    if ctx.expectation not in _VALID_EXPECTATION:
        issues.append(f"expectation={ctx.expectation}")
    if ctx.severity not in _VALID_SEVERITY:
        issues.append(f"severity={ctx.severity}")
    return issues


@dataclass
class AIBehaviorEvent:
    event_id: str = field(
        default_factory=lambda: hashlib.sha256(f"{time.time_ns()}:{threading.get_ident()}".encode()).hexdigest()[:16]
    )
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    model_name: str = "unknown"
    model_version: str = "unknown"
    task_type: str = "unknown"
    module_id: str = "unknown"
    prompt_template_id: str = "unknown"
    prompt_version: str = "unknown"

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    decision_point: str = ""
    options_evaluated: list[str] = field(default_factory=list)
    chosen_option: str = ""
    rationale: str = ""
    backtrack_count: int = 0

    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_error_rate: float = 0.0

    gate_rejects: dict[str, int] = field(default_factory=dict)
    gate_bypass_detected: bool = False
    gate_latency_ms: dict[str, float] = field(default_factory=dict)

    output_consistency_score: float = 1.0
    factual_consistency_score: float = 1.0
    lint_error_count: int = 0

    error_context: ErrorContext | None = None
    human_escalation: bool = False

    rate_limit_hit: bool = False
    rate_limit_retries: int = 0
    rate_limit_backoff_ms: float = 0.0

    custom_labels: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def token_efficiency(self) -> float:
        if self.input_tokens == 0:
            return 0.0
        return self.output_tokens / self.input_tokens

    @property
    def is_suspicious(self) -> bool:
        flags = 0
        if self.token_efficiency < 0.2:
            flags += 1
        if self.factual_consistency_score < 0.7:
            flags += 1
        if self.backtrack_count > 3:
            flags += 1
        if self.gate_bypass_detected:
            flags += 1
        if self.error_context is not None and self.error_context.severity == "fatal":
            flags += 1
        return flags >= 2

    def snapshot(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "ts": self.timestamp,
            "model": {"name": self.model_name, "version": self.model_version},
            "task": {"type": self.task_type, "module_id": self.module_id},
            "prompt": {
                "template_id": self.prompt_template_id,
                "version": self.prompt_version,
            },
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
                "efficiency": round(self.token_efficiency, 4),
            },
            "cost_usd": self.cost_usd,
            "decision": {
                "point": self.decision_point,
                "options_evaluated": self.options_evaluated,
                "chosen": self.chosen_option,
                "rationale": self.rationale,
                "backtracks": self.backtrack_count,
            },
            "tools": {
                "calls": self.tool_calls,
                "error_rate": self.tool_error_rate,
            },
            "gates": {
                "rejects": self.gate_rejects,
                "bypass": self.gate_bypass_detected,
                "latency_ms": self.gate_latency_ms,
            },
            "quality": {
                "output_consistency": self.output_consistency_score,
                "factual_consistency": self.factual_consistency_score,
                "lint_errors": self.lint_error_count,
            },
            "error": (self.error_context.snapshot() if self.error_context else None),
            "rate_limit": {
                "hit": self.rate_limit_hit,
                "retries": self.rate_limit_retries,
                "backoff_ms": self.rate_limit_backoff_ms,
            },
            "human_escalation": self.human_escalation,
            "suspicious": self.is_suspicious,
            "labels": self.custom_labels,
        }


def emit_ai_behavior_event(
    model_name: str = "unknown",
    task_type: str = "unknown",
    module_id: str = "unknown",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    decision_point: str = "",
    chosen_option: str = "",
    rationale: str = "",
    tool_calls: list[dict[str, Any]] | None = None,
    error_context: ErrorContext | None = None,
    **labels: Any,
) -> AIBehaviorEvent:
    event = AIBehaviorEvent(
        model_name=model_name,
        task_type=task_type,
        module_id=module_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
        decision_point=decision_point,
        chosen_option=chosen_option,
        rationale=rationale,
        tool_calls=list(tool_calls or []),
        error_context=error_context,
        custom_labels=dict(labels),
    )

    snapshot = event.snapshot()

    with _ring_lock:
        _event_ring.append(snapshot)
        if len(_event_ring) > _EVENT_RING_MAX:
            _event_ring.pop(0)

    if os.environ.get("ZALPHA_AI_BEHAVIOR_TELEMETRY", "1") == "1":
        try:
            from zephyr.infrastructure.system_telemetry.logs.structured_sink import append_jsonl_record

            append_jsonl_record(snapshot, labels={"__type": "ai_behavior_event"})
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("suppressed error in event_sink", exc_info=True)

    return event
