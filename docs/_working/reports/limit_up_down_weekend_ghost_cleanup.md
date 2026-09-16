---
ttl: task_bound
completes_when: 裁定#289 已落地（2026-09-17）；残余=alt_regime_signal F23 周末键 20 行待 Owner 另裁，裁后本件可归档
---

# limit_up_down 周末幽灵行存量清理报告（GW-P）

- 会话: st-ghostclean-20260916 | 日期: 2026-09-16 | 授权: Owner 开工令（破坏性操作授权生效，裁定#277 残余）
- 表: `c1_market.limit_up_down`（ClickHouse ReplacingMergeTree，PARTITION BY toYYYYMM(trade_date)，ORDER BY (trade_date, symbol)）
- 守卫真源: LUE-2 周末幽灵行守卫（裁定#257⑤）采集端 src/zephyr/data/implementations/akshare_provider.py:3200+（窗口内交易日集+weekday()>=5 剔除）

## 1. 成因与真实性（RULE-DATA-OPS 之必要性/真实性）

akshare 涨停池接口非交易日回吐最近交易日池，采集按日抓取把周五池复制进周六/周日分区
（挖矿实证 limit_up_event_load_mining.md §2：5 对周末分区行数与前一交易日完全相等）。
表 DDL 口径=交易日历（trade_date Date，日频成品，business_data_categories.yaml category_id=market_limit_up_down），
A股周末不交易，周末分区无合法语义，判定为伪行。

## 2. 普查清单（2026-09-16 清理前，CH 只读）

总行数 5378（2026-07-20 ~ 2026-09-16）；weekend=664 行/10 分区，weekday=4714 行/43 日。

| trade_date | 星期 | 行数 | 幽灵对照（前一交易日行数） |
|---|---|---|---|
| 2026-08-15 | 六 | 73 | 2026-08-14(五)=87 |
| 2026-08-16 | 日 | 73 | 同上 |
| 2026-08-22 | 六 | 67 | 2026-08-21(五)=75 |
| 2026-08-23 | 日 | 67 | 同上 |
| 2026-08-29 | 六 | 83 | 2026-08-28(五)=171 |
| 2026-08-30 | 日 | 83 | 同上 |
| 2026-09-05 | 六 | 48 | 2026-09-04(五)=76 |
| 2026-09-06 | 日 | 48 | 同上 |
| 2026-09-12 | 六 | 61 | 2026-09-11(五)=71 |
| 2026-09-13 | 日 | 61 | 同上 |

注: 挖矿时（守卫前）周末行数与周五完全相等（63/63 等）；本普查时周五值已被后续盘后采集更新，
不等不再成立，但周末伪行性质由交易日历口径独立成立（周六抽样行 ingest_ts=2026-09-13 21:42:58 UTC，
即周日采集时回吐的周五池快照）。

幽灵行样例（2026-09-12 前 5 行）:
    2026-09-12  000017  深中华A   7.50  -9.9639  559686688    跌停  akshare  2026-09-13 21:42:58+00
    2026-09-12  000428  华天酒店  4.64 -10.0775  436431744    跌停  akshare  2026-09-13 21:42:58+00
    2026-09-12  000523  红棉股份  4.01 -10.0896  1482227184   跌停  akshare  2026-09-13 21:42:58+00
    2026-09-12  000636  风华高科 55.99  10.0000  9984863744   涨停  akshare  2026-09-13 21:42:58+00
    2026-09-12  000737  北方铜业 14.74 -10.0122  2139939792   跌停  akshare  2026-09-13 21:42:58+00

## 3. 下游污染路径（清理前实态）

| 消费方 | 查询形态 | 是否可读到幽灵行 |
|---|---|---|
| alt_data/alt_regime_signals.py _compute_limitup（F23 涨停情绪） | 全表扫 WHERE limit_type=涨停，无周末过滤 | 会（周末伪日进连板/晋级率序列，周五池重复致晋级率虚高） |
| regime/features/regime_data_loader.py _load_limit_up_down | 窗口 trade_date BETWEEN，无周末过滤 | 会（窗口覆盖 2026-08-15+ 即读入） |
| data/sector_report_builder.py SQL_LIMIT_UP_DOWN_WINDOW | 窗口 BETWEEN，无周末过滤 | 会（窗口扫过周末即读入） |
| signal_ashare/limit_up/limit_up_reason_attribution.py、limit_up_followthrough.py | 单日 trade_date = :d | 仅当调用方传入周末日期（低风险） |
| daban_board_event_deriver.py（deriver） | 不读本表（kline/stk_limit 自算） | 否 |
| FPB-4 修复后派生路径 _derive_limit_up_down_from_kline | kline_daily×stk_limit 精确 join，不读本表 | 否 |

## 4. 三步验证留痕（RULE-DATA-OPS）

1. 必要性: 上表——多消费方无周末过滤，幽灵行污染涨停情绪/连板/晋级率与窗口聚合。
2. 真实性: DDL 口径=交易日历；采集守卫 LUE-2（裁定#257⑤）已证周末不该有分区；
   GW-G2 实证派生双表周末分区=0（守卫后零新增），存量皆守卫前累积。
3. 可逆性: 全量 664 行已备份（见 §5），可按 manifest 原列序重放（ReplacingMergeTree 幂等）。

## 5. 备份（T3）

- 文件: data/backups/c1_market_limit_up_down_weekend_rows_20260916_pre_ghostclean.csv
- 行数: 664（列=trade_date,symbol,name,close,pct_change,amount,limit_type,data_source,ingest_ts,exchange,symbol_canonical）
- SHA256: 8c59014c02bda7cc36af767b0520d6dfa8db59a1536909af52c7745e96e93bd3（71,404 字节，写后进程外复核一致）
- manifest: 同名 .manifest.json（逐分区行数+恢复指引）

## 6. 清理执行与对照（T4）

- 方式: ch_writer 正道（get_client + ALTER TABLE ... DELETE WHERE trade_date = <分区> SETTINGS mutations_sync = 2），逐分区 10 条。
- 逐分区 pre 计数全部=备份行数（73/73/67/67/83/83/48/48/61/61），post 全部=0。
- 复验: 全表周末行=0；weekday=4714 行/43 日不变；system.mutations 无残留。
- 下游核验（T5）: 2026-09-11(五)=71 行与清理前一致；下游涨停序列周末键=空；
  守卫回归 tests/zephyr/data/test_internal_compute_limit_up_routing.py + tests/feedback/scheduling/test_collectors.py = 85 passed。

## 7. GW-P2 接力核验附录（2026-09-17，st-ghostclean2-20260916）

GW-P 因速率限制阵亡后接力。总包预判"删除大概率未做"，实态复核推翻该预判——**清理已由
GW-P 在阵亡前完成**，本文 §1-§6 为实况记录而非预写。接力工作=独立复核+下游抽查+裁定登记，
未重复执行删除（禁为做而做）。

1. **实态复核（T1/T3）**: system.mutations 实证 mutation_538~547（DELETE WHERE
   trade_date=<10 个周末分区>，SETTINGS mutations_sync=2）全部 is_done=1；当前全表
   4714 行全部为工作日（43 日，2026-07-20~09-16；区间 59 天-16 周末日=43 自洽），
   周末分区=0，对照日 2026-09-11(五)=71 行——与 §2/§6 完全一致。
2. **备份复核（T2）**: data/backups/c1_market_limit_up_down_weekend_rows_20260916_pre_ghostclean.csv
   SHA256 复算=8c59014c02bda7cc36af767b0520d6dfa8db59a1536909af52c7745e96e93bd3（与 §5 及
   manifest 内嵌值一致），665 行（664 数据+表头），manifest 逐分区行数与 §2 表吻合。
   目录归属已厘清：data/backup/stock_indicator_circmv_20260916/=GW-S 车道件（禁碰），
   本件在 data/backups/。备份 CSV 未入库（还原工件留盘，路径见裁定#289 evidence）。
3. **守卫回归（T4）**: 两测试文件复跑 85 passed（2026-09-17），与 §6 一致。
4. **静态证明（T4）**: daban_board_event_deriver.py 零引用 limit_up_down；
   FPB-4 _derive_limit_up_down_from_kline（regime/features/regime_data_loader.py:421）
   仅读 market_kline_daily×market_stk_limit——两者结构上不受本清理影响，"零变化"成立。
5. **下游抽查（T4）+ §6 勘误**: §6 "下游涨停序列周末键=空"与持久化表实态不符——
   c1_market.alt_regime_signal 中 F23_LIMITUP_EMOTION 仍有 20 行周末键（幽灵派生存量，
   最新 signal_date=2026-09-13，清理后零新增）。该存量属边界外另一车道，GW-P2 不处置，
   已登记裁定#289 遗留待裁项。旁注：F14_BTC_MOMENTUM_30D 周末键（212 行）属 7x24 合法
   语义，F7/F8 事件信号周末触发亦可能合法，勿按周末一刀切清理。
6. **裁定登记（T5）**: 裁定#289 已入 ruling_registry.yaml（与本文档同 commit 原子）；
   登记时 max=#288（GW-S 于 02:00:04 落地，早于总包"已占至 #287"的情报快照）。

