---
ttl: task_bound
---
# Schema Truth Drift Report

- 生成时间: 2026-07-24T16:20:01.660838+00:00
- 校验表数: 26
- 漂移条目: 10
- 退出码: 1 (有漂移)

## 逐表结果

| 状态 | 库.表 | 真源文件 |
|------|-------|----------|
| DRIFT | c1_market.cross_validation_log | cross_validation_log.py |
| OK | c3_fundamental.analyst_forecast | fundamental_analyst_forecast.py |
| OK | c3_fundamental.balance_sheet | fundamental_balance_sheet.py |
| OK | c3_fundamental.cashflow_statement | fundamental_cashflow_statement.py |
| OK | c3_fundamental.disclosure_plan | fundamental_disclosure_plan.py |
| OK | c3_fundamental.equity_pledge_detail | fundamental_equity_pledge_detail.py |
| OK | c3_fundamental.income_statement | fundamental_income_statement.py |
| OK | c3_fundamental.industry_class_suppl | fundamental_industry_class_suppl.py |
| OK | c3_fundamental.restricted_shares | fundamental_restricted_shares.py |
| OK | c3_fundamental.rights_issue | fundamental_rights_issue.py |
| OK | c3_fundamental.share_change | fundamental_share_change.py |
| OK | c3_fundamental.share_unlock | fundamental_share_unlock.py |
| DRIFT | c1_market.auction_snapshot | market_auction.py |
| DRIFT | c1_market.auction_book | market_auction_book.py |
| OK | c1_market.convertible_bond_iv | market_cb_iv.py |
| DRIFT | c1_market.futures_position | market_futures_position.py |
| DRIFT | c1_market.futures_term_structure | market_futures_term.py |
| DRIFT | c1_market.index_quote | market_index.py |
| DRIFT | c1_market.index_weight | market_index_weight.py |
| OK | c1_market.kline_daily | market_kline_daily.py |
| DRIFT | c1_market.option_iv_surface | market_option_iv.py |
| OK | c1_market.sector_list | market_sector_list.py |
| OK | c1_market.sector_meta | market_sector_meta.py |
| DRIFT | c1_market.sector_snapshot | market_sector_snapshot.py |
| OK | c1_market.stock_list | market_stock_list.py |
| DRIFT | c1_market.tick_data | market_tick.py |

## 漂移明细

- [cross_validation_log] 真源有定义但 DB 中不存在（c1_market.cross_validation_log）
- [auction_snapshot] 列 'ingest_ts' DB 有但真源无
- [auction_book] 列 'ingest_ts' DB 有但真源无
- [futures_position] 列 'ingest_ts' DB 有但真源无
- [futures_term_structure] 列 'ingest_ts' DB 有但真源无
- [index_quote] 列 'ingest_ts' DB 有但真源无
- [index_weight] 列 'index_code' DB 有但真源无
- [option_iv_surface] 列 'ingest_ts' DB 有但真源无
- [sector_snapshot] 列 'ingest_ts' DB 有但真源无
- [tick_data] 列 'recorded_time' 真源有但 DB 无
