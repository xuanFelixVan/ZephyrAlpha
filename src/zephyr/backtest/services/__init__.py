# [TTL] permanent
# backtest/services
# NOTE(P1W18): scaffold 注册器对本子包写入非法行首 eager import
# （from zephyr.backtest/services.layered_validation_pipeline import ...，斜杠非点号）
# + __all__.append——已归一移除，维持本包"空导出、子模块显式导入"约定（见 #ARCH-242 族）。
# NOTE(P1W18-2): 首次归一后被回写复原（疑并行/后台进程），二次归一留痕。

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/services__init__.yaml
"""

__all__: list[str] = []
