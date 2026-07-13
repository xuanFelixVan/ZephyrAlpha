# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.resilience.failure_matcher
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.governance.ops_governance.event_hook
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_failure_matcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
FailurePatternMatcher — 任务失败模式识别与纠正建议
=====================================================
Blueprint: MOD-TASK_SYSTEM 盲点#22
依赖: EventHook (订阅 FAILED 状态)

通过 EventHook 订阅 task FAILED，分析失败原因并生成纠正建议。

Usage:
    from zephyr.orchestrator.resilience.failure_matcher import FailurePatternMatcher
    matcher = FailurePatternMatcher()
    matcher.activate()
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger("zephyr.failure_matcher")


@dataclass
class FailureDiagnosis:
    task_id: str
    pattern_name: str
    severity: str  # "low" | "medium" | "high" | "critical"
    suggestion: str
    automatic_recovery: bool = False
    metadata: dict = field(default_factory=dict)


# ── Pattern definitions ──────────────────────────────────────────────

_FAILURE_PATTERNS: list[dict] = [
    {
        "name": "iterative_retry_loop",
        "severity": "high",
        "regex": r"(retry|再次尝试|第\s*\d+\s*次)",
        "suggestion": "检测到迭代重试循环——建议暂停、检查是否模型幻觉、降低 temperature 或切换模型重试。",
        "automatic_recovery": False,
    },
    {
        "name": "context_insufficient",
        "severity": "medium",
        "regex": r"(context|token.*limit|超出.*上下文|truncat)",
        "suggestion": "上下文不足——建议拆分为更小的原子任务、或使用 Context Window 裁剪策略。",
        "automatic_recovery": False,
    },
    {
        "name": "multi_module_failure",
        "severity": "critical",
        "regex": r"(多个.*模块|跨模块.*失败|multi.*module)",
        "suggestion": "多模块级联失败——暂停全线，检查上游依赖的 CT-* 契约对齐性。",
        "automatic_recovery": False,
    },
    {
        "name": "schema_mismatch",
        "severity": "medium",
        "regex": r"(schema|字段.*缺失|field.*missing|类型.*不匹配|validation error)",
        "suggestion": "Schema 或字段不匹配——检查字段对齐并执行 Schema 版本迁移。",
        "automatic_recovery": False,
    },
    {
        "name": "gate_violation",
        "severity": "high",
        "regex": r"(gate|门禁|violation|G\d)",
        "suggestion": "门禁检查失败——检查 G1-G7 不变式违规详情，补齐缺失字段/上下文后手动重试。",
        "automatic_recovery": False,
    },
    {
        "name": "dependency_freshness",
        "severity": "medium",
        "regex": r"(stale|过期|依赖.*变更|dependency.*outdated)",
        "suggestion": "依赖新鲜度过期——上游蓝图已更新，需重新获取最新依赖并重建上下文。",
        "automatic_recovery": False,
    },
    {
        "name": "timeout_exceeded",
        "severity": "low",
        "regex": r"(timeout|超时|timed out|耗时.*分钟)",
        "suggestion": "任务超时——考虑拆分任务、增加 timeout 上限、或使用 faster model。",
        "automatic_recovery": True,
    },
]


class FailurePatternMatcher:
    """失败模式匹配器——分析 FAILED 事件并生成诊断报告。"""

    def __init__(self) -> None:
        self._active = False
        self._diagnoses: list[FailureDiagnosis] = []

    def activate(self) -> None:
        if self._active:
            return
        try:
            from zephyr.governance.ops_governance.event_hook import hook_registry

            hook_registry.register(
                self._on_transition,
                priority=10,
                name="failure-pattern-matcher",
            )
            self._active = True
            logger.info("FailurePatternMatcher activated")
        except ImportError:
            logger.warning("Cannot activate FailurePatternMatcher: hooks not available")

    def deactivate(self) -> None:
        if not self._active:
            return
        try:
            from zephyr.governance.ops_governance.event_hook import hook_registry

            hook_registry.unregister(self._on_transition)
        except ImportError:
            pass
        self._active = False

    def analyze(self, task_id: str, error_text: str) -> FailureDiagnosis | None:
        """分析一条错误文本并返回诊断。"""
        error_lower = error_text.lower()
        best: FailureDiagnosis | None = None
        best_severity = 99

        for pat in _FAILURE_PATTERNS:
            if re.search(pat["regex"], error_text, re.IGNORECASE):
                sev_weight = {"low": 3, "medium": 2, "high": 1, "critical": 0}.get(pat["severity"], 3)
                if sev_weight < best_severity:
                    best = FailureDiagnosis(
                        task_id=task_id,
                        pattern_name=pat["name"],
                        severity=pat["severity"],
                        suggestion=pat["suggestion"],
                        automatic_recovery=pat["automatic_recovery"],
                        metadata={"matched_text": error_text[:150]},
                    )
                    best_severity = sev_weight

        if best is not None:
            self._diagnoses.append(best)
        return best

    def diagnoses(self) -> list[FailureDiagnosis]:
        return list(self._diagnoses)

    def clear_diagnoses(self) -> None:
        self._diagnoses.clear()

    # ── internal ─────────────────────────────────────────────────

    def _on_transition(self, event) -> None:
        """EventHook 回调：当任务进入 FAILED 时触发分析。"""
        if event.to_status != "failed":
            return
        diagnosis = self.analyze(event.task_id, event.note or "")
        if diagnosis is not None:
            sev_icon = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}.get(diagnosis.severity, "❓")
            logger.warning(
                "%s [%s] %s — %s",
                sev_icon,
                diagnosis.pattern_name,
                event.task_id,
                diagnosis.suggestion,
            )


class FailureCategory:
    TRANSIENT = "TRANSIENT"
    PERMANENT = "PERMANENT"
    CASCADING = "CASCADING"
    TIMEOUT = "TIMEOUT"
    RESOURCE = "RESOURCE"
    DEPENDENCY = "DEPENDENCY"
    CONFIGURATION = "CONFIGURATION"
    UNKNOWN = "UNKNOWN"


class FailureMatch:
    def __init__(self, error="", category=None, confidence=0.0, suggested_action=""):
        self.error = error
        self.category = category
        self.confidence = confidence
        self.suggested_action = suggested_action


class FailureMatcher:
    def __init__(self, config=None):
        self.config = config or {}

    def match(self, error):
        return FailureMatch(error=str(error))
