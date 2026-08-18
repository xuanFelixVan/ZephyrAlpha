# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-UNK-pf_alloc | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from typing import Final

from zephyr.pf_alloc import (
    batched_position_builder,  # noqa: F401  # ORPHAN-MODULE: 新模块引用登记（41_buy_flow MOD-PA-006）
)

__all__: Final = ["strategy_lifecycle_event", "batched_position_builder"]
