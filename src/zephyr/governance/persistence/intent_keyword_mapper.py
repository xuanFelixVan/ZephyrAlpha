# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
# [MODULE] zephyr.governance.persistence.intent_keyword_mapper
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
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
# [A_module] module_id=MOD-ORC_intent_keyword_mapper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
IntentKeywordMapper - Stage 1 of three-stage intent parsing (
=========================================================================
Task ID : T-2-21
safety_level : L

Stage 1: keyword dictionary matching with jieba tokenization.
10 domains (D0-D9) x >= 20 keywords per domain.
P95 latency < 5ms, zero API cost.

Cascading logic:
  confidence >= 0.75  -> return directly
  confidence < 0.75   -> fallback hint for Stage 2 (when available)

Data contract ( section 4.3):
  IntentResult with primary_domain, confidence, source_stage, etc.
"""

from __future__ import annotations

import re
import time
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG

__all__ = [
    "MAP",
    "IntentDomain",
    "IntentKeywordMapper",
    "IntentResult",
    "StageLiteral",
    "map_intent_to_keywords",
]

StageLiteral = Literal["keyword", "semantic", "llm"]

_KEYWORD_CONFIDENCE_THRESHOLD = 0.75

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "D0": [
        "meta",
        "session",
        "handoff",
        "log",
        "status",
        "init",
        "bootstrap",
        "startup",
        "overview",
        "dashboard",
        "system",
        "config",
        "setup",
        "register",
        "index",
        "summary",
        "report",
        "context",
        "health",
        "check",
    ],
    "D1": [
        "data",
        "source",
        "ingest",
        "connector",
        "normalize",
        "quality",
        "storage",
        "fetch",
        "download",
        "api",
        "feed",
        "stream",
        "csv",
        "json",
        "parquet",
        "database",
        "import",
        "export",
        "pipeline",
        "etl",
    ],
    "D2": [
        "architecture",
        "blueprint",
        "design",
        "module",
        "component",
        "interface",
        "layer",
        "adr",
        "decision",
        "review",
        "structure",
        "diagram",
        "spec",
        "specification",
        "contract",
        "dependency",
        "coupling",
        "cohesion",
        "pattern",
        "rationale",
    ],
    "D3": [
        "factor",
        "alpha",
        "signal",
        "indicator",
        "feature",
        "momentum",
        "mean",
        "reversion",
        "volatility",
        "volume",
        "price",
        "return",
        "sharpe",
        "sortino",
        "ic",
        "rank",
        "zscore",
        "neutralize",
        "decay",
        "lag",
    ],
    "D4": [
        "strategy",
        "backtest",
        "trading",
        "portfolio",
        "position",
        "entry",
        "exit",
        "signal",
        "order",
        "execution",
        "profit",
        "loss",
        "drawdown",
        "benchmark",
        "alpha",
        "beta",
        "correlation",
        "regime",
        "regime-switch",
        "trend",
    ],
    "D5": [
        "risk",
        "stop",
        "loss",
        "limit",
        "budget",
        "exposure",
        "var",
        "cvar",
        "drawdown",
        "margin",
        "leverage",
        "concentration",
        "correlation",
        "stress",
        "scenario",
        "hedge",
        "protect",
        "safeguard",
        "threshold",
        "breach",
    ],
    "D6": [
        "governance",
        "audit",
        "compliance",
        "standard",
        "policy",
        "rule",
        "sentinel",
        "scan",
        "violation",
        "contradiction",
        "ssot",
        "registry",
        "inventory",
        "controlled",
        "document",
        "validate",
        "verify",
        "check",
        "gate",
        "enforce",
    ],
    "D7": [
        "analytics",
        "report",
        "metric",
        "performance",
        "attribution",
        "pnl",
        "return",
        "benchmark",
        "tearsheet",
        "analysis",
        "statistics",
        "distribution",
        "correlation",
        "regression",
        "chart",
        "visualization",
        "dashboard",
        "monitor",
        "alert",
        "kpi",
    ],
    "D8": [
        "human",
        "interface",
        "chat",
        "prompt",
        "command",
        "cli",
        "terminal",
        "input",
        "output",
        "display",
        "notification",
        "alert",
        "message",
        "feedback",
        "interaction",
        "conversation",
        "query",
        "request",
        "response",
        "dialogue",
    ],
    "D9": [
        "debug",
        "fix",
        "error",
        "bug",
        "issue",
        "troubleshoot",
        "diagnose",
        "repair",
        "patch",
        "hotfix",
        "crash",
        "exception",
        "traceback",
        "log",
        "fail",
        "broken",
        "corrupt",
        "recover",
        "rollback",
        "restore",
    ],
}

_DIRECTIVE_MAP: dict[str, list[str]] = {
    "D0": ["000", "999"],
    "D1": ["111", "999"],
    "D2": ["222", "244", "999"],
    "D3": ["333", "344", "999"],
    "D4": ["433", "344", "999"],
    "D5": ["555", "999"],
    "D6": ["611", "622", "999"],
    "D7": ["777", "999"],
    "D8": ["888", "999"],
    "D9": ["911", "999"],
}

_WORD_BOUNDARY_CACHE: dict[str, re.Pattern[str]] = {}


class IntentDomain(str, Enum):
    """意图识别域（D0-D9 + UNKNOWN，与 metadata_registry.yaml §9.2 domain 枚举对齐）。"""

    D0 = "D0"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"
    D6 = "D6"
    D7 = "D7"
    D8 = "D8"
    D9 = "D9"
    UNKNOWN = "UNKNOWN"


class IntentResult(BaseModel):
    model_config = BASE_CONFIG

    query: str
    primary_domain: IntentDomain = Field(description="Primary matched domain (D0-D9 or UNKNOWN)")
    secondary_domains: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list)
    source_stage: StageLiteral = Field(description="keyword, semantic, or llm")
    suggested_directives: list[str] = Field(default_factory=list)
    requires_human: bool = False
    rationale: str | None = None
    latency_ms: int = Field(ge=0)
    cost_usd: float = Field(default=0.0)
    fallback_hint: str | None = None


def _tokenize(query: str) -> list[str]:
    tokens: list[str] = []
    try:
        import jieba

        tokens = list(jieba.cut(query))
    except ImportError:
        tokens = re.findall(r"[a-zA-Z0-9]+|[\u4e00-\u9fff]", query)
    cleaned: list[str] = []
    for t in tokens:
        t = t.strip()
        if t:
            cleaned.append(t.lower())
    return cleaned


def _word_boundary_pattern(kw: str) -> re.Pattern[str]:
    pat = _WORD_BOUNDARY_CACHE.get(kw)
    if pat is None:
        pat = re.compile(r"\b" + re.escape(kw) + r"\b")
        _WORD_BOUNDARY_CACHE[kw] = pat
    return pat


class IntentKeywordMapper:
    """Stage 1 keyword-based intent mapper (

    Parameters
    ----------
    keywords : dict[str, list[str]] | None
        Domain-to-keywords mapping. Defaults to built-in _DOMAIN_KEYWORDS.
    confidence_threshold : float
        Minimum confidence to return without fallback hint.
    """

    def __init__(
        self,
        keywords: dict[str, list[str]] | None = None,
        confidence_threshold: float = _KEYWORD_CONFIDENCE_THRESHOLD,
    ) -> None:
        self._keywords = keywords or _DOMAIN_KEYWORDS
        self._threshold = confidence_threshold
        self._kw_index: dict[str, list[str]] = {}
        for domain, kws in self._keywords.items():
            for kw in kws:
                kl = kw.lower()
                domain_list = self._kw_index.setdefault(kl, [])
                if domain not in domain_list:
                    domain_list.append(domain)
        for domain in self._keywords:
            if domain not in _DIRECTIVE_MAP:
                raise ValueError(f"Domain {domain!r} has keywords but no entry in _DIRECTIVE_MAP")

    def map_intent(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> IntentResult:
        t0 = time.perf_counter()
        if not query or not query.strip():
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            return IntentResult(
                query=query,
                primary_domain=IntentDomain.UNKNOWN,
                confidence=0.0,
                matched_keywords=[],
                source_stage="keyword",
                latency_ms=elapsed_ms,
                requires_human=True,
                rationale="Empty query",
            )

        tokens = _tokenize(query)
        domain_hits: dict[str, int] = {}
        matched_keywords: list[str] = []

        for token in tokens:
            domains = self._kw_index.get(token)
            if domains is not None:
                for domain in domains:
                    domain_hits[domain] = domain_hits.get(domain, 0) + 1
                if token not in matched_keywords:
                    matched_keywords.append(token)

        query_lower = query.lower()
        for kw, domains in self._kw_index.items():
            if kw not in matched_keywords and _word_boundary_pattern(kw).search(query_lower):
                for domain in domains:
                    domain_hits[domain] = domain_hits.get(domain, 0) + 1
                matched_keywords.append(kw)

        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        if not domain_hits:
            return IntentResult(
                query=query,
                primary_domain=IntentDomain.UNKNOWN,
                confidence=0.0,
                matched_keywords=[],
                source_stage="keyword",
                latency_ms=elapsed_ms,
                fallback_hint="stage-1-only",
                rationale="No keyword match found",
            )

        sorted_domains = sorted(domain_hits.items(), key=lambda x: x[1], reverse=True)
        primary_domain = sorted_domains[0][0]
        primary_hits = sorted_domains[0][1]
        total_hits = sum(domain_hits.values())

        confidence = min(primary_hits / max(len(tokens), 1), 1.0)
        if total_hits > 1:
            confidence = min(confidence * (primary_hits / total_hits) * 1.5, 1.0)
        confidence = round(confidence, 4)

        secondary_domains = [d for d, _ in sorted_domains[1:4]]

        suggested_directives = _DIRECTIVE_MAP.get(primary_domain, ["999"])

        fallback_hint: str | None = None
        if confidence < self._threshold:
            fallback_hint = "stage-1-only"

        return IntentResult(
            query=query,
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            confidence=confidence,
            matched_keywords=matched_keywords,
            source_stage="keyword",
            suggested_directives=suggested_directives,
            requires_human=confidence < 0.3,
            rationale=f"Matched {len(matched_keywords)} keywords in domain {primary_domain}",
            latency_ms=elapsed_ms,
            cost_usd=0.0,
            fallback_hint=fallback_hint,
        )

    @property
    def domain_count(self) -> int:
        return len(self._keywords)

    @property
    def total_keywords(self) -> int:
        return sum(len(kws) for kws in self._keywords.values())

    def get_keywords_for_domain(self, domain: str) -> list[str]:
        return list(self._keywords.get(domain, []))


MAP: dict[str, list[str]] = {
    "CODE_GEN": [
        "generate",
        "create",
        "implement",
        "build",
        "write",
        "code",
        "scaffold",
        "skeleton",
        "module",
        "class",
        "function",
        "生成",
        "创建",
        "实现",
        "编写",
        "新建",
    ],
    "CODE_REVIEW": [
        "review",
        "inspect",
        "code review",
        "audit",
        "check",
        "validate",
        "verify",
        "quality",
        "审查",
        "检查",
        "校验",
    ],
    "ANALYSIS": [
        "analysis",
        "analyze",
        "report",
        "evaluate",
        "assess",
        "metric",
        "benchmark",
        "profile",
        "分析",
        "评估",
        "报告",
    ],
    "OPS_FIX": [
        "fix",
        "bug",
        "hotfix",
        "patch",
        "repair",
        "security",
        "vulnerability",
        "incident",
        "修复",
        "漏洞",
        "安全事故",
    ],
    "DOC": [
        "documentation",
        "doc",
        "readme",
        "changelog",
        "manual",
        "guide",
        "spec",
        "文档",
        "手册",
    ],
    "REFACTOR": [
        "refactor",
        "restructure",
        "rewrite",
        "cleanup",
        "optimize",
        "simplify",
        "重构",
        "重写",
    ],
    "TEST": [
        "test",
        "pytest",
        "unittest",
        "coverage",
        "mock",
        "fixture",
        "assert",
        "测试",
        "单元测试",
    ],
    "AUDIT": [
        "audit",
        "compliance",
        "governance",
        "policy",
        "standard",
        "regulation",
        "审计",
        "合规",
    ],
    "QUERY": [
        "query",
        "question",
        "search",
        "find",
        "lookup",
        "retrieve",
        "查询",
        "问题",
        "搜索",
    ],
    "DEBUG": [
        "debug",
        "troubleshoot",
        "diagnose",
        "trace",
        "log",
        "breakpoint",
        "stack trace",
        "调试",
        "排查",
    ],
}


def map_intent_to_keywords(intent: str) -> list[str]:
    """BUILD-C01 入口——将意图类型映射为检索关键词列表。

    Parameters
    ----------
    intent : str
        意图类型字符串，应为 IntentType 枚举值之一

    Returns
    -------
    list[str]
        关键词列表

    Raises
    ------
    ValueError
        若 intent 无效或映射结果为空（BUILD-C01 reject 模式）

    Examples
    --------
    >>> map_intent_to_keywords("CODE_GEN")
    ['generate', 'create', 'implement', ...]
    >>> map_intent_to_keywords("UNKNOWN")
    Traceback (most recent call last):
    ...
    ValueError: BUILD-C01: 未知意图类型 'UNKNOWN'，请补充 intent→keyword 映射到 intent_keyword_mapper.py
    """
    keywords = MAP.get(intent)
    if not keywords:
        raise ValueError(f"BUILD-C01: 未知意图类型 '{intent}'，请补充 intent→keyword 映射到 intent_keyword_mapper.py")
    return keywords
