# [BLUEPRINT] MOD-ML_SERVE | (pending)
# [MODULE] zephyr.ml_serve.core
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ML_SERVE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2

# ml_serve/core

# NOTE(P1W25 2026-08-25): scaffold 注册器写入斜杠非法 import（#ARCH-228 同款 bug
# 第 12 次复发，原写于文件头第 1 行），归一为点号 import 并移至治理头之后。
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: ModelDriftMonitor
#   code: __init__.py import L53
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ModelDriftMonitor（共 1 符号）
#   desc: __init__ import L53；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: ModelDriftMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.ml_serve.core.model_drift_monitor import ModelDriftMonitor

__all__: list[str] = []

__all__.append("ModelDriftMonitor")
