# [A_module] module_id=MOD-INF_archive | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""遥测 · archive — 冷存储归档管道（TTL + gzip + backup + 成本降级）"""

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
