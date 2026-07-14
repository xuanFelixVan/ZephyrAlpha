# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.error_classifier
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib(re)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯字符串匹配无副作用; 不可恢复错误立即fallback; 可恢复错误重试用完才fallback
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入None/空串->unknown; 匹配失败->unknown
# [TESTS] tests/zephyr/data/test_error_classifier.py
# [A_module] module_id=MOD-L00-004-error_classifier | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据源错误分类器——根据错误字符串判断可恢复性。

设计理念（数据韧性三层机制 §2）：
  - 不可恢复错误（配额耗尽/接口废弃/认证失败）→ 立即 fallback 到副源
  - 可恢复错误（超时/网络波动）→ 重试用完才 fallback
  - 未知错误 → 当作可恢复处理（给重试机会）

分类基于关键词匹配（FetchResult.error 字符串），覆盖 iFind/akshare/QMT 常见错误。

Usage::

    from zephyr.data.error_classifier import classify_error, is_unrecoverable

    if is_unrecoverable(result.error):
        # 立即 fallback 到副源
        ...
"""

from __future__ import annotations

import re

__all__ = ["classify_error", "is_unrecoverable", "is_recoverable"]

# 不可恢复错误关键词——配额/废弃/认证类，重试无意义
_UNRECOVERABLE_PATTERNS = [
    r"-4318",           # iFind 配额耗尽
    r"-4309",           # iFind 接口废弃
    r"配额",
    r"quota",
    r"接口已废弃",
    r"deprecated",
    r"认证失败",
    r"\bauth\b",
    r"\b401\b",
    r"\b403\b",
    r"请指定正确的接口名",
    r"未授权",
    r"unauthorized",
    r"license",
    r"许可",
]

# 可恢复错误关键词——超时/网络类，重试可能成功
_RECOVERABLE_PATTERNS = [
    r"Timeout",
    r"ConnectionError",
    r"RemoteDisconnected",
    r"HTTPError",
    r"JSONDecodeError",
    r"ConnectionRefused",
    r"ConnectionReset",
    r"timeout",
    r"timed out",
    r"ServiceUnavailable",
    r"\b503\b",
    r"\b502\b",
    r"temporarily",
    r"retry",
]

# 预编译正则
_UNRECOVERABLE_RE = re.compile("|".join(_UNRECOVERABLE_PATTERNS))
_RECOVERABLE_RE = re.compile("|".join(_RECOVERABLE_PATTERNS))


def classify_error(error: str | None) -> str:
    """分类错误类型。

    Args:
        error: 错误字符串（FetchResult.error）。

    Returns:
        "unrecoverable" | "recoverable" | "unknown"
    """
    if not error:
        return "unknown"
    if _UNRECOVERABLE_RE.search(error):
        return "unrecoverable"
    if _RECOVERABLE_RE.search(error):
        return "recoverable"
    return "unknown"


def is_unrecoverable(error: str | None) -> bool:
    """是否不可恢复错误（应立即 fallback）。"""
    return classify_error(error) == "unrecoverable"


def is_recoverable(error: str | None) -> bool:
    """是否可恢复错误（应重试）。"""
    return classify_error(error) == "recoverable"
