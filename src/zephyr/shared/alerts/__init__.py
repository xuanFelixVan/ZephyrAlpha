# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.alerts
# [DOMAIN] D_SHARED
# [TTL] permanent
"""包 shared.alerts 的初始化文件。

AI-15 审计治本（2026-08-17）：补齐缺失的 __init__.py——本包被生产代码
（trading/governance/risk/backtest 的 threshold_loader 消费方）与
zephyr.shared.__init__ 惰性导出引用，缺 __init__.py 时 setuptools
find_packages 不识别 namespace 子包，wheel 打包会整包丢失。
__all__ 仅声明子模块名，不做 eager import。
"""

from typing import Final

__all__: Final = [
    "alert_escalation",
    "alert_manager",
    "alert_precision_tracker",
    "dual_channel_alert",
    "heartbeat_server",
    "threshold_loader",
]
