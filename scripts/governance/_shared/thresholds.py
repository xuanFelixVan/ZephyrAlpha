# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/thresholds.py | §
# [MODULE] scripts.governance._shared.thresholds
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
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
# [TTL] task_bound
"""
thresholds.py — 阈值集中配置加载器

对标 B16（关键阈值外置+变更审计）+ SCRIPT-QUALITY-001 D-G-01（配置外置）。
所有脚本通过 from _shared.thresholds import get_thresholds 读取阈值，
不再硬编码关键数字。

Usage:
    from _shared.thresholds import get_thresholds
    t = get_thresholds()
    max_fpr = t["finding_quality"]["false_positive_rate_max"]
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_THRESHOLDS_PATH = Path(__file__).resolve().parent / "thresholds.yaml"
_CACHE: dict[str, Any] | None = None


def get_thresholds() -> dict[str, Any]:
    """惰性加载阈值配置（Google Style §2.10: 禁止模块级副作用）。

    Returns:
        dict: 八大阈值分组——scanning/finding_quality/error_budget/
              sla_timers/shadow_mode/script_health/ast_similarity/blueprint_sync

    Raises:
        FileNotFoundError: thresholds.yaml 不存在
        yaml.YAMLError: YAML 格式无效
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    with open(_THRESHOLDS_PATH, encoding="utf-8") as f:
        _CACHE = yaml.safe_load(f)
    return _CACHE


def get(key_path: str, default: Any = None) -> Any:
    """按点分隔路径读取嵌套阈值。

    Args:
        key_path: 点分隔的配置路径（如 "finding_quality.false_positive_rate_max"）
        default: 路径不存在时的默认值

    Returns:
        Any: 对应的阈值，或 default

    Examples:
        >>> get("error_budget.burn_rate.critical_1h_percent")
        0.02
    """
    t = get_thresholds()
    node: Any = t
    for part in key_path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return default
    return node


def get_thresholds_safe() -> dict[str, Any]:
    """graceful 变体：thresholds.yaml 缺失时返回 {} 而非 raise FileNotFoundError。

    供防御性调用方使用（如 manage_error_budget 用 .get() 链式取值 + fallback 默认值）。
    文件存在时委托 get_thresholds()（享受缓存）；缺失时返回空 dict。
    """
    if not _THRESHOLDS_PATH.exists():
        return {}
    return get_thresholds()


def invalidate_cache() -> None:
    """清除缓存——阈值文件被修改后调用，确保下次读取最新值。"""
    global _CACHE
    _CACHE = None
