# [BLUEPRINT] SRC-024 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.behavioral_admission.vibe_coding_enforcer
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
# [A_module] module_id=MOD-GOV_vibe_coding_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from enum import Enum
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class VibeRuleLevel(str, Enum):
    MUST = "MUST"
    SHOULD = "SHOULD"
    MAY = "MAY"


VIBE_CODING_RULES: dict[str, tuple[VibeRuleLevel, str]] = {
    "lock_before_write": (VibeRuleLevel.MUST, "写入前必须 lock_files.py check → acquire"),
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
        # 修复 fail-open：未知规则默认拒绝（原为 return True）
        return False
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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            enforce(rule_name, level=VibeRuleLevel.SHOULD)
            return func(*args, **kwargs)

        wrapper._vibe_rule = rule_name  # type: ignore[attr-defined]
        wrapper._vibe_level = VibeRuleLevel.SHOULD  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def list_rules_by_level(level: VibeRuleLevel) -> dict[str, str]:
    return {name: desc for name, (lvl, desc) in VIBE_CODING_RULES.items() if lvl == level}
