"""
errors.py —— Re-export wrapper → canonical: zephyr.shared.foundation.errors

本文件是向后兼容的顶层别名。规范实现位于 foundation/errors.py。
修改异常层次请编辑 foundation/errors.py，不要编辑本文件。
"""

from zephyr.shared.foundation.errors import *  # noqa: F401, F403
