# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.chunk_strategy_router
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INT_chunk_strategy_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ChunkStrategyRouter — MOD-INF-011 分块策略调度
================================================
蓝图 §2.1 · §6 · 6 种分块策略按 Collection 差异化路由

策略矩阵
--------
┌───────────────┬──────────────────────┬────────────┐
│ chunk_strategy │ 适用 Collection       │ 说明        │
├───────────────┼──────────────────────┼────────────┤
│ semantic       │ decisions             │ 500-800tk  │
│ ast_aware      │ code_context          │ func/class │
│ paragraph      │ lessons               │ 300-500tk  │
│ heading_aware  │ knowledge             │ 500-800tk  │
│ rule_level     │ rules                 │ 整条存储    │
│ section_aware  │ blueprints            │ 按§拆分     │
│ session_level  │ session_snapshots     │ 单摘要      │
│ time_window    │ execution_traces      │ 1min窗口    │
└───────────────┴──────────────────────┴────────────┘
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG

_logger = logging.getLogger(__name__)


class Chunk(BaseModel):
    model_config = BASE_CONFIG

    text: str
    strategy: str
    index: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkStrategyRouter:
    VALID_STRATEGIES: ClassVar[frozenset[str]] = frozenset(
        {
            "semantic",
            "ast_aware",
            "paragraph",
            "heading_aware",
            "rule_level",
            "section_aware",
            "session_level",
            "time_window",
        }
    )

    def route(self, text: str, strategy: str) -> list[Chunk]:
        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(f"未知分块策略: {strategy}。允许: {sorted(self.VALID_STRATEGIES)}")

        if strategy == "rule_level":
            return [Chunk(text=text, strategy=strategy, index=0)]
        if strategy == "session_level":
            return [Chunk(text=text, strategy=strategy, index=0)]
        if strategy == "time_window":
            return [Chunk(text=text, strategy=strategy, index=0)]

        return self._default_chunk(text, strategy)

    def _default_chunk(self, text: str, strategy: str, target_size: int = 500) -> list[Chunk]:
        if len(text) <= target_size:
            return [Chunk(text=text, strategy=strategy, index=0)]

        chunks: list[Chunk] = []
        idx = 0
        while idx < len(text):
            end = min(idx + target_size, len(text))
            chunk_text = text[idx:end]
            chunks.append(Chunk(text=chunk_text, strategy=strategy, index=len(chunks)))
            idx = end
        return chunks
