# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.context
# [DOMAIN] D_SHARED
# [TTL] permanent
"""
包 shared.context 的初始化文件。

AI-15 审计治本（2026-08-17）：补齐缺失的 __init__.py——缺 __init__.py 时
setuptools find_packages 不识别 namespace 子包，wheel 打包会整包丢失。
__all__ 仅声明子模块名，不做 eager import。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final
#   code: __init__.py import L39
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final（共 1 符号）
#   desc: __init__ import L39；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: Final
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = [
    "context_engine",
]
