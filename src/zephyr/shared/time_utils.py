"""
time_utils.py — 时间工具函数 SSoT

根因修复：此前 _now_iso() 在 9 个文件中重复定义，
_default_now() 在 5 个文件中重复定义。
任何时间格式变更需改 14 处。

对标：
  - Python datetime best practices: UTC everywhere
  - Google Style Guide: "Don't repeat yourself"
  - Django: timezone.now() 作为唯一时间获取入口
"""
from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """返回当前 UTC 时间。

    替代 datetime.now(timezone.utc) 的分散调用，
    便于全局切换时间源（测试时可 mock 此函数）。
    """
    return datetime.now(timezone.utc)


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串。

    替代 9 处分散的 _now_iso() 定义。
    """
    return utc_now().isoformat()


def default_now() -> datetime:
    """Pydantic Field default_factory 用的 UTC 时间工厂。

    替代 5 处分散的 _default_now() 定义。

    Usage::

        created_at: datetime = Field(default_factory=default_now)
    """
    return utc_now()


__all__ = [
    "utc_now",
    "now_iso",
    "default_now",
]
