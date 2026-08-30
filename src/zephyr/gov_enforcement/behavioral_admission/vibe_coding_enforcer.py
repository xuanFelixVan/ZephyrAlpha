# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement.behavioral_admission.vibe_coding_enforcer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
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
#   name: rule_name 参数
#   fields: 参数 rule_name，类型注解 str
#   code: vibe_coding_enforcer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: level 参数
#   fields: 参数 level（无注解）
#   code: vibe_coding_enforcer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: checks 参数
#   fields: 参数 checks，类型注解 dict[str, VibeRuleLevel | None]
#   code: vibe_coding_enforcer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① enforce
#   name_en: enforce
#   intro: enforce(rule_name, level) 源码 L126-L135
#   desc: 源码 L126-L135
#   inputs: rule_name level
#   outputs: bool
# - id: A2
#   name_zh: ② enforce_all
#   name_en: enforce_all
#   intro: enforce_all(checks) 源码 L138-L139
#   desc: 源码 L138-L139
#   inputs: checks
#   outputs: dict[str, bool]
# - id: A3
#   name_zh: ③ must
#   name_en: must
#   intro: must(rule_name) 源码 L142-L156
#   desc: 源码 L142-L156
#   inputs: rule_name
#   outputs: Callable[[F], F]
# - id: A4
#   name_zh: ④ should
#   name_en: should
#   intro: should(rule_name) 源码 L159-L170
#   desc: 源码 L159-L170
#   inputs: rule_name
#   outputs: Callable[[F], F]
# - id: A5
#   name_zh: ⑤ list_rules_by_level
#   name_en: list_rules_by_level
#   intro: list_rules_by_level(level) 源码 L173-L174
#   desc: 源码 L173-L174
#   inputs: level
#   outputs: dict[str, str]
#   （注：A5 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: dict[str, bool]
#   name_en: dict[str, bool]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Any, Callable, Final, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class VibeRuleLevel(str, Enum):
    MUST = "MUST"
    SHOULD = "SHOULD"
    MAY = "MAY"


VIBE_CODING_RULES: Final[dict[str, tuple[VibeRuleLevel, str]]] = {
    "lock_before_write": (VibeRuleLevel.MUST, "写入前必须 lock_files.py check -> acquire"),
    "release_after_write": (VibeRuleLevel.MUST, "写入后必须 release 锁"),
    "encoding_utf8": (VibeRuleLevel.MUST, "所有文件写入必须 encoding='utf-8'"),
    "read_blueprint_first": (VibeRuleLevel.MUST, "写代码前必须先读 blueprint 对应 section"),
    "dual_ai_review": (VibeRuleLevel.SHOULD, "关键代码应由 ≥2 模型交叉审查"),
    "provenance_embed": (VibeRuleLevel.SHOULD, "生成代码应嵌入 __provenance__"),
    "journal_log": (VibeRuleLevel.SHOULD, "任务完成应追加 journal 行"),
    "checkpoint_update": (VibeRuleLevel.SHOULD, "批量完成后更新 checkpoint"),
    "smoke_test": (VibeRuleLevel.SHOULD, "关键模块应有 smoke test"),
    "exploratory_first": (VibeRuleLevel.MAY, "新域先探索后固化为 SHOULD/MUST"),
    "prompt_ab_test": (VibeRuleLevel.MAY, "不同 prompt 效果 A/B 测试"),
}


def enforce(rule_name: str, *, level: VibeRuleLevel | None = None) -> bool:
    entry = VIBE_CODING_RULES.get(rule_name)
    if entry is None:
        # 未知规则默认允许（fail-open：不阻断未知规则，测试 SSoT）
        return True  # 未知规则默认允许
    actual_level, _ = entry
    if level is None:
        return actual_level is not VibeRuleLevel.MUST
    level_order = {VibeRuleLevel.MAY: 0, VibeRuleLevel.SHOULD: 1, VibeRuleLevel.MUST: 2}
    return level_order.get(level, 0) <= level_order.get(actual_level, 0)


def enforce_all(checks: dict[str, VibeRuleLevel | None]) -> dict[str, bool]:
    return {name: enforce(name, level=level) for name, level in checks.items()}


def must(rule_name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> object:
            if not enforce(rule_name, level=VibeRuleLevel.MUST):
                import logging

                logging.getLogger(__name__).warning("Vibe Coding MUST violation: %s in %s", rule_name, func.__name__)
            return func(*args, **kwargs)

        wrapper._vibe_rule = rule_name  # type: ignore[attr-defined]
        wrapper._vibe_level = VibeRuleLevel.MUST  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def should(rule_name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> object:
            enforce(rule_name, level=VibeRuleLevel.SHOULD)
            return func(*args, **kwargs)

        wrapper._vibe_rule = rule_name  # type: ignore[attr-defined]
        wrapper._vibe_level = VibeRuleLevel.SHOULD  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def list_rules_by_level(level: VibeRuleLevel) -> dict[str, str]:
    return {name: desc for name, (lvl, desc) in VIBE_CODING_RULES.items() if lvl == level}
