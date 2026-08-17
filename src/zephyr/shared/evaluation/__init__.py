# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.evaluation
# [DOMAIN] D_SHARED
# [TTL] permanent
"""包 shared.evaluation 的初始化文件。

AI-15 审计治本（2026-08-17）：补齐缺失的 __init__.py——缺 __init__.py 时
setuptools find_packages 不识别 namespace 子包，wheel 打包会整包丢失。
__all__ 仅声明子模块名，不做 eager import。
"""

from typing import Final

__all__: Final = [
    "evals",
]
