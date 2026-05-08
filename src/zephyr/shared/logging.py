"""
logging.py —— Re-export wrapper → canonical: zephyr.shared.observability.logging

本文件是向后兼容的顶层别名。规范实现位于 observability/logging.py。
修改日志逻辑请编辑 observability/logging.py，不要编辑本文件。
"""

from zephyr.shared.observability.logging import *  # noqa: F401, F403
