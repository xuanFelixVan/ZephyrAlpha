# 代理模块：将 zephyr.shared.quality.quality_monitor 重定向到 zephyr.infrastructure.quality.quality_monitor
from zephyr.infrastructure.quality.quality_monitor import QualityMonitor

__all__ = ["QualityMonitor"]
