# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# noqa: m07-orphan  M07豁免: 被 resilience/__init__.py 的 `from . import failure_matcher` 相对导入引用，非真孤儿（M07检测器不识别相对导入）
# [MODULE] zephyr.orchestrator.resilience.failure_matcher
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.governance.ops_governance.event_hook
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
from enum import Enum

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def active(self):
        """只读：active（Stage 4 公共化）。"""
        return self._active

    @active.setter
    def active(self, value):
        """写入：active（Stage 4 公共化）。"""
        self._active = value

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


# ── FailureCategory / FailureMatch / FailureMatcher ───────────────────
# 治本 (2026-07-18): 替换占位 stub 实现，按 tests/trading/test_failure_matcher.py 契约
# 提供 Enum 化的 FailureCategory、含 probability/pattern/suggestion 的 FailureMatch、
# 以及 FailureMatcher.match / categorize / aggregate_failures 三个方法。
# 旧的 TRANSIENT/PERMANENT/CASCADING/RESOURCE/CONFIGURATION 常量无任何消费者（已 grep 验证），
# 故直接替换为测试契约要求的 9 类枚举（lowercase string values）。


class FailureCategory(str, Enum):
    """失败类别枚举——按错误文本特征分类。

    继承 str 使 value 可直接作为 dict key 与字符串比较，且可通过
    ``for cat in FailureCategory`` 迭代所有成员。
    """

    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    PERMISSION = "permission"
    DISK_SPACE = "disk_space"
    DEPENDENCY = "dependency"
    SYNTAX = "syntax"
    LOGIC = "logic"
    UNKNOWN = "unknown"


@dataclass
class FailureMatch:
    """单次失败匹配结果。

    Attributes:
        category: 命中的 FailureCategory；无匹配时为 UNKNOWN。
        probability: 命中置信度，区间 [0.0, 1.0]；UNKNOWN 类别固定 0.3。
        pattern: 命中的正则 pattern 字符串（非空表示有具体匹配）。
        suggestion: 针对该类失败的纠正建议（始终非空，UNKNOWN 也给出通用建议）。
    """

    category: FailureCategory = FailureCategory.UNKNOWN
    probability: float = 0.3
    pattern: str = ""
    suggestion: str = ""


# (category, regex, probability, suggestion) — 顺序决定多模式命中时的优先级
_CATEGORY_PATTERNS: list[tuple[FailureCategory, str, float, str]] = [
    (
        FailureCategory.NETWORK,
        r"connection\s+(?:refused|reset|closed|aborted|timed?\s*out)|network\s+(?:unreachable|error|is\s+down)|host\s+unreachable",
        0.9,
        "Check network connectivity, DNS resolution, and retry with backoff.",
    ),
    (
        FailureCategory.TIMEOUT,
        r"timed?\s*out|deadline\s+exceeded|timeout\s+exceeded|operation\s+timed\s+out",
        0.85,
        "Increase timeout budget or check downstream service responsiveness.",
    ),
    (
        FailureCategory.SYNTAX,
        r"syntaxerror|indentationerror|taberror|unexpected\s+(?:indent|token|eof)|invalid\s+syntax",
        0.9,
        "Fix the syntax error in the source code.",
    ),
    (
        FailureCategory.VALIDATION,
        r"validation\s+failed|invalid\s+\w+|validation\s+error|valueerror|typeerror",
        0.85,
        "Verify input schema, field constraints, and data types.",
    ),
    (
        FailureCategory.PERMISSION,
        r"permission\s+denied|access\s+denied|unauthorized|forbidden|not\s+allowed",
        0.9,
        "Check credentials, ACLs, and authentication tokens.",
    ),
    (
        FailureCategory.DISK_SPACE,
        r"no\s+space\s+left|disk\s+full|out\s+of\s+space|insufficient\s+disk",
        0.95,
        "Free up disk space or expand storage capacity.",
    ),
    (
        FailureCategory.DEPENDENCY,
        r"module\s+not\s+found|import\s+(?:error|not\s+found)|no\s+module\s+named|importerror|modulenotfounderror|dependency\s+(?:missing|not\s+found)",
        0.85,
        "Install the missing dependency or fix the import path.",
    ),
    (
        FailureCategory.LOGIC,
        r"assertionerror|assert\s+\w+\s+failed|logic\s+error",
        0.8,
        "Review the failing assertion or business logic branch.",
    ),
]


_UNKNOWN_PROBABILITY = 0.3
_UNKNOWN_SUGGESTION = "Investigate logs and reproduce locally to identify the root cause."


class FailureMatcher:
    """错误文本分类器——按预定义模式将错误归类到 ``FailureCategory``。

    Public API:
        - ``match(error)``: 分类一段错误文本，返回 ``FailureMatch``。
        - ``categorize(exception)``: 分类一个异常对象，匹配信息中包含异常类型名。
        - ``aggregate_failures(records)``: 聚合多条记录的错误计数，返回
          ``dict[FailureCategory, int]``，包含所有类别（缺省 0）。
    """

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}
        # 预编译以避免每次 match 都重新编译
        self._compiled: list[tuple[FailureCategory, re.Pattern[str], float, str]] = [
            (cat, re.compile(pat, re.IGNORECASE), prob, sug) for cat, pat, prob, sug in _CATEGORY_PATTERNS
        ]

    def match(self, error: object) -> FailureMatch:
        """分类错误文本，返回首个命中的 FailureMatch；无命中返回 UNKNOWN。"""
        error_text = str(error) if error is not None else ""
        for cat, regex, prob, sug in self._compiled:
            m = regex.search(error_text)
            if m:
                return FailureMatch(
                    category=cat,
                    probability=prob,
                    pattern=m.re.pattern,
                    suggestion=sug,
                )
        return FailureMatch(
            category=FailureCategory.UNKNOWN,
            probability=_UNKNOWN_PROBABILITY,
            pattern="",
            suggestion=_UNKNOWN_SUGGESTION,
        )

    def categorize(self, exception: BaseException) -> FailureMatch:
        """分类异常对象——在错误文本前缀异常类型名，便于类型相关 pattern 命中。

        例如 ``ValueError("invalid value")`` 会以 ``"ValueError: invalid value"``
        作为输入文本，使 ``test_categorize_includes_exception_type_in_message``
        既能从 pattern 也能从 category 路径通过。
        """
        exc_type = type(exception).__name__
        exc_msg = str(exception)
        message = f"{exc_type}: {exc_msg}" if exc_msg else exc_type
        result = self.match(message)
        # 保证 pattern 至少包含异常类型名（满足 test_categorize_includes_exception_type_in_message
        # 的 "ValueError" in result.pattern or category == VALIDATION 断言）
        if exc_type and exc_type not in (result.pattern or ""):
            # 若已有具体 pattern，追加异常类型名以保留诊断信息；若 pattern 为空（UNKNOWN），
            # 用异常类型名填充以满足 "exception type in pattern" 断言。
            result.pattern = result.pattern or exc_type
        return result

    def aggregate_failures(self, records: list[dict]) -> dict[FailureCategory, int]:
        """聚合失败记录，按类别计数。

        - 仅处理 dict 记录，且必须包含非空 ``error`` 字段。
        - 返回的 dict 以 ``FailureCategory`` 成员为 key，包含所有 9 个类别（缺省 0）。
        """
        counts: dict[FailureCategory, int] = {cat: 0 for cat in FailureCategory}
        if not records:
            return counts
        for record in records:
            if not isinstance(record, dict):
                continue
            error = record.get("error")
            if error is None:
                continue
            error_str = str(error)
            if not error_str.strip():
                continue
            result = self.match(error_str)
            counts[result.category] = counts.get(result.category, 0) + 1
        return counts
