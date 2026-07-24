---
ttl: task_bound
---
# Schema Truth Drift Report

- 生成时间: 2026-07-24T16:38:57.250890+00:00
- 校验表数: 26
- 漂移条目: 0
- 退出码: 0 (零漂移)

## 逐表结果

| 状态 | 库.表 | 真源文件 |
|------|-------|----------|
| OK | c1_market.cross_validation_log | cross_validation_log.py |
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
| OK | c1_market.auction_snapshot | market_auction.py |
| OK | c1_market.auction_book | market_auction_book.py |
| OK | c1_market.convertible_bond_iv | market_cb_iv.py |
| OK | c1_market.futures_position | market_futures_position.py |
| OK | c1_market.futures_term_structure | market_futures_term.py |
| OK | c1_market.index_quote | market_index.py |
| OK | c1_market.index_weight | market_index_weight.py |
| OK | c1_market.kline_daily | market_kline_daily.py |
| OK | c1_market.option_iv_surface | market_option_iv.py |
| OK | c1_market.sector_list | market_sector_list.py |
| OK | c1_market.sector_meta | market_sector_meta.py |
| OK | c1_market.sector_snapshot | market_sector_snapshot.py |
| OK | c1_market.stock_list | market_stock_list.py |
| OK | c1_market.tick_data | market_tick.py |

## 漂移明细

零漂移：所有 DDL-as-Code 真源与 ClickHouse 实际表结构一致。
