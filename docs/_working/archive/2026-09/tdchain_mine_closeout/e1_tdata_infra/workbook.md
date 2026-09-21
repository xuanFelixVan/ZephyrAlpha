---
ttl: task_bound
title: E1 做T 数据面基建作业簿——ETF 时区修复+板块高周期合成+缺口登记
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E1 做T 数据面基建作业簿

## 六向台账

- **目标**：交接令任务 1 数据半边，按 CH 实测缺口收窄后执行三件：①ETF 分钟族五表时区污染修复（RULE-DATA-OPS 三步验证+备份）；②板块分钟 09-11/14/15 高周期（15/30/60m）合成回灌；③剩余缺口登记（不虚做）。
- **证据**（2026-09-18 侦察，CH 实测 172.24.30.100:9000 只读）：
  - 股票分钟族健康：kline_1min 14.77 亿行 5849 只（2021-09-01→2026-09-16，纯 6 位码）；15/30/60min 全量在库（97.98M/48.86M/24.49M 行，同期同只数）——交接令"15min 表不存在"过时。
  - ETF 时区污染：kline_etf_15min toHour(trade_time)<=7 误标行=23,168,185（五表同病，trade_date<=2026-06-30 UTC 墙钟误标进 Asia/Shanghai 列）；股票族 09-14 已修过一轮（*_tzbak_20260914 在库为证）。
  - 修复工具：scripts/data/repair_etf_minute_tz_split.py（前班遗物，.gitignore:603 忽略未入库；影子表重建+8h→EXCHANGE 换名，旧表留 *_tz_bak_20260918；默认 dry-run）。
  - 板块分钟：kline_sector_intraday 10.08M 行；09-11/14/15 三天仅 1m 合成行（synth_sh/synth_eq），15/30/60m 缺；合成工具=scripts/data/synth_board_minute.py，聚合器=src/zephyr/data/kline_resampler.py。
  - 缺口登记项：kline_1min/15min 止于 09-16（09-17/18 缺，miniQMT 白班关停所致，晨间任务自然回补，登记 known_data_gaps 属 he 会话文件规避）；kline_index_intraday 不存在（intraday_l1_tracker.py:406 已登记 510300 代理，新表须碰 apply_market_tables_ddl.py=residual C1 独占→挂单）；120min 豁免（tasks.yaml:2027"60min 两根聚合"先例，查询期聚合）。
- **块**：B1 三步验证+dry-run；B2 --execute（后台 30-120min）+复测；B3 板块高周期回灌+抽样验证；B4 缺口登记回写本簿；B5 执行纪要归档（.runtime/tmp/tdchain_e1_data_exec_report.md→摘要落本簿）。
- **依赖**：residual C1（不碰三共享文件）；CH 夜间空窗（盘后）；他轴会话只读查询共存无碍。
- **三态**：执行中（代理在飞）。
- **下一步**：代理回报后回写 §执行结果，修复行数对账表入册。

## 执行结果（回写区）

（待代理回报）

## 长尾登记

- repair 脚本本身是否入库：.gitignore 白名单制（scripts/data/* 忽略），收编需改 .gitignore（共享文件）——本环节不收编，登记挂单给数据线班次；脚本内容已在执行纪要中留指纹（sha256）。
- 8803/8804 行业板 132 个无成分映射不参与分钟合成（synth_board_minute INVARIANTS 已登记）——台账记录，暂不施工。

## 执行结果（2026-09-18 06:2x 终态回写）

- **ETF 五表全部修复完成**（冻结台三代流，九轮实跑迭代定稿）：
  | 表 | 修复行数 | remaining_utc | 修复前 utc 行 |
  |---|---|---|---|
  | kline_etf_1min | 326,301,055（含 303,422,787 误标行） | 0 | 303,422,787 |
  | kline_etf_5min | 71,856,186 | 0 | 68,163,011 |
  | kline_etf_15min | 24,331,141 | 0 | 23,168,185 |
  | kline_etf_30min | 11,939,337 | 0 | 11,360,495 |
  | kline_etf_60min | 5,962,194 | 0 | 5,680,248 |
- **可逆性**：五张旧表整体保留为 *_tz_bak_20260918（反向换名即退；物理删除留 Owner 门位）。
- **工具治本三件**（scripts/ch/repair_etf_minute_tz_split.py，随批提交）：①CREATE AS 子句（Code 80）；②冻结台三代流（stage/shadow 普通 MergeTree 确定性对账 → final 原引擎原子拷贝换名）治 ReplacingMergeTree 后台折叠假报（首轮起五轮根因）；③MATERIALIZED 列排除+显式回拷列清单+max_partitions_per_insert_block。
- **RULE-DATA-OPS 三步验证**：必要性（23.17M+ 误标行毒化下游考试）、真实性（五表 precheck 边界零违例/错日零/零碰撞+平移守恒分桶全等）、可逆性（bak 换名即退）——全过留痕于 etf_tzfix_exec*.log。
- **板块 15/30/60m 合成**：裁定跳过施工（三问停止判据：无独立消费方+1m 原料系二阶近似+无现成工具且存量 15m 桶时间戳全分钟发散存疑）——缺口如实登记，不为凑数造管线。
- **已知残留**：①kline_1min/15min 止于 09-16（miniQMT 白班关停，晨间任务自愈）；②kline_index_intraday 不存在（510300 代理在案，新表需 apply_market_tables_ddl=residual C1 独占→挂单）；③repair 脚本 M11 豁免注记已加，随批收编入 git（scripts/ch/ 非 ignore 区）。
