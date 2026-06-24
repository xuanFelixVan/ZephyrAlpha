# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] src.zephyr.shared.contracts.backpressure.pause
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.contracts.backpressure._types
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_pause | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Import from shared-internal _types.py — eliminates circular import to infrastructure

from zephyr.shared.contracts.backpressure._types import BackpressurePause

__all__ = ["BackpressurePause"]
