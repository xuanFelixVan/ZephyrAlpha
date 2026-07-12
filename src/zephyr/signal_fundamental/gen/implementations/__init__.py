# [A_module] module_id=MOD-UNK_implementations_gen_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md
# [MODULE] zephyr.signal_fundamental.gen.implementations
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_SIGNAL — Signal Generation Concrete Implementations"""

from __future__ import annotations

from zephyr.signal_fundamental.gen.implementations.default_signal_aggregator import DefaultSignalAggregator

__all__ = ["DefaultSignalAggregator", "default_signal_aggregator"]
