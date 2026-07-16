# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_injector
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.autonomy_core.__init__; zephyr.security.llm_defense.llm_security.gateway
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ContextInjector: retrieve and inject relevant knowledge into prompt context
============================================================================
Task ID : T-2-12 (C39)
safety_level : L

Retrieves knowledge and assembles it into an injected context string for
prompt construction. Supports three retrieval modes:
  1. By task_id  — find KEs related to a specific task
  2. By module_id — find KEs belonging to a module
  3. By keyword  — semantic/keyword search

KB refactor (Phase 1-3 done): removed kb_repo.py SQLite layer.
inject_by_* methods return empty InjectedContext (no data source).
KB retrieval is handled by UnifiedMemoryAPI
(see zephyr.gov_kb.storage.unified_memory_api).

Respects token budget limits from ContextBudgetTracker.
"""

from __future__ import annotations

from typing import Final
import time
from enum import Enum
from pydantic import BaseModel, Field

from zephyr.infrastructure.capacity_assurance.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET, estimate_tokens
from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

__all__ = [
    "ContextInjector",
    "InjectedContext",
    "InjectionLayer",
    "InjectionResult",
    "RetrievalMode",
    "ValidatedContext",
    "format_context",
    "inject",
]


class RetrievalMode(str, Enum):
    TASK_ID = "task_id"
    MODULE_ID = "module_id"
    KEYWORD = "keyword"


class InjectedContext(BaseModel):
    model_config = BASE_CONFIG

    context: str = Field(default="", description="Assembled context string")
    sources: list[str] = Field(default_factory=list, description="Source file paths used")
    provenances: list[str] = Field(default_factory=list, description="溯源信息 {blueprint_id}:{§}/{ke_id}")
    token_count: int = Field(default=0, ge=0, description="Estimated token count")
    retrieval_mode: str = Field(description="Retrieval mode used")
    query: str = Field(default="", description="Original query string")
    budget_remaining: int = Field(default=0, ge=0, description="Remaining token budget")


class ContextInjector:
    """Retrieve and inject knowledge context.

    KB refactor (Phase 1-3 done): removed kb_repo.py; inject_by_* return empty.
    KB retrieval is handled by UnifiedMemoryAPI
    (zephyr.gov_kb.storage.unified_memory_api).

    Parameters
    ----------
    token_budget : int
        Maximum token budget for injected context (default 8000).
    max_sources : int
        Maximum number of sources to include (default 10).
    """

    def __init__(
        self,
        token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
        max_sources: int = 10,
    ) -> None:
        self._token_budget = token_budget
        self._max_sources = max_sources

    def inject_by_task_id(self, task_id: str) -> InjectedContext:
        return InjectedContext(
            retrieval_mode=RetrievalMode.TASK_ID.value,
            query=task_id,
            budget_remaining=self._token_budget,
        )

    def inject_by_module_id(self, module_id: str) -> InjectedContext:
        return InjectedContext(
            retrieval_mode=RetrievalMode.MODULE_ID.value,
            query=module_id,
            budget_remaining=self._token_budget,
        )

    def inject_by_keyword(self, keyword: str) -> InjectedContext:
        return InjectedContext(
            retrieval_mode=RetrievalMode.KEYWORD.value,
            query=keyword,
            budget_remaining=self._token_budget,
        )

    def inject(self, query: str, mode: RetrievalMode = RetrievalMode.KEYWORD) -> InjectedContext:
        if mode is RetrievalMode.TASK_ID:
            return self.inject_by_task_id(query)
        elif mode is RetrievalMode.MODULE_ID:
            return self.inject_by_module_id(query)
        else:
            return self.inject_by_keyword(query)

    @property
    def token_budget(self) -> int:
        return self._token_budget

    @property
    def max_sources(self) -> int:
        return self._max_sources


class InjectionLayer(int, Enum):
    """INJECT-C00 四层结构化注入层序（越小越底层）。

    Anti-Pattern AP3 直接破解——禁止 Flat string concat 注入。
    """

    SYSTEM = 1
    RULES = 2
    KNOWLEDGE = 3
    EXAMPLES = 4


class ValidatedContext(BaseModel):
    """Validate 阶段产物 -> Inject 阶段输入。

    由 pattern_library.validate_context() 产生，
    经四层分类后由 context_injector.inject() 注入 session。
    """

    model_config = BASE_CONFIG

    system_rules: list[str] = Field(default_factory=list, description="Layer1: AGENTS.md core rules")
    contracts: list[str] = Field(default_factory=list, description="Layer2: CT-* 合同 + blueprints")
    ke_entries: list[str] = Field(default_factory=list, description="Layer3: KE + failure_patterns")
    examples: list[str] = Field(default_factory=list, description="Layer4: 类似任务成功案例")
    token_count: int = Field(default=0, ge=0, description="验证后的 token 估算")
    is_clean: bool = Field(default=True, description="是否通过安全校验")
    validation_warnings: list[str] = Field(default_factory=list, description="校验警告")


class InjectionResult(BaseModel):
    """Inject 阶段产物——四层结构化注入结果。"""

    model_config = BASE_CONFIG

    token_count: int = Field(default=0, ge=0, description="注入的总 token 数")
    layer_tokens: dict[str, int] = Field(default_factory=dict, description="各层 token 分布")
    sources: list[str] = Field(default_factory=list, description="注入内容的来源列表")
    provenances: list[str] = Field(default_factory=list, description="DD8 溯源字段 {blueprint_id}:{§}")
    layer_count: dict[str, int] = Field(default_factory=dict, description="各层条目数")
    budget_remaining: int = Field(default=0, ge=0, description="剩余 token 预算")
    injected_successfully: bool = Field(default=True, description="注入是否成功")
    authority_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="权威分数：CE build(0.7)->Orc check(0.85)->User review(1.0)"
    )
    authority_reviewed: bool = Field(default=False, description="是否通过 authority chain review")


LAYER_HEADERS: Final[dict[str, str]] = {
    "system": "## System Core Rules (Layer1 — always-on)\n",
    "rules": "## Task-Specific Contracts & Blueprints (Layer2)\n",
    "knowledge": "## Knowledge Entries & Failure Patterns (Layer3)\n",
    "examples": "## Similar Task Success Examples (Layer4)\n",
}


def format_context(context: ValidatedContext) -> dict[str, str]:
    """将 ValidatedContext 按四层结构格式化。

    Parameters
    ----------
    context : ValidatedContext
        Validate 阶段校验通过的上下文

    Returns
    -------
    dict[str, str]
        {"system": str, "rules": str, "knowledge": str, "examples": str}
        每层是格式化的 Markdown 文本块
    """
    formatted: dict[str, str] = {}

    if context.system_rules:
        parts = [LAYER_HEADERS["system"]]
        for i, rule in enumerate(context.system_rules, 1):
            parts.append(f"{i}. {rule}\n")
        formatted["system"] = "".join(parts)

    if context.contracts:
        parts = [LAYER_HEADERS["rules"]]
        for i, contract in enumerate(context.contracts, 1):
            parts.append(f"{i}. {contract}\n")
        formatted["rules"] = "".join(parts)

    if context.ke_entries:
        parts = [LAYER_HEADERS["knowledge"]]
        for i, entry in enumerate(context.ke_entries, 1):
            parts.append(f"{i}. {entry}\n")
        formatted["knowledge"] = "".join(parts)

    if context.examples:
        parts = [LAYER_HEADERS["examples"]]
        for i, example in enumerate(context.examples, 1):
            parts.append(f"{i}. {example}\n")
        formatted["examples"] = "".join(parts)

    return formatted


def _lsg_scan_context(context: ValidatedContext) -> bool:
    """Perform LSG security scan on context content before injection.

    Fail-closed: returns False (block) if LSG is unavailable or detects threats.
    Returns True only if LSG explicitly allows the content.
    """
    try:
        import asyncio

        from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

        gateway = LSGSecurityGateway()
        content_parts = []
        if context.system:
            content_parts.append(context.system)
        if context.rules:
            content_parts.append(context.rules)
        if context.knowledge:
            content_parts.append(context.knowledge)
        if context.examples:
            content_parts.extend(str(e) for e in context.examples)
        content = "\n".join(content_parts)
        if not content.strip():
            return True
        result = run_sync(gateway.scan_input(content))
        return result.decision.value in ("allow", "ALLOW")
    except ImportError:
        return False
    except Exception:
        return False


def _record_layer_metadata(
    layer_name: str,
    context: ValidatedContext,
    text: str,
    sources: list[str],
    provenances: list[str],
    layer_count: dict[str, int],
) -> None:
    """Record per-layer sources, provenances, and counts (extracted from inject)."""
    if layer_name == "system":
        layer_count[layer_name] = len(context.system_rules)
        sources.append("AGENTS.md")
        provenances.append("root:AGENTS.md:§0")
    elif layer_name == "rules":
        layer_count[layer_name] = len(context.contracts)
        for c in context.contracts:
            if ":" in c:
                sources.append(c.split(":")[0])
            else:
                sources.append(c[:50])
        provenances.extend(context.contracts[:10])
    elif layer_name == "knowledge":
        layer_count[layer_name] = min(len(context.ke_entries), len(text.split("\n")))
        for ke in context.ke_entries:
            if ":" in ke:
                provenances.append(ke.split("\n")[0] if "\n" in ke else ke[:80])
        provenances.extend(context.ke_entries[:5])
    elif layer_name == "examples":
        layer_count[layer_name] = len(context.examples)
        provenances.extend([f"example:{i}" for i in range(len(context.examples))])


def inject(
    context: ValidatedContext,
    *,
    session_limit: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
    examples_similarity_threshold: float = 0.7,
    timeout_s: float = 10.0,
    lsg_passed: bool | None = None,
) -> InjectionResult:
    """INJECT 阶段入口——将校验上下文以四层结构注入。

    注入顺序：Layer1(system) -> Layer2(rules) -> Layer3(knowledge) -> Layer4(examples)

    AP1 防护：注入前必须通过 CT-CE-LSG-001 三层审查。
    AP3 防护：结构化分层注入，禁止 flat string concat。
    CE 10s 超时降级：仅注入硬编码规则。

    Parameters
    ----------
    context : ValidatedContext
    session_limit : int
    examples_similarity_threshold : float
    timeout_s : float
        CE 超时阈值（默认 10s）
    lsg_passed : bool | None
        LSG 安全审查是否通过 (AP1 guard)。
        None 表示自动调用 LSG 扫描（推荐）。
        显式 True/False 用于测试或已知安全的调用方。

    Returns
    -------
    InjectionResult
    """
    if lsg_passed is None:
        lsg_passed = _lsg_scan_context(context)
    if not lsg_passed:
        return InjectionResult(
            token_count=0,
            layer_tokens={},
            sources=["LSG_BLOCKED"],
            provenances=["CT-CE-LSG-001:FAIL"],
            layer_count={"system": 0},
            budget_remaining=session_limit,
            injected_successfully=False,
        )

    start = time.monotonic()

    if not context.is_clean:
        return InjectionResult(
            token_count=0,
            layer_tokens={},
            sources=["VALIDATION_FAILED"],
            provenances=list(context.validation_warnings),
            layer_count={},
            budget_remaining=session_limit,
            injected_successfully=False,
        )

    formatted = format_context(context)
    sorted_layers: list[tuple[str, int, str]] = []
    for layer_name in ("system", "rules", "knowledge", "examples"):
        if layer_name in formatted:
            layer_num = InjectionLayer[layer_name.upper()].value
            sorted_layers.append((layer_name, layer_num, formatted[layer_name]))

    sorted_layers.sort(key=lambda x: x[1])

    injected_parts: list[str] = []
    sources: list[str] = []
    provenances: list[str] = []
    layer_tokens: dict[str, int] = {}
    layer_count: dict[str, int] = {}
    total_tokens = 0

    for layer_name, _layer_num, text in sorted_layers:
        elapsed = time.monotonic() - start
        if elapsed > timeout_s:
            return _timeout_degradation(session_limit)

        layer_tokens_val = estimate_tokens(text)
        if total_tokens + layer_tokens_val > session_limit:
            if layer_name == "knowledge":
                text, layer_tokens_val = _trim_knowledge_layer(context, text, session_limit - total_tokens)
            elif layer_name == "examples":
                continue
            else:
                break

        injected_parts.append(text)
        total_tokens += layer_tokens_val
        layer_tokens[layer_name] = layer_tokens_val

        _record_layer_metadata(layer_name, context, text, sources, provenances, layer_count)

    budget_remaining = max(0, session_limit - total_tokens)

    injected_text = "\n\n".join(injected_parts)
    elapsed = time.monotonic() - start
    if elapsed > timeout_s:
        return _timeout_degradation(session_limit)

    return InjectionResult(
        token_count=total_tokens,
        layer_tokens=layer_tokens,
        sources=sources,
        provenances=provenances,
        layer_count=layer_count,
        budget_remaining=budget_remaining,
        injected_successfully=total_tokens <= session_limit,
    )


def _trim_knowledge_layer(
    context: ValidatedContext,
    text: str,
    budget: int,
) -> tuple[str, int]:
    """超出 budget 时降低 knowledge 层 top_k。"""
    if budget <= 0:
        return "", 0
    entries = context.ke_entries
    trimmed_entries: list[str] = []
    used = 0
    header_tokens = estimate_tokens(LAYER_HEADERS["knowledge"])
    remaining = max(0, budget - header_tokens)
    for entry in entries:
        t = estimate_tokens(entry + "\n")
        if used + t > remaining:
            break
        trimmed_entries.append(entry)
        used += t
    if not trimmed_entries:
        return "", 0
    parts = [LAYER_HEADERS["knowledge"]]
    for i, entry in enumerate(trimmed_entries, 1):
        parts.append(f"{i}. {entry}\n")
    result = "".join(parts)
    return result, estimate_tokens(result)


_CE_TIMEOUT_METRIC: int = 0


AUTHORITY_CHAIN: Final[dict[str, float]] = {
    "CE_build": 0.7,
    "Orc_check": 0.85,
    "User_review": 1.0,
}


def with_authority_review(result: InjectionResult, level: str = "CE_build") -> InjectionResult:
    """TASK-018: 为注入结果标记 authority chain review 层级。

    CE build(0.7) -> Orc check(0.85) -> User review(1.0)
    """
    score = AUTHORITY_CHAIN.get(level, 0.7)
    result.authority_score = score
    result.authority_reviewed = True
    return result


def _timeout_degradation(session_limit: int) -> InjectionResult:
    """CE 10s 超时降级——仅注入硬编码规则。"""
    global _CE_TIMEOUT_METRIC
    _CE_TIMEOUT_METRIC += 1
    hardcoded = "\n".join(
        [
            "## CE Timeout — Hardcoded Rules Only",
            "1. Never delete files (R-ONLY-CREATE)",
            "2. Never ask questions (R-NO-ASK)",
            "3. Always use encoding='utf-8' (R-UTF8)",
            "4. Related changes in same commit (R-ATOMIC)",
            "5. Post-task audit mandatory (R-AUDIT)",
        ]
    )
    return InjectionResult(
        token_count=estimate_tokens(hardcoded),
        layer_tokens={"system": estimate_tokens(hardcoded)},
        sources=["CE_TIMEOUT_DEGRADATION"],
        provenances=[f"CE_timeout_metric={_CE_TIMEOUT_METRIC}"],
        layer_count={"system": 5},
        budget_remaining=session_limit,
        injected_successfully=False,
    )
