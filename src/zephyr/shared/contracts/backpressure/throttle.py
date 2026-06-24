# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.backpressure.throttle
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
# [A_module] module_id=MOD-SHR_throttle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Import from shared-internal _types.py — eliminates circular import to infrastructure

from zephyr.shared.contracts.backpressure._types import BackpressureThrottle

__all__ = ["BackpressureThrottle"]
