"""
SRC-0039: 向后兼容 shim — escaLATION 已重命名为 escalation_engine

本文件仅重新导出 zephyr.escalation_engine 的符号以保证向后兼容。
新代码应直接 import from zephyr.escalation_engine。
"""

from zephyr.escalation_engine import *  # noqa: F403
