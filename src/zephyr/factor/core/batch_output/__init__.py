# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-BO
# [MODULE] zephyr.factor.core.batch_output
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.contracts.factor_signal
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 缓冲达 batch_size 或距上次 flush 超 flush_interval_s 触发刷新；空缓冲 flush 返回 None
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] writer 失败由调用方处理（FlushOutcome.outcome 携带 WriteOutcome）；空 payload 跳过写入
# [TESTS] tests/factor/test_batch_output.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_FACTOR core batch_output 子包——FactorSignal 批量缓冲写入器。

缓冲 FactorSignal 列表，按定量（batch_size）或定时（flush_interval_s）触发刷新，
调用 ch_writer.write_tsv_outcome 写入 ClickHouse。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, BatchOutputConfig, FactorSignalBuffer, FlushOutcome, sig…
#   code: __init__.py import L50
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BatchOutputConfig, FactorSignalBuffer, FlushOutcome, signal_to_tsv_row, sig…
#   desc: __init__ import L50；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: BatchOutputConfig, FactorSignalBuffer, FlushOutcome, signal_to_tsv_row, signals…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.factor.core.batch_output.buffer import (
    BatchOutputConfig,
    FactorSignalBuffer,
    FlushOutcome,
    signal_to_tsv_row,
    signals_to_tsv,
)

__all__ = [
    "BatchOutputConfig",
    "FactorSignalBuffer",
    "FlushOutcome",
    "signal_to_tsv_row",
    "signals_to_tsv",
]
