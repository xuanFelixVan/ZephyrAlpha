"""[A_module] module_id=MOD-TRADING-RUNTIME | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

trading.runtime — 异步运行时子包（R1 升级：同步->async 渐进式迁移）
"""

from zephyr.trading.runtime.async_runtime import AsyncRuntime

__all__ = [
    "AsyncRuntime",
]
