# [A_module] module_id=MOD-SHR_pause | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
# Import from shared-internal _types.py — eliminates circular import to infrastructure

from zephyr.shared.contracts.backpressure._types import BackpressurePause

__all__ = ["BackpressurePause"]
