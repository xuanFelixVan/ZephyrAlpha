# [A_module] module_id=MOD-INF-archive | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.archive
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] TTL分级策略严格执行;成本超限->三级降级;SQLite backup使用RULE-ONE原子写入
# [MODIFY-GUARD] cold_stub.py; facade.py
# [CONSUMERS] facade.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] gzip失败->跳过压缩保留原文;SQLite backup失败->日志warning
# [TESTS] tests/infrastructure/
# [TTL] permanent
"""
遥测 · archive — 冷存储归档管道（TTL + gzip + backup + 成本降级）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: RetentionPolicy, apply_cost_degradation, compress_dir, configure, cos…
#   code: __init__.py import L43
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 RetentionPolicy, apply_cost_degradation, cold_stub, compress_dir, configure…
#   desc: __init__ import L43；__all__ 8 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（8 符号）
#   name_en: __all__
#   intro: RetentionPolicy, apply_cost_degradation, cold_stub, compress_dir, configure, co…
#   downstream: facade.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.system_telemetry.archive.cold_stub import (
    RetentionPolicy,
    apply_cost_degradation,
    compress_dir,
    configure,
    cost_status,
    next_archive_batch_id,
    rotate_by_ttl,
)

__all__ = [
    "RetentionPolicy",
    "apply_cost_degradation",
    "cold_stub",
    "compress_dir",
    "configure",
    "cost_status",
    "next_archive_batch_id",
    "rotate_by_ttl",
]
