# [TTL] permanent
"""

[A_module] module_id=MOD-TRADING-RUNTIME | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

trading.runtime — 异步运行时子包（R1 升级：同步->async 渐进式迁移）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 子模块 AsyncRuntime 类定义
#   fields: zephyr.trading.runtime.async_runtime.AsyncRuntime（异步运行时，R1 同步→async 渐进迁移）
#   code: src/zephyr/trading/runtime/async_runtime.py
# 层: 算法
# - id: A1
#   name_zh: ① 包入口再导出
#   name_en: runtime/__init__ re-export
#   intro: 把子模块的 AsyncRuntime 提到包命名空间，声明 __all__ 控制导出面
#   desc: from .async_runtime import AsyncRuntime；__all__=["AsyncRuntime"]；无其他逻辑
#   inputs: I1
#   outputs: 包级命名空间导出
# 层: 输出
# - id: O1
#   name_zh: 包级导出 zephyr.trading.runtime.AsyncRuntime
#   name_en: AsyncRuntime (package-level export)
#   intro: 上层模块经包入口直接导入异步运行时，无需感知子模块路径
#   downstream: 无下游/内部使用（MOD-TRADING-RUNTIME 包入口，供交易域上层导入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.trading.runtime.async_runtime import AsyncRuntime

__all__ = [
    "AsyncRuntime",
]
