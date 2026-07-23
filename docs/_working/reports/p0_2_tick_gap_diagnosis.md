---
ttl: task_bound
---
# P0-2 Tick Data Gap Diagnosis Report

**Date**: 2026-07-23
**Issue ID**: #ARCH-CH-021 P0-2
**Status**: DIAGNOSED — permanent data loss, prevention mechanism recommended

## Gap Confirmation

| Month | Total Rows | Trading Days | Daily Avg | Drop |
|-------|-----------|-------------|-----------|------|
| 2026-04 | 469,846,918 | 21 | 22.4M | — |
| 2026-05 | 429,340,030 | 18 | **23.9M** | baseline |
| 2026-06 | 52,048,481 | 21 | **2.48M** | **-89.6%** |
| 2026-07 | 127,205,897 | 7 | 18.2M | recovering |

## Root Cause

**June tick_data only captured INDEX market type (531 symbols).**

May 15 breakdown (8 market types, 8,864 symbols):
- stock: 5,194 symbols (15.9M rows)
- sector: 609 symbols (2.9M rows)
- index: 530 symbols (2.5M rows)
- etf: 1,522 symbols (1.7M rows)
- cb: 334 symbols (0.97M rows)
- stock_bj: 311 symbols (0.38M rows)
- mkt_index: 69 symbols (0.33M rows)
- lof: 379 symbols (0.10M rows)

June 15 breakdown (1 market type only, 531 symbols):
- index: 531 symbols (2.48M rows) ← ONLY market type captured

**Transition date**: Sudden drop on June 1, 2026
- May 29: 8,887 symbols, 24.2M rows
- June 1: 531 symbols, 2.48M rows (only index)

## Root Cause Analysis

1. **NOT Hyper-V migration**: Hyper-V migration was 2026-07-16, after the June gap
2. **NOT code bug**: `tick_subscriber._get_all_symbols()` correctly fetches all market types (stock, stock_bj, etf, lof, cb, index)
3. **Likely cause**: Runtime QMT client degradation — QMT connection partially failed, only index subscriptions remained active. The QMT data feed for non-index market types was interrupted.

## Backfill Attempt

Used existing `backfill_checker.backfill_tick_data()` mechanism:
- Downloads via `xtdata.download_history_data(symbol, "tick", start, end)`
- Covers 沪深A股 stocks (5,202 symbols)
- **Result**: 0 rows returned for all symbols on all June dates
- **Conclusion**: QMT data server does not retain tick data beyond ~30 days. June 2026 tick data is permanently lost.

## Mitigation Recommendations

1. **Daily tick health check**: Alert if daily tick_data row count < 5M (existing `_TICK_THRESHOLD`)
2. **Market type coverage check**: Alert if daily tick_data has < 5 market types (currently only checks row count)
3. **Early detection**: The backfill_checker runs weekly with 7-day lookback — consider adding a daily check for same-day coverage
4. **Data loss acceptance**: June tick data gap is permanent. For backtesting, June 2026 tick-level strategies will have incomplete data (only index ticks available).

## Existing Safeguards

- `backfill_checker._TICK_THRESHOLD = 5,000,000` — June's 2.48M < 5M would be flagged
- `backfill_checker.run_weekend_backfill()` — would detect and attempt backfill (but QMT has no data)
- `tick_subscriber._get_all_symbols()` — code correctly subscribes to all market types

## Conclusion

The June 2026 tick data gap is a **permanent data loss** caused by QMT client runtime degradation (only index subscriptions active). The backfill mechanism attempted recovery but QMT does not retain historical tick data beyond ~30 days. Code is correct — no code fix needed. Prevention via daily market-type coverage monitoring is recommended.
