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
"""D_FACTOR core batch_output 子包——FactorSignal 批量缓冲写入器。

缓冲 FactorSignal 列表，按定量（batch_size）或定时（flush_interval_s）触发刷新，
调用 ch_writer.write_tsv_outcome 写入 ClickHouse。
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
