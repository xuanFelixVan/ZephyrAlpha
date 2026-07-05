# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.base
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ==== BEGIN CODGEN:OCP-001 ====
from __future__ import annotations
import abc
from dataclasses import dataclass, field
from typing import ClassVar

# ---
# layer: l02
# category: ocp_extension
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — base.py

OCP-001: FactorBase + FactorRegistry / 因子扩展点

D_FACTOR 因子基类契约。所有因子必须继承 FactorBase，实现 compute()，向 FactorRegistry 注册。 (INV-007: implementors must ensure cross-layer calls carry idempotency_key)

SSoT: cross_layer_contracts.yaml → OCP-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    D_FACTOR 因子基类契约。所有因子必须继承 FactorBase，实现 compute()，向 FactorRegistry 注册。 (INV-007: implementors must ensure cross-layer calls carry idempotency_key)
"""


@dataclass
class FactorMeta:
    description: str
    domain: str
    factor_id: str
    name: str
    version: str
    author: str = "agent"
    tags: list[str] = field(default_factory=list)


class FactorBase(abc.ABC):
    """D_FACTOR 因子基类契约。所有因子必须继承 FactorBase，实现 compute()，向 FactorRegistry 注册。 (INV-007: implementors must ensure cross-layer calls carry idempotency_key)"""

    meta: ClassVar[FactorMeta]

    @abc.abstractmethod
    def compute(self) -> list[FactorSignal]:
        """计算因子信号（禁止 look-ahead bias）"""
        ...

    def validate_inputs(self) -> bool:
        """输入验证钩子（可选覆盖）。"""
        pass


# ==== END CODGEN:OCP-001 ====
