---
ttl: task_bound
completes_when: 全流通战役 BRK-050 验收（tasks.yaml 无依赖任务数收敛）且推导器可重跑再生
---

# BRK-050 · 任务依赖推导建议清单（derive_task_dependencies.py 产物，禁手改）

- 任务总数 264；本次运行快照无 `dependencies` 声明 225 个（普查基线 262 任务 / 235 无依赖）。
- 高置信（表级唯一生产者 + 实现码或任务自述证据）建议任务数：**21**（本次 --apply 已写入 tasks.yaml）。
- 单任务扇入预算 4：超预算同族边不落地、在本文件 §2.1 登记（避免任一上游 FAILED 即 BLOCKED 的耦合放大）。
- 低置信（跨文件一跳歧义/多生产者）建议任务数：**12**（登记交总包，禁硬编）。

## 1. 高置信（已落地）

| 任务 | 新增前置 | 表 | 证据族 | 证据 |
|---|---|---|---|---|
| `kline_daily_incremental` | `crypto_kline_daily_incremental` | `c1_market.crypto_kline_daily` | impl_direct | src/zephyr/data/implementations/crypto_provider.py:285（实现函数体内表级读取） |
| `consensus_daily_build` | `research_report_detail_incremental` | `c3_fundamental.research_report` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:634 → src/zephyr/data/implementations/consensus_daily_compute.py（一跳模块读取） |
| `consensus_daily_build` | `trade_calendar_refresh` | `c1_market.trade_calendar` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:634 → src/zephyr/data/implementations/consensus_daily_compute.py（一跳模块读取） |
| `anchored_state_build` | `kline_index_incremental` | `c1_market.kline_index` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:623 → src/zephyr/regime/core/anchored_state_machine.py（一跳模块读取） |
| `dividend_incremental` | `ex_dividend_event_incremental` | `c3_fundamental.ex_dividend_event` | impl_direct | src/zephyr/data/implementations/miniqmt_provider.py:2241（实现函数体内表级读取） |
| `dividend_incremental` | `ex_dividend_event_incremental` | `c3_fundamental.ex_dividend_event` | task_prose | tasks.yaml[dividend_incremental] 自述点名任务 ex_dividend_event_incremental |
| `kline_daily_full_refresh` | `crypto_kline_daily_incremental` | `c1_market.crypto_kline_daily` | impl_direct | src/zephyr/data/implementations/crypto_provider.py:285（实现函数体内表级读取） |
| `research_report_incremental` | `research_report_detail_incremental` | `c3_fundamental.research_report` | impl_direct | src/zephyr/data/implementations/akshare_provider.py:4059（实现函数体内表级读取） |
| `calendar_event_refresh` | `trade_calendar_refresh` | `c1_market.trade_calendar` | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:1149（实现函数体内表级读取） |
| `technical_indicator_incremental` | `kline_daily_hfq_incremental` | `c1_market.kline_daily_hfq` | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:970（实现函数体内表级读取） |
| `technical_indicator_incremental` | `kline_etf_daily_incremental` | `c1_market.kline_etf_daily` | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:970（实现函数体内表级读取） |
| `kline_sector_1min_incremental` | `kline_sector_incremental` | `c1_market.kline_sector` | impl_direct | src/zephyr/data/implementations/tqcenter_provider.py:378（实现函数体内表级读取） |
| `kline_sector_5min_incremental` | `kline_sector_incremental` | `c1_market.kline_sector` | impl_direct | src/zephyr/data/implementations/tqcenter_provider.py:378（实现函数体内表级读取） |
| `kline_sector_15min_incremental` | `kline_sector_incremental` | `c1_market.kline_sector` | impl_direct | src/zephyr/data/implementations/tqcenter_provider.py:378（实现函数体内表级读取） |
| `kline_sector_30min_incremental` | `kline_sector_incremental` | `c1_market.kline_sector` | impl_direct | src/zephyr/data/implementations/tqcenter_provider.py:378（实现函数体内表级读取） |
| `kline_sector_60min_incremental` | `kline_sector_incremental` | `c1_market.kline_sector` | impl_direct | src/zephyr/data/implementations/tqcenter_provider.py:378（实现函数体内表级读取） |
| `index_valuation_daily_incremental` | `kline_index_incremental` | `c1_market.kline_index` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `pattern_event_incremental` | `pattern_evidence_certify` | `c1_market.market_pattern_certification` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:682 → src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py（一跳模块读取） |
| `pattern_win_rate_materialize` | `pattern_event_incremental` | `c1_market.market_pattern_event` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:695 → src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py（一跳模块读取） |
| `pattern_win_rate_materialize` | `pattern_evidence_certify` | `c1_market.market_pattern_certification` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:695 → src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py（一跳模块读取） |
| `pattern_evidence_certify` | `pattern_event_incremental` | `c1_market.market_pattern_event` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:722 → src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py（一跳模块读取） |
| `pattern_weight_sync` | `pattern_event_incremental` | `c1_market.market_pattern_event` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:708 → src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py（一跳模块读取） |
| `pattern_weight_sync` | `pattern_evidence_certify` | `c1_market.market_pattern_certification` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:708 → src/zephyr/signal_ashare/strategy_signal/pattern_event_job.py（一跳模块读取） |
| `daban_engine_load_daily` | `index_quote_snapshot` | `c1_market.index_quote` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:821 → src/zephyr/ex_core/daban_load_producer.py（一跳模块读取） |
| `daban_engine_load_daily` | `kline_index_incremental` | `c1_market.kline_index` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:821 → src/zephyr/ex_core/daban_load_producer.py（一跳模块读取） |
| `daban_engine_load_daily` | `market_breadth_snapshot_minute` | `c1_market.market_breadth_snapshot` | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:821 → src/zephyr/ex_core/daban_load_producer.py（一跳模块读取） |
| `road_freight_index_full_refresh` | `road_freight_index_refresh` | `c1_market.road_freight_index` | task_prose | tasks.yaml[road_freight_index_full_refresh] 自述点名任务 road_freight_index_refresh |
| `dividend_incremental_akshare` | `dividend_incremental` | `c3_fundamental.dividend` | task_prose | tasks.yaml[dividend_incremental_akshare] 自述点名任务 dividend_incremental |
| `dividend_incremental_akshare` | `ex_dividend_event_incremental` | `c3_fundamental.ex_dividend_event` | impl_direct | src/zephyr/data/implementations/miniqmt_provider.py:2241（实现函数体内表级读取） |

## 2. 低置信 / 冲突（登记交总包，禁硬编）

| 任务 | 候选前置 | 置信 | 证据族 | 证据 |
|---|---|---|---|---|
| `market_breadth_snapshot_minute` | `st_stock_list_refresh` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:5062 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `market_breadth_snapshot_minute` | `st_stock_list_refresh` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:5062 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `market_breadth_snapshot_minute` | `st_status_premarket` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:5062 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `market_breadth_snapshot_minute` | `st_status_premarket` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:5062 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `market_breadth_snapshot_minute` | `st_namechange_backfill` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:5062 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `market_breadth_snapshot_minute` | `st_namechange_backfill` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:5062 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `ex_dividend_event_incremental` | `dividend_incremental_akshare` | medium | impl_direct | src/zephyr/data/implementations/akshare_provider.py:3468（实现函数体内表级读取） |
| `ex_dividend_event_incremental` | `dividend_incremental_akshare` | medium | impl_direct | src/zephyr/data/implementations/miniqmt_provider.py:2241（实现函数体内表级读取） |
| `ex_dividend_event_incremental` | `dividend_incremental` | medium | impl_direct | src/zephyr/data/implementations/akshare_provider.py:3468（实现函数体内表级读取） |
| `ex_dividend_event_incremental` | `dividend_incremental` | medium | impl_direct | src/zephyr/data/implementations/miniqmt_provider.py:2241（实现函数体内表级读取） |
| `option_iv_surface_incremental` | `option_kline_incremental` | medium | impl_direct | src/zephyr/data/implementations/miniqmt_provider.py:2503（实现函数体内表级读取） |
| `option_iv_surface_incremental` | `option_kline_full_refresh` | medium | impl_direct | src/zephyr/data/implementations/miniqmt_provider.py:2503（实现函数体内表级读取） |
| `st_namechange_backfill` | `kline_daily_full_refresh` | medium | impl_direct | src/zephyr/data/implementations/tushare_provider.py:1393（实现函数体内表级读取） |
| `st_namechange_backfill` | `kline_daily_delisted_backfill` | medium | impl_direct | src/zephyr/data/implementations/tushare_provider.py:1393（实现函数体内表级读取） |
| `st_namechange_backfill` | `kline_daily_incremental` | medium | impl_direct | src/zephyr/data/implementations/tushare_provider.py:1393（实现函数体内表级读取） |
| `daban_board_event_derive` | `kline_daily_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:785 → src/zephyr/data/implementations/daban_board_event_deriver.py（一跳模块读取） |
| `daban_board_event_derive` | `kline_daily_delisted_backfill` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:785 → src/zephyr/data/implementations/daban_board_event_deriver.py（一跳模块读取） |
| `daban_board_event_derive` | `st_namechange_backfill` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:785 → src/zephyr/data/implementations/daban_board_event_deriver.py（一跳模块读取） |
| `daban_board_event_derive` | `tick_backfill_weekly` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:785 → src/zephyr/data/implementations/daban_board_event_deriver.py（一跳模块读取） |
| `auction_book_snapshot` | `st_stock_list_refresh` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:4933 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `auction_book_snapshot` | `st_status_premarket` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:4933 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `auction_book_snapshot` | `st_namechange_backfill` | medium | impl_module | src/zephyr/data/implementations/miniqmt_provider.py:4933 → src/zephyr/data/market_breadth_collector.py（一跳模块读取） |
| `index_adjustment_derive` | `index_constituent_refresh` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:1240（实现函数体内表级读取） |
| `index_adjustment_derive` | `index_constituent_refresh` | medium | task_prose | tasks.yaml[index_adjustment_derive] 自述点名表 ['c1_market.index_constituent'] |
| `index_adjustment_derive` | `index_member_postclose` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:1240（实现函数体内表级读取） |
| `index_adjustment_derive` | `index_member_postclose` | medium | task_prose | tasks.yaml[index_adjustment_derive] 自述点名表 ['c1_market.index_constituent'] |
| `index_adjustment_derive` | `index_member_premarket` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:1240（实现函数体内表级读取） |
| `index_adjustment_derive` | `index_member_premarket` | medium | task_prose | tasks.yaml[index_adjustment_derive] 自述点名表 ['c1_market.index_constituent'] |
| `technical_indicator_full_refresh` | `kline_5min_history_backfill` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:970（实现函数体内表级读取） |
| `technical_indicator_full_refresh` | `kline_cb_full_refresh` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:970（实现函数体内表级读取） |
| `technical_indicator_full_refresh` | `kline_daily_full_refresh` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:970（实现函数体内表级读取） |
| `technical_indicator_full_refresh` | `kline_daily_delisted_backfill` | medium | impl_direct | src/zephyr/data/implementations/internal_compute_provider.py:970（实现函数体内表级读取） |
| `index_valuation_daily_backfill` | `macro_data_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `index_valuation_daily_backfill` | `eia_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `index_valuation_daily_backfill` | `macro_worldbank_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `index_valuation_daily_backfill` | `macro_fred_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `kline_index_calc_refresh` | `kline_daily_incremental` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:933 → src/zephyr/data/implementations/index_eqw_compute.py（一跳模块读取） |
| `kline_index_calc_refresh` | `kline_daily_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:933 → src/zephyr/data/implementations/index_eqw_compute.py（一跳模块读取） |
| `kline_index_calc_refresh` | `kline_daily_delisted_backfill` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:933 → src/zephyr/data/implementations/index_eqw_compute.py（一跳模块读取） |
| `futures_warehouse_receipt_backfill_czce` | `futures_warehouse_receipt_incremental` | medium | task_prose | tasks.yaml[futures_warehouse_receipt_backfill_czce] 自述点名任务 futures_warehouse_receipt_incremental |
| `futures_warehouse_receipt_backfill_czce` | `futures_warehouse_receipt_backfill_shfe` | medium | task_prose | tasks.yaml[futures_warehouse_receipt_backfill_czce] 自述点名任务 futures_warehouse_receipt_incremental |
| `index_valuation_daily_compute_after_ingest` | `macro_data_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `index_valuation_daily_compute_after_ingest` | `eia_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `index_valuation_daily_compute_after_ingest` | `macro_worldbank_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |
| `index_valuation_daily_compute_after_ingest` | `macro_fred_full_refresh` | medium | impl_module | src/zephyr/data/implementations/internal_compute_provider.py:950 → src/zephyr/data/implementations/index_valuation_compute.py（一跳模块读取） |

### 2.1 丢弃边与跨日界标注

- `market_breadth_snapshot_minute` ← st_stock_list_refresh：跨日界依赖（daily_capital 晚于 intraday_minute，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `market_breadth_snapshot_minute` ← st_stock_list_refresh：跨日界依赖（daily_capital 晚于 intraday_minute，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `option_iv_surface_incremental` ← option_kline_incremental：跨日界依赖（daily_kline 晚于 intraday_realtime，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `kline_daily_full_refresh` ← crypto_kline_daily_incremental：跨日界依赖（daily_crypto 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `research_report_incremental` ← research_report_detail_incremental：跨日界依赖（research_nightly 晚于 news_slow，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `st_namechange_backfill` ← kline_daily_incremental：跨日界依赖（daily_kline 晚于 monthly_static，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← kline_1min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← kline_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← st_stock_list_refresh：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← st_status_premarket：跨日界依赖（pre_market 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← stk_limit_premarket：跨日界依赖（pre_market 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← stk_limit_postclose：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← tick_data_snapshot：跨日界依赖（intraday_realtime 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← futures_tick_intraday：跨日界依赖（intraday_realtime 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `daban_board_event_derive` ← st_stock_list_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← stk_limit_postclose：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← kline_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← kline_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← tick_data_snapshot：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← futures_tick_intraday：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← st_status_premarket：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_board_event_derive` ← stk_limit_premarket：超单任务扇入预算 4（同族冗余边，登记待裁）
- `auction_book_snapshot` ← st_stock_list_refresh：跨日界依赖（daily_capital 晚于 auction_highfreq，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_adjustment_derive` ← index_member_premarket：跨日界依赖（pre_market 晚于 monthly_static，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_adjustment_derive` ← index_member_postclose：跨日界依赖（daily_capital 晚于 monthly_static，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_adjustment_derive` ← index_member_premarket：跨日界依赖（pre_market 晚于 monthly_static，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_adjustment_derive` ← index_member_postclose：跨日界依赖（daily_capital 晚于 monthly_static，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_incremental` ← kline_futures_incremental：跨日界依赖（daily_capital 晚于 daily_kline，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_incremental` ← kline_us_daily_incremental：跨日界依赖（daily_capital 晚于 daily_kline，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_incremental` ← kline_us_daily_qmt_incremental：跨日界依赖（daily_capital 晚于 daily_kline，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_incremental` ← global_hsi_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← global_nikkei_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← global_kospi_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← global_usdcnh_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_index_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_index_calc_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_monthly_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_monthly_hfq_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_880_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_880_resample：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_weekly_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_weekly_hfq_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_futures_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_us_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_us_daily_qmt_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_etf_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_etf_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_etf_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_etf_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_etf_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_hk_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_lof_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_lof_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_lof_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_lof_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_lof_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_sector_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← global_wti_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← global_gold_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_5min_history_backfill：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_cb_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_daily_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_daily_delisted_backfill：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_futures_full：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_incremental` ← kline_us_daily_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_15min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_1min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_30min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_5min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_60min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_cb_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_daily_hfq_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_etf_15min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_etf_1min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_etf_30min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_etf_5min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_etf_60min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_etf_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_futures_incremental：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← global_wti_daily_incremental：跨日界依赖（pre_market 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← global_gold_daily_incremental：跨日界依赖（pre_market 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← global_hsi_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← global_nikkei_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← global_kospi_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← global_usdcnh_daily_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_hk_daily_incremental：跨日界依赖（intraday_realtime 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_index_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_index_calc_refresh：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_lof_15min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_lof_1min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_lof_30min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_lof_5min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_lof_60min_incremental：跨日界依赖（intraday_minute 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_monthly_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_monthly_hfq_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_880_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_880_resample：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_1min_incremental：跨日界依赖（intraday_sector 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_5min_incremental：跨日界依赖（intraday_sector 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_15min_incremental：跨日界依赖（intraday_sector 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_30min_incremental：跨日界依赖（intraday_sector 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_sector_60min_incremental：跨日界依赖（intraday_sector 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_us_daily_incremental：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_us_daily_qmt_incremental：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_weekly_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_weekly_hfq_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `technical_indicator_full_refresh` ← kline_futures_full：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_us_daily_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_futures_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_us_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_us_daily_qmt_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_cb_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_daily_hfq_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_etf_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← global_hsi_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← global_nikkei_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← global_kospi_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← global_usdcnh_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_index_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_index_calc_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_monthly_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_monthly_hfq_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_880_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_880_resample：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_weekly_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_weekly_hfq_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_etf_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_etf_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_etf_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_etf_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_etf_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_hk_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_lof_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_lof_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_lof_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_lof_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_lof_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_1min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_5min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_15min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_30min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← kline_sector_60min_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← global_wti_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `technical_indicator_full_refresh` ← global_gold_daily_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `kline_sector_1min_incremental` ← kline_sector_incremental：跨日界依赖（daily_kline 晚于 intraday_sector，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `kline_sector_5min_incremental` ← kline_sector_incremental：跨日界依赖（daily_kline 晚于 intraday_sector，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `kline_sector_15min_incremental` ← kline_sector_incremental：跨日界依赖（daily_kline 晚于 intraday_sector，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `kline_sector_30min_incremental` ← kline_sector_incremental：跨日界依赖（daily_kline 晚于 intraday_sector，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `kline_sector_60min_incremental` ← kline_sector_incremental：跨日界依赖（daily_kline 晚于 intraday_sector，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_incremental` ← eia_petroleum_incremental：跨日界依赖（daily_capital 晚于 daily_kline，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_incremental` ← macro_data_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_incremental` ← eia_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_incremental` ← macro_worldbank_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_incremental` ← macro_fred_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_backfill` ← kline_index_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_backfill` ← macro_data_incremental：跨日界依赖（event_driven 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_backfill` ← eia_petroleum_incremental：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_backfill` ← macro_fred_incremental：跨日界依赖（event_driven 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_backfill` ← eia_petroleum_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_backfill` ← kline_index_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_backfill` ← macro_data_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_backfill` ← macro_fred_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_engine_load_daily` ← daban_board_event_derive：超单任务扇入预算 4（同族冗余边，登记待裁）
- `daban_engine_load_daily` ← stock_indicator_full_refresh：超单任务扇入预算 4（同族冗余边，登记待裁）
- `dividend_incremental_akshare` ← ex_dividend_event_incremental：跨日界依赖（daily_event 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `dividend_incremental_akshare` ← dividend_incremental：跨日界依赖（disabled 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_compute_after_ingest` ← kline_index_incremental：跨日界依赖（daily_kline 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_compute_after_ingest` ← macro_data_incremental：跨日界依赖（event_driven 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_compute_after_ingest` ← eia_petroleum_incremental：跨日界依赖（daily_capital 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_compute_after_ingest` ← macro_fred_incremental：跨日界依赖（event_driven 晚于 weekend_calibration，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）
- `index_valuation_daily_compute_after_ingest` ← eia_petroleum_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_compute_after_ingest` ← kline_index_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_compute_after_ingest` ← macro_data_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）
- `index_valuation_daily_compute_after_ingest` ← macro_fred_incremental：超单任务扇入预算 4（同族冗余边，登记待裁）

## 3. 同源争用面（BRK-067 型，供串行化排班核对）

- `miniqmt` @ `daily_capital` 同批 5 任务：block_trade_qmt_placeholder, dragon_tiger_qmt_placeholder, kline_futures_incremental, kline_us_daily_qmt_incremental, margin_trading_qmt_placeholder
- `miniqmt` @ `daily_event` 同批 3 任务：earnings_forecast_incremental, ex_dividend_event_incremental, express_report_incremental
- `miniqmt` @ `daily_kline` 同批 10 任务：adj_factor_incremental, kline_cb_incremental, kline_daily_hfq_incremental, kline_daily_incremental, kline_etf_daily_incremental, kline_index_incremental, kline_monthly_hfq_incremental, kline_monthly_incremental, kline_weekly_hfq_incremental, kline_weekly_incremental
- `miniqmt` @ `intraday_minute` 同批 16 任务：kline_15min_incremental, kline_1min_incremental, kline_30min_incremental, kline_5min_incremental, kline_60min_incremental, kline_etf_15min_incremental, kline_etf_1min_incremental, kline_etf_30min_incremental, kline_etf_5min_incremental, kline_etf_60min_incremental, kline_lof_15min_incremental, kline_lof_1min_incremental, kline_lof_30min_incremental, kline_lof_5min_incremental, kline_lof_60min_incremental, market_breadth_snapshot_minute
- `miniqmt` @ `intraday_realtime` 同批 10 任务：convertible_bond_iv_incremental, futures_kline_qmt_incremental, futures_tick_intraday, hk_kline_incremental, index_quote_snapshot, kline_hk_daily_incremental, l2_tick_snapshot, option_greeks_incremental, option_iv_surface_incremental, tick_data_snapshot
- `miniqmt` @ `monthly_static` 同批 4 任务：index_weight_refresh, kline_5min_history_backfill, sector_list_refresh, stock_list_refresh
- `miniqmt` @ `nightly_financial` 同批 5 任务：balance_sheet_incremental, cashflow_statement_incremental, financial_indicator_incremental, income_statement_incremental, main_business_incremental
- `miniqmt` @ `weekend_calibration` 同批 3 任务：hk_kline_full_refresh, kline_cb_full_refresh, kline_daily_full_refresh
- `tdx` @ `intraday_sector` 同批 5 任务：kline_sector_15min_incremental, kline_sector_1min_incremental, kline_sector_30min_incremental, kline_sector_5min_incremental, kline_sector_60min_incremental
- `tickflow` @ `daily_capital` 同批 2 任务：kline_us_daily_incremental, us_index_incremental
- `tickflow` @ `weekend_calibration` 同批 2 任务：kline_us_daily_full_refresh, us_index_full_refresh
- `tqcenter` @ `daily_kline` 同批 3 任务：kline_sector_880_incremental, kline_sector_880_resample, kline_sector_incremental

## 4. 重跑方式

```bash
python scripts/derive_task_dependencies.py --apply   # 幂等：已声明的边不重复加
```

真源：`src/zephyr/data/config/tasks.yaml` + 品类表名册 + 实现码。
