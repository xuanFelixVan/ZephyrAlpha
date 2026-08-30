# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.architecture_principles
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: kb_ref 参数
#   fields: 参数 kb_ref，类型注解 str
#   code: architecture_principles.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: violations 参数
#   fields: 参数 violations，类型注解 list[str]
#   code: architecture_principles.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① princpled_check
#   name_en: princpled_check
#   intro: 装饰器：为函数标记适用的架构原则。
#   desc: 装饰器：为函数标记适用的架构原则。；源码 L138-L150
#   inputs: 无参数
#   outputs: Callable[[F], F]
# - id: A2
#   name_zh: ② get_principle_by_kb_ref
#   name_en: get_principle_by_kb_ref
#   intro: get_principle_by_kb_ref(kb_ref) 源码 L153-L157
#   desc: 源码 L153-L157
#   inputs: kb_ref
#   outputs: ArchPrinciple | None
# - id: A3
#   name_zh: ③ validate_against_principles
#   name_en: validate_against_principles
#   intro: 若 violations 非空，则违反某原则，记录并返回 False。
#   desc: 若 violations 非空，则违反某原则，记录并返回 False。；源码 L160-L169
#   inputs: violations
#   outputs: bool
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: Callable[[F], F]
#   name_en: Callable[[F], F]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: ArchPrinciple | None
#   name_en: ArchPrinciple | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, Final, TypeVar

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
        def wrapper(*args: Any, **kwargs: Any) -> object:
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
