# [BLUEPRINT] MOD-SHR_converters | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.converters
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] scripts.governance.sync_panorama_module, scripts.governance.d5_architecture.generators.align_panoramas
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] normalize_to_none("") is None; normalize_to_none(0) == 0 (不误转非空字符串的 falsy 值)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/shared/test_converters.py
# [A_module] module_id=MOD-SHR_converters | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
converters.py — 类型转换工具（消除 '' vs None 语义鸿沟）

病根（Ruling:100PCT-AI-GOVERNANCE P1-1，2026-07-19）：
  weighted_domain_vote / min_maturity 在无值时返回 ""（空字符串），
  但 PostgreSQL CHECK 约束（如 chk_decision_layers_domain_id_not_empty）
  允许 NULL 禁止 ''，导致 INSERT 静默失败。

  原修复：消费方用 `value or None` 转换。但 `or None` 会误转所有 falsy 值
  （0, False, []），且意图不明确（读代码者需推断为何要 `or None`）。

治本：
  统一 normalize_to_none() 工具函数——只转 "" 为 None，其他值原样返回。
  - 语义明确：函数名即文档
  - 类型安全：不误转 0/False/[] 等合法 falsy 值
  - 集中维护：转换逻辑唯一真源，未来扩展（如 whitespace-only 也转 None）只改一处

用法::

    from zephyr.shared.utils.converters import normalize_to_none

    domain_id = normalize_to_none(weighted_domain_vote(rows))
    # "" → None（让 PostgreSQL 写入 NULL，对齐 CHECK 约束语义）
    # "D_GOVERNANCE" → "D_GOVERNANCE"（原样返回）

SSoT: MOD-SHR_converters
Version: 1.0.0
"""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")

__all__ = ["normalize_to_none"]


def normalize_to_none(value: T) -> T | None:
    """将空字符串转为 None，其他值原样返回。

    语义：
      - "" → None（空字符串语义上等于"未知"，对齐 PostgreSQL CHECK 约束）
      - None → None（原样）
      - 其他任何值（0, False, "text", []）→ 原样返回

    与 `value or None` 的区别：
      - `"" or None` → None ✓
      - `0 or None` → None ✗（0 是合法值，不应转 None）
      - `normalize_to_none(0)` → 0 ✓（只转空字符串）

    Args:
        value: 任意值。

    Returns:
        None 如果 value 是空字符串或 None；否则原样返回 value。
    """
    if value is None or value == "":
        return None
    return value
