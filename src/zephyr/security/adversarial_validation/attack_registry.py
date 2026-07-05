# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red-blue-validator/blueprint.md
# [MODULE] zephyr.security.adversarial_validation.attack_registry
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] 见蓝图 §4 接口契约
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐
# [MODIFY-GUARD] red-blue-validator/blueprint.md; red-blue-validator/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RedBlueValidationError
# [TESTS] tests/red-blue-validator/
# [A_module] module_id=MOD-SEC_attack_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


__all__: list[str] = ["AttackRegistry"]


class AttackRegistry:
    def __init__(self) -> None:
        pass

    def register(self, attack_id: str, tier: int, scenario: str) -> None:
        pass

    def query_by_tier(self, tier: int) -> list[str]:
        pass

    def count(self) -> int:
        pass
