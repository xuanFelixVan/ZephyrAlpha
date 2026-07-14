# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.architecture_principles
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
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
# [A_module] module_id=MOD-GOV_architecture_principles | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ArchPrinciple(str, Enum):
    P1_SSOT = "P1_SSOT"
    P2_YAML_SCHEMA = "P2_YAML_SCHEMA"
    P3_DUAL_AI = "P3_DUAL_AI"
    P4_OCP = "P4_OCP"
    P5_BLUEPRINT_FIRST = "P5_BLUEPRINT_FIRST"


class BlueprintIronLaw(str, Enum):
    IL1_FLAT_TOP = "IL1_FLAT_TOP"
    IL2_BOOTSTRAP_LINK = "IL2_BOOTSTRAP_LINK"
    IL3_AUDITABLE_CHANGE = "IL3_AUDITABLE_CHANGE"
    IL4_EQUIVALENCE = "IL4_EQUIVALENCE"
    IL5_SOURCE_OF_TRUTH = "IL5_SOURCE_OF_TRUTH"


PRINCIPLE_DEFS: Final[dict[ArchPrinciple, dict[str, str]]] = {
    ArchPrinciple.P1_SSOT: {
        "label": "P1-SSoT (ADR-0001)",
        "statement": "YAML=真源，MD=衍生视图",
        "kb_ref": "ADR-0001",
    },
    ArchPrinciple.P2_YAML_SCHEMA: {
        "label": "P2-YAML Schema (ADR-0002)",
        "statement": "单Schema，Phased Required Fields（Phase 0->Phase 5）",
        "kb_ref": "ADR-0002",
    },
    ArchPrinciple.P3_DUAL_AI: {
        "label": "P3-DeepSeek Pipeline (ADR-0003)",
        "statement": "DeepSeek V4 Pro 全管线 + Claude 极端救援",
        "kb_ref": "ADR-0003",
    },
    ArchPrinciple.P4_OCP: {
        "label": "P4-OCP (ADR-0004)",
        "statement": "Open-Closed Principle——对扩展开放，对修改封闭",
        "kb_ref": "ADR-0004",
    },
    ArchPrinciple.P5_BLUEPRINT_FIRST: {
        "label": "P5-Blueprint First (G6)",
        "statement": "先读蓝图->后写代码",
        "kb_ref": "G6",
    },
}

IRON_LAW_DEFS: Final[dict[BlueprintIronLaw, str]] = {
    BlueprintIronLaw.IL1_FLAT_TOP: "单层目录不允许嵌套子目录",
    BlueprintIronLaw.IL2_BOOTSTRAP_LINK: "自举链接——所有MD必须可通过YAML重建",
    BlueprintIronLaw.IL3_AUDITABLE_CHANGE: "变更记录必须可审计追踪",
    BlueprintIronLaw.IL4_EQUIVALENCE: "YAML和MD视图语义完全等价",
    BlueprintIronLaw.IL5_SOURCE_OF_TRUTH: "YAML为唯一真源，其他格式均派生",
}


def princpled_check(*principles: ArchPrinciple) -> Callable[[F], F]:
    """装饰器：为函数标记适用的架构原则。"""

    def decorator(func: F) -> F:
        func._zephyr_principles = list(principles)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def get_principle_by_kb_ref(kb_ref: str) -> ArchPrinciple | None:
    for p in ArchPrinciple:
        if PRINCIPLE_DEFS[p]["kb_ref"] == kb_ref:
            return p
    return None


def validate_against_principles(violations: list[str]) -> bool:
    """若 violations 非空，则违反某原则，记录并返回 False。"""
    if violations:
        import logging

        logger = logging.getLogger(__name__)
        for v in violations:
            logger.warning("Arch Principle Violation: %s", v)
        return False
    return True
