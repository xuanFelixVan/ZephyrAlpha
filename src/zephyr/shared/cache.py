"""
cache.py —— Re-export wrapper → canonical: zephyr.shared.infra.cache

本文件是向后兼容的顶层别名。规范实现位于 infra/cache.py。
修改缓存逻辑请编辑 infra/cache.py，不要编辑本文件。
"""

from .infra.cache import *  # noqa: F401, F403
