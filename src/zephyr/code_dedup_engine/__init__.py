"""code_dedup_engine — Re-export proxy.

Canonical 实现位于 l01_infrastructure.code_dedup_engine（MOD-INF-017）。
本包为兼容性 re-export 代理——两个 import 路径均可使用。
"""

from zephyr.l01_infrastructure.code_dedup_engine import *  # noqa: F403

from zephyr.l01_infrastructure.code_dedup_engine import (
    __module_id__,
    __status__,
    __version__,
)

__all__ = []  # populated by from-import above
