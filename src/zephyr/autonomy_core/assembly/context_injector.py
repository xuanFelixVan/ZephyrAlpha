# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.assembly.context_injector
# [DOMAIN] D-AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_context_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
ContextInjector: retrieve and inject relevant knowledge into prompt context
============================================================================
Task ID : T-2-12 (C39)
safety_level : L
Depends : kb_repo.py

Retrieves knowledge from KbRepo and assembles it into an injected context
string for prompt construction. Supports three retrieval modes:
  1. By task_id  — find KEs related to a specific task
  2. By module_id — find KEs belonging to a module
  3. By keyword  — semantic/keyword search via KbRepo.search()

Respects token budget limits from ContextBudgetTracker.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from zephyr.autonomy_core.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET, estimate_tokens
from zephyr.integration.shared.schema.schemas import BASE_CONFIG

__all__ = [
    "ContextInjector",
    "InjectedContext",
    "RetrievalMode",
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
    """Retrieve and inject knowledge context from KbRepo.

    Parameters
    ----------
    kb_repo : KbRepo
        Knowledge base repository instance.
    token_budget : int
        Maximum token budget for injected context (default 8000).
    max_sources : int
        Maximum number of sources to include (default 10).
    """

    def __init__(
        self,
        kb_repo: Any,
        token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
        max_sources: int = 10,
    ) -> None:
        self._kb_repo = kb_repo
        self._token_budget = token_budget
        self._max_sources = max_sources

    def inject_by_task_id(self, task_id: str) -> Self:
        records = self._kb_repo.list_by_status()
        matching: list[Any] = []
        for rec in records:
            if (
                (hasattr(rec, "tags") and task_id in rec.tags)
                or (hasattr(rec, "summary") and task_id in rec.summary)
                or (hasattr(rec, "source_file") and task_id in rec.source_file)
            ):
                matching.append(rec)

        return self._assemble_context(matching, RetrievalMode.TASK_ID, task_id)

    def inject_by_module_id(self, module_id: str) -> Self:
        records = self._kb_repo.list_by_status()
        matching: list[Any] = []
        for rec in records:
            if (
                (hasattr(rec, "category") and rec.category == module_id)
                or (hasattr(rec, "tags") and module_id in rec.tags)
                or (hasattr(rec, "ke_id") and module_id in rec.ke_id)
            ):
                matching.append(rec)

        return self._assemble_context(matching, RetrievalMode.MODULE_ID, module_id)

    def inject_by_keyword(self, keyword: str) -> Self:
        hits = self._kb_repo.search(
            query_text=keyword,
            collection="ke_entries",
            n_results=self._max_sources,
            score_threshold=0.3,
        )

        matching: list[Any] = []
        for hit in hits:
            matching.append(hit)

        return self._assemble_from_hits(matching, RetrievalMode.KEYWORD, keyword)

    def inject(self, query: str, mode: RetrievalMode = RetrievalMode.KEYWORD) -> Self:
        if mode == RetrievalMode.TASK_ID:
            return self.inject_by_task_id(query)
        elif mode == RetrievalMode.MODULE_ID:
            return self.inject_by_module_id(query)
        else:
            return self.inject_by_keyword(query)

    def _assemble_context(
        self,
        records: list[Any],
        mode: RetrievalMode,
        query: str,
    ) -> Self:
        parts: list[str] = []
        sources: list[str] = []
        provenances: list[str] = []
        total_tokens = 0

        for rec in records[: self._max_sources]:
            content = getattr(rec, "summary", "") or getattr(rec, "content", "")
            source = getattr(rec, "source_file", "") or getattr(rec, "ke_id", "")
            ke_id = getattr(rec, "ke_id", "unknown")
            blueprint_id = getattr(rec, "blueprint_id", "")
            section = getattr(rec, "section", "")

            provenance = f"{blueprint_id}:{section}" if blueprint_id and section else ke_id
            entry_text = f"[{provenance}] {content}\n"
            entry_tokens = estimate_tokens(entry_text)

            if total_tokens + entry_tokens > self._token_budget:
                break

            parts.append(entry_text)
            if source:
                sources.append(source)
            provenances.append(provenance)
            total_tokens += entry_tokens

        context_str = "".join(parts)
        budget_remaining = self._token_budget - total_tokens

        return InjectedContext(
            context=context_str,
            sources=sources,
            provenances=provenances,
            token_count=total_tokens,
            retrieval_mode=mode.value,
            query=query,
            budget_remaining=budget_remaining,
        )

    def _assemble_from_hits(
        self,
        hits: list[Any],
        mode: RetrievalMode,
        query: str,
    ) -> Self:
        parts: list[str] = []
        sources: list[str] = []
        provenances: list[str] = []
        total_tokens = 0

        for hit in hits[: self._max_sources]:
            content = getattr(hit, "content", "")
            source = getattr(hit, "ke_id", "") or ""
            chunk_id = getattr(hit, "chunk_id", "unknown")
            blueprint_id = getattr(hit, "blueprint_id", "")
            section = getattr(hit, "section", "")

            provenance = f"{blueprint_id}:{section}" if blueprint_id and section else (source or chunk_id)
            entry_text = f"[{provenance}] {content}\n"
            entry_tokens = estimate_tokens(entry_text)

            if total_tokens + entry_tokens > self._token_budget:
                break

            parts.append(entry_text)
            if source:
                sources.append(source)
            provenances.append(provenance)
            total_tokens += entry_tokens

        context_str = "".join(parts)
        budget_remaining = self._token_budget - total_tokens

        return InjectedContext(
            context=context_str,
            sources=sources,
            provenances=provenances,
            token_count=total_tokens,
            retrieval_mode=mode.value,
            query=query,
            budget_remaining=budget_remaining,
        )

    @property
    def token_budget(self) -> int:
        return self._token_budget

    @property
    def max_sources(self) -> int:
        return self._max_sources
