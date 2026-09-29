# [BLUEPRINT] MOD-ML_SERVE | (pending)
# [MODULE] zephyr.ml_serve.core
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES]zephyr.ml_serve.core.model_drift_monitor
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


# [ALGO_FLOW] external: docs/03_modules/_domain_ml_serve/algo_flow/core__init__.yaml
"""

# 2026-09-30 st-finaldel-retire：model_drift_monitor 已随 F130 物理净删（successor=F129 ml_train；
# 8 件净删面归档 G:/zephyr_cold/retire_c267_20260930/F130_ml_serve/），原 L29 re-export 同步拆除。

__all__: list[str] = []
