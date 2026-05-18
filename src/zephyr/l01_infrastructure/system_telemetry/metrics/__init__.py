# [BLUEPRINT] MOD-INF-015 | docs/03_modules/l01_infrastructure/system-telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.l01_infrastructure.system_telemetry.metrics
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] 蓝图读取事件MUST通过blueprint_metrics记录;输出JSONL格式
# [MODIFY-GUARD] blueprint_metrics.py; facade.py
# [CONSUMERS] facade.py; auto_bootstrap.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] JSONL写入失败→日志warning
# [TESTS] tests/unit/telemetry/
"""L12 · metrics — SLI/SLO 与业务指标流"""

__all__ = ['blueprint_metrics']
