# [BLUEPRINT] MOD-BT-FEXAM | docs/03_modules/MOD-BT-FEXAM/ | 抢救证据件（st-matrix-20261007 P0-1 抢救面，st-govfix-g3-20261007 治理入库）
# [not-trading: 抢救证据件（st-matrix-20261007 P0-1 考试现场快照原样转正），非交易运行面，零生产消费链，不挂 TDM 决策图]
# [MODULE] scripts.matrix_rescued_tmp.probes.grid_oos_dsr
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] 无（一次性考卷/对拍/计时证据件；随附数据在 docs/_working/matrix_campaign/rescued_tmp_20261007/）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 抢救证据件原样保留，判定面不入核；表名走 TableRegistry 真源
# [MODIFY-GUARD] freeze——抢救证据件禁改写业务逻辑（门禁合规头/noqa 除外）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 运行期异常如实抛出（证据件不吞错不改判）
# [TESTS] 无独立测试（一次性证据件，输出随件入册）
# [TTL] task_bound
# -*- coding: ascii -*-
# DSR N-ledger recording for the 324-cell grid OOS exam (temp script)
# dedup: the 324 backtests are ALREADY counted by auto_sync as factory_grid_batch_a
# entries grid_20261006-201353/201854/201935/202016/202055 (18+54+54+54+144=324).
# => record this exam batch as a 0-increment pointer entry to avoid double counting.
from zephyr.backtest.core.n_trial_ledger import TrialLedger

BATCH = "fexam-grid-strat-20261007"
KIND = "fexam_grid_strategy_family"

led = TrialLedger()
before = led.cumulative_trials()
snap0 = led.snapshot()
already = [r for r in snap0.breakdown if BATCH in r]
print("cumulative_trials_before:", before)
print("batch_already_present:", already)
room_ids = [
    "grid_20261006-201353",
    "grid_20261006-201854",
    "grid_20261006-201935",
    "grid_20261006-202016",
    "grid_20261006-202055",
]
room_sum = sum(v for k, v in snap0.breakdown.items() if any(r in k for r in room_ids))
print("room_entries_counted:", room_sum, "(expect 324; dedup basis)")

rec = led.record_run(
    KIND,
    BATCH,
    0,
    note=(
        "R-dao OOS exam of F-dao 324-cell strategy-family grid; NO new backtests: the 324 "
        "machine backtests already counted under factory_grid_batch_a batch_ids "
        "grid_20261006-201353/201854/201935/202016/202055 (18+54+54+54+144); this entry is a "
        "0-increment pointer to avoid double-counting the DSR denominator; verdicts=docs/_working/"
        "fexam/grid_strategy_oos_v1.yaml (all rework, IS window not run by device); prereg frozen "
        "2026-10-06T19:27Z before any verdict calc"
    ),
    recorded_by="st-matrix-20261007",
)
after = led.cumulative_trials()
print("record_run:", rec)
print("cumulative_trials_after:", after, "| delta:", after - before)
assert after == before, "ledger must not change: 0-increment pointer entry"
print("DSR receipt OK: batch registered, denominator unchanged (no double count)")
