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
"""
logs — 结构化日志流（structlog + JSONL + trace注入）（D_SYSTEM_TELEMETRY）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: append_jsonl_record, buffer_depth, configure, flush, log_record_stub,…
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 append_jsonl_record, log_record_stub, flush, panic_flush, buffer_depth, con…
#   desc: __init__ import L44；__all__ 7 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（7 符号）
#   name_en: __all__
#   intro: append_jsonl_record, log_record_stub, flush, panic_flush, buffer_depth, configu…
#   downstream: facade.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
