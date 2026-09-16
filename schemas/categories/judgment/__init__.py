# [BLUEPRINT] MOD-L04-001 | schemas/categories/judgment/__init__.py | §
# [MODULE] schemas.categories.judgment
# [DOMAIN] D_DATA
# [TTL] permanent
"""判定台账（Forecast Ledger）DDL 真源子目录。

范围：作战室三任务首批四表（2026-09-16 判定台账标准 v0.1 §三）——
judgment_intraday_market_state（盘中大盘状态）/ judgment_next_day_forecast
（次日概率）/ judgment_daily_plan（晨间预案）/ judgment_plan_verification
（预案盘中验证，与 daily_plan 分表）。

铁律（标准 §一）：判定与结算分离——judgment 列组判定时刻写死（PIT 锚
asof_ts+input_cutoff_ts）；结算列组（outcome_*/eval_*/evaluated_*）只许
结算器（zephyr.plan_engine.judgment_settler）回填，判定模块禁写；
MergeTree 只增不改，修订=新 judgment_id 追加。

新表落位：判定台账新表一律入本目录；DDL 真源文件自包含（禁跨文件
import——verify_schema_truth.py 按 spec_from_file_location 裸加载，
包上下文不可用）；通用列骨架以 judgment_ledger 库件常量+漂移守卫单测
（tests/plan_engine/test_judgment_ledger.py）机械对齐。
"""
