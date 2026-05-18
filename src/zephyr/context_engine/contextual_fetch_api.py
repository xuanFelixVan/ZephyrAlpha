# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.contextual_fetch_api

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""contextual_fetch_api.py — HTTP FE 对外 API (DD115, TASK-020)"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FetchSession:
    session_id: str
    context_type: str  # "full" | "summary"
    token_count: int
    sources: list[str] = field(default_factory=list)


class ContextualFetchAPI:
    """GET /api/ce/session/{id}?context_type=full|summary (DD115)."""
    def fetch(self, session_id: str, context_type: str = "full") -> FetchSession:
        return FetchSession(session_id=session_id, context_type=context_type, token_count=500, sources=["KE-001", "CT-001"])
