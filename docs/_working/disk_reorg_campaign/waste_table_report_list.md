---
ttl: task_bound
completes_when: Owner 逐表批文落地（批一张删一张；未批一律保留）
session: st-disk-ch-20260921
issue: WASTE-TABLE-REPORT-20260920
---

# 废表呈报清单（Owner 逐表批制·裁定#382 载体）

> **呈报日期**: 2026-09-20 ｜ **呈报人**: st-disk-ch-20260921（乙线总包）
> **批法**: 每表一张盘点卡，Owner 逐表批"删"；批一张删一张，未批一律保留。
> **保险**: 13 张呈报表已全部完成双副本导出（F 主库 + G 镜像 Parquet，行数核对+全量 sha256，
> 见 `waste_table_export_manifest.yaml`）——即使批错也可完整恢复。
> **机读底档**: `waste_table_inventory.yaml`（出身/零引用/内容关系/快照全字段）+ `waste_table_registry.yaml`（登记册）。

## 逐表盘点卡（13 张呈报，合计 35.39G）

### ① c3_fundamental.news_data_pre_tz2_20260828（12.88G，7,872,827 行）
- **出身档案**: 2026-08-28 行情时区修复(P0-1)前旧态快照。修复已执行并验收（st-mktfix 波次收口）。
- **零引用证据**: 全仓 grep 2 命中——均为非消费引用：`api_server.py`（仪表盘展示层标签字典）、
  `scripts/ch/rebuild_news_data_tz2.py`（当年建它的修复脚本本体）。
- **与活表关系**: 活表 `news_data` 8,185,499 行 ⊃ 本表旧态；活表健康（max=09-18）。
- **建议**: **删**（修复已验收、双副本在库）。附注：批删后同批清 api_server 标签字典两行。

### ② c3_fundamental.news_data_corrupt_20260828（12.99G，8,040,882 行）
- **出身档案**: 2026-08-28 时区修复事件族的污染数据隔离快照。污染源已修复。
- **零引用证据**: 2 命中，同上（api_server 标签 + rebuild_news_data.py 建表脚本）。
- **与活表关系**: 活表 news_data 健康且更新。
- **建议**: **删**。附注：同①批删后清标签。

### ③-⑦ c1_market.kline_etf_{1min,5min,15min,30min,60min}_tz_bak_20260918
（5.39G/1.52G/0.62G/0.35G/0.21G；325M/72M/24M/12M/6.0M 行）
- **出身档案**: 2026-09-18 ETF 分钟族时区修复的回滚保险（换名即退的通道）。
  修复已执行（dataqa R2 报告在案）。
- **零引用证据**: 五表全仓 grep **零命中**。
- **与活表关系**: 对应活表 kline_etf_* 均健康（max=09-18，行数略多于 bak=修复后追加）。
- **建议**: dataqa R1 建议**保留至修复后一个完整月度复盘（≈2026-10-18）再批删**；
  双副本已导出，到期自动获得第二道保险。Owner 也可提前批。

### ⑧ c1_market.kline_1min_tzbak_20260914（0.95G，36,194,235 行）
- **出身档案**: 09-14 1min 时区修复旧备份；该修复已被 09-18 ETF 族修复覆盖验证。
- **零引用证据**: 零命中。活表 kline_1min 14.8 亿行健康。
- **建议**: **删**。

### ⑨ c1_market.kline_5min_tzbak_20260914（0.10G，4,456,056 行）
- **出身档案**: 同⑧（5min 版）。零引用除一个 deprecated 修复脚本（repair_kline5min_tz_deprecated_update_key.py，
  名字自带 deprecated，重跑会自建新 bak 不受影响）。
- **建议**: **删**。

### ⑩ c1_market.kline_daily_bak_256（0.37G，9,669,695 行，max=08-21）
- **出身档案**: 8 月日线批次修复事件备份；后续日线链修复（final3 T1 复权链 D0+RB）已验证。
- **零引用证据**: 1 命中=api_server 展示层标签字典（非消费）。
- **建议**: **删**（批删后同批清标签）。

### ⑪ c1_market.tick_data_tzbak_20260914（0.012G，507,700 行）
- **出身档案**: tick 时区修复备份；**注意**：`scripts/data/p0_tick_backfill.py:349` 与
  `wipe_tick3days.py` 把本表当**回滚保险**引用（甲线 tick 补批正在用的回滚通道）。
- **建议**: **留观**——保留至甲线 tick 补批收口（q 批文⑩模拟盘找回完成后）再呈报删。
  体量仅 12MB，保留无成本。

### ⑫ c1_market.auction_book_limit_bak_20260908（0.006G，1,911,474 行）
- **出身档案**: 竞价簿限额修复备份（A' 竞价桥方案已落地验证）。
- **零引用证据**: 零命中。**建议**: **删**。

### ⑬ c1_market.kline_daily_hfq_bak_20260915dup（<0.01G，5,207 行）
- **出身档案**: 后复权修复 dup 备份（final3 复权链 D0+RB 已落地验证）。
- **零引用证据**: 零命中。**建议**: **删**。

## 不进呈报的 4 张（治本参照原料，裁定#382）

`balance_sheet / cashflow_statement / financial_indicator / income_statement` 的
`_bak_1970clean_20260914`（合计 ~9,783 行，<0.001G）：09-14 清理备份，1970 治本（裁定#380②，归甲线）
未启动前保留作参照原料。登记册中状态=治本参照·保留。

## 新增机制证据（裁定#380①）

- 扫描器: `scripts/ch/waste_table_scanner.py`（名字族正则命中→登记册+报警"待人工盘点"，**永不自动删**）
- 登记册: `waste_table_registry.yaml`（17 张全部在册：13 呈报 + 4 治本参照）
- 首跑报警证据: 2026-09-20 23:54 十二张新登记报警输出（第二跑 5 张补登记，合计 17）

## 批文执行记录（2026-09-22，裁定#399 落地）

- Owner 全批=废表两态制 17 张全删（裁定#399）；本班 st-disk-final-20260922 独占窗 04:40-07:30 内 17/17 DROP 完成。
- 删前保险：13 张原双副本 manifest（F+G Parquet，sha256 两侧全等）+4 张 1970clean 补导出
  （waste_table_export_manifest_1970clean.yaml，行数核对+sha256 全等）——数据第一公理全满足。
- 4 张 1970clean 附加验证=甲线治本收官报告（4ec4b1e13ed，零误清零可找回价值；3988001c3c 写入端治本）。
- 删前引用清零：tick 回滚通道两处引用退役（p0_tick_backfill.py:401 ABORT 存档 + wipe_tick3days.py 档案化）；
  api_server 标签字典 3 行清除（kline_daily_bak_256/news_data_corrupt/news_data_pre_tz2）。
- 逐张证据（行数/字节/free_space 前后快照）：.runtime/tmp/diskfinal/drop_evidence.jsonl；
  净回收 +32.0GiB（107.43→139.39GiB，CH 26 异步清理延迟数分钟属预期）。
- 底档：waste_table_registry.yaml 全部 17 条 status=已删除（裁定#399）。
