# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.assembly.context_injector
# [DOMAIN] D_AUTONOMY_CORE
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
# [TTL] task_bound

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

KB refactor Step 2.1 removed kb_repo.py SQLite layer;
inject_by_* methods return empty InjectedContext (no data source).
KB refactor Phase 3 will migrate consumers to VMS-backed retrieval.

Respects token budget limits from ContextBudgetTracker.
"""

from __future__ import annotations

from enum import Enum

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
    """Retrieve and inject knowledge context.

    KB refactor Step 2.1 removed kb_repo.py; inject_by_* return empty context.

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

    def inject(self, query: str, mode: RetrievalMode = RetrievalMode.KEYWORD) -> Self:
        if mode == RetrievalMode.TASK_ID:
            return self.inject_by_task_id(query)
        elif mode == RetrievalMode.MODULE_ID:
            return self.inject_by_module_id(query)
        else:
            return self.inject_by_keyword(query)

    @property
    def token_budget(self) -> int:
        return self._token_budget

    @property
    def max_sources(self) -> int:
        return self._max_sources
