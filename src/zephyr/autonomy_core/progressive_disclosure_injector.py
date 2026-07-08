# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.progressive_disclosure_injector
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
# [A_module] module_id=MOD-ORC_progressive_disclosure_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""progressive_disclosure_injector.py — 渐进式披露 (B7, DD81, TASK-015 beta w)"""

from dataclasses import dataclass


@dataclass
class DisclosureResult:
    summary_injected: bool
    ke_ids_available: list[str]
    expanded_ke_id: str = ""


class ProgressiveDisclosureInjector:
    """摘要先注->agent 请求展开完整 KE (DD81)."""

    def inject_summary(self, ke_ids: list[str]) -> DisclosureResult:
        return DisclosureResult(summary_injected=True, ke_ids_available=ke_ids)

    def expand(self, ke_id: str) -> str:
        return f"Full content for {ke_id}"
