# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.logs
# [DOMAIN] D_INFRA_RUNTIME
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] PII自动脱敏;RULE-ONE原子写入;单Consumer线程串行化
# [MODIFY-GUARD] structured_sink.py; facade.py
# [CONSUMERS] facade.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写入失败->stderr->内存缓冲(1000条)->丢弃+告警
# [TESTS] tests/infrastructure/
# [TTL] permanent
"""logs — 结构化日志流（structlog + JSONL + trace注入）（D_SYSTEM_TELEMETRY）"""

from zephyr.infrastructure.system_telemetry.logs.structured_sink import (
    append_jsonl_record,
    buffer_depth,
    configure,
    flush,
    log_record_stub,
    panic_flush,
)

__all__ = [
    "append_jsonl_record",
    "log_record_stub",
    "flush",
    "panic_flush",
    "buffer_depth",
    "configure",
    "structured_sink",
]
