# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.contextual_fetch_api
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_contextual_fetch_api | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""contextual_fetch_api.py — HTTP FE 对外 API (DD115, TASK-020)"""

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
        return FetchSession(
            session_id=session_id, context_type=context_type, token_count=500, sources=["KE-001", "CT-001"]
        )
