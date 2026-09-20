---
ttl: task_bound
---

# 技术指标库线 交接包（2026-09-15 · st-tilib 系列会话 → 接管会话）

> 使命：技术指标库广度工程+历史数据回填。九个施工批全部落地，当前**卡在 P0 运维事故**（见 §0）。

## 0. P0 阻塞项：CH 内存爆满（接管会话第一件事）

**现状**：c1_market.technical_indicator 表 162 列宽表，多轮回填产生 **1304 个 active parts / 125 GB 磁盘**，CH 进程 RSS 顶满 7.28/7.15 GiB 上限——**当前连单行 SELECT 都返回 Code 241**（OvercommitTracker 拒绝），全项目 CH 读写实质不可用。

**恢复三选一（需 Owner 拍板）**：
1. `ALTER TABLE c1_market.technical_indicator DELETE IN PARTITION ... `？不行——正确做法是 **OPTIMIZE TABLE ... FINAL** 强制合并 parts 释放多版本内存（重 IO 长时间，需停其他 CH 负载执行）
2. 调大 users.xml 的 `max_memory_usage`（当前 7.15 GiB）后重启 CH
3. 等待 CH 后台 merge 自行消化（ parts 会慢慢降，但当前 OvercommitTracker 会压制 merge 线程，可能僵局）

恢复判据：`SELECT count() FROM system.parts WHERE database='c1_market' AND table='technical_indicator' AND active`（parts 数显著下降）+ 单行 SELECT 成功。恢复后执行 §3 收口探针。

## 1. 项目背景（30 秒版）

ZephyrAlpha=个人量化交易平台（Windows 单机，Python 3.12，ClickHouse 存储，Git Bash）。技术指标库=REG-IND-001 注册表管控的 OHLCV 衍生指标宽表 `c1_market.technical_indicator`（8 大类 101 指标/162 列/171 物理列）。两库分工：**图形形态归图形会话（candlestick_scanner/pattern_event）**，**技术指标归本线**。设计契约演变：纯 OHLCV → 已批扩张（流通股本类待建）。

## 2. 已完成 9 批总账（全部在 HEAD）

| 批 | 内容 | commit |
|---|---|---|
| 批1 | A股标配 BIAS/PSY/LWR/DKX + 统计族 4 | 48406d924c |
| 批2a | HMA/ZLEMA/KAMA/VORTEX/SUPERTREND/DPO/NATR/TRANGE | 93869bfee2 |
| 批2b | TSI/SMI/FISHER/KST/CONNORSRSI/QQE/STC/RVGI/ELDER 系 16 个 | 5fda555c4d |
| 批3 | Ichimoku 补实现 + 循环族 HT 系 5（Ehlers 相位累积口径） | f5df04f80a |
| 批6 | 挖矿立卡清偿 14 个（RV 波动率族/STOCH 本体/BRAR+CR 等） | 15a4326bc1 |
| 批7 | 消费端接线：indicator_reader PIT API + 消费样板 + 锚点 | 53a00cdfb7 |
| 薄视图→B | IND-REV-001 退役（裁定#233，图形会话执行） | 579e5763ce→1ecf6275cd |
| 批8 | M-L4 经典族 10 个（Alligator/GMMA/GannHiLo/AC/Fractals/Elder/Coppock/Squeeze/WaveTrend/ForceIndex） | 011ad6ba58 |
| 治本 | token 工具 CAS 化 + apply 脚本子进程隔离+探针 + ConnorsRSI/BRAR/CR/autodiscover 四修 | 0450a5e962/7f3d8c9a14/1bfba66acd |

## 3. 施工清单（剩余全部）

### 批 9：stock_daily_basic 数据批（筹码族地基，P1）
1. 新表 `c1_market.stock_daily_basic` DDL-as-Code（schemas/categories/market/，字段：trade_date/symbol/turnover_rate/float_share/circ_mv/total_mv）
2. 数据源：AKShare 东财历史接口（`stock_zh_a_hist` 含换手率列）逐标的采集；或 tushare `daily_basic`（token 在案）
3. 采集 provider（参照 src/zephyr/data/implementations/akshare_provider.py 模式）+ tasks.yaml 任务注册 + 全市场历史回填
4. 验收：000852 换手率 2021 起 100% 覆盖

### 批 10：筹码族施工（依赖批 9）
- CYQ 筹码分布族：chips_winner（获利盘比例）/chips_avg_cost/chips_cost_5/chips_cost_95（迭代衰减算法，标准全市场通用模型）
- SCR 筹码集中度、CYC 成本均线（通达信口径）
- 契约扩张裁定记录进 16 号设计文档（指标输入首次引入换手率）

### 杂项（随批搭车）
- 16 号 memo §7 开放问题逐项核销状态刷新
- 探针脚本沉淀：.runtime/tmp/tilib-probe/audit_all_cols.py（全列非空审计，回填后必跑）
- **回填九轮/夜跑/十轮死于并发+内存——回填 MUST 单进程串行**（每晚 02:30 计划任务 tilib_indicator_backfill_nightly 已注册会自动跑，白天勿手动并发）

## 4. 必读文件（新会话冷启动后按序）

1. `D:\ZephyrAlpha\AGENTS.md`（宪法 L0）
2. `D:\ZephyrAlpha\.trae\rules\project_rules.md`（硬规则）
3. `D:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\16_technical_indicator_catalog.md`（指标库设计文档真源）
4. `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\technical_indicator_registry.yaml`（REG-IND-001 注册表）
5. `D:\ZephyrAlpha\schemas\categories\market\market_technical_indicator.py`（DDL-as-Code 真源，注意 9-14 已拆子目录）
6. `D:\ZephyrAlpha\docs\_working\2026-09-14-indicator-mining-batch4.md`（挖矿报告+批 5 增补）
7. `D:\ZephyrAlpha\docs\_working\2026-09-14-tilib-batch6-plan.md`（批 6 施工方案范本）

## 5. 工作文件

- 指标代码：`src/zephyr/factor/technical_indicators/`（10 文件：trend/momentum/volatility/volume/reversal/statistics/cycle + indicator_base + indicator_reader + __init__）
- 测试：`tests/zephyr/factor/technical_indicators/`（9 文件，762 tests）
- 回填器（留盘不入库）：`scripts/data/backfill_technical_indicator_dwm.py`
- 夜间计划任务：`tilib_indicator_backfill_nightly`（每日 02:30，bat=.runtime/tmp/tilib-probe/backfill_night.bat）
- 探针脚本：`.runtime/tmp/tilib-probe/`（audit_all_cols.py 全列审计/alter_columns_b6.py 逐列 ALTER 配方/fix_yaml*.py）
- 交接包（图形会话）：`.runtime/handoffs/TILIB_PATTERN_BOUNDARY_20260914.md`
- 挖矿报告：`docs/_working/2026-09-14-indicator-mining-batch4.md`

## 6. 配方与坑（血泪清单，违反必炸）

1. **CH 内存 Code 241**：当前爆满（§0）。恢复前禁一切 CH 大查询/写入；恢复后回填必须**单进程串行**（并发=互相撞死+日志截停误导）
2. **ch_writer.query 强制无表头 TSV**：SELECT 列名按顺序自建 names
3. **ch_writer.query 吞错返回空串**：一切 DDL/写入后必须 system.columns 探针核实（apply 脚本已探针化但 ✓ 仍需人核）
4. **干净进程逐列 ALTER**：主进程大 DDL 触发通道污染（Code 62→TCP 失效→HTTP 500 全军覆没）
5. **safe_write_text base hash = LF 归一口径**（CRLF 文件 rb 字节 hash 会永久误拒）
6. **registry 条目 module_id 必须与指标文件头 [BLUEPRINT] 一致**（gate 按 blueprint_id 口径校验）
7. **registry 是热文件**：safe_write_text + CAS 重试 + 文本级插入（禁 yaml.dump 丢注释）
8. **新会话必先 capability_lookup**，否则队列 CAPABILITY-LOOKUP-REQUIRED 死信（lookup 后 requeue 即过）
9. **autodiscover 已无条件化**（勿回改 if==0 跳过——cycle 族漏算实证）
10. **提交走 scripts/git_commit.py 队列**（--enqueue；死信读 dead_reason 修复后 requeue）
11. **Git Bash 无 pgrep；heredoc 两次断裂**——多行 python 一律 Write 落文件执行
12. **长任务先登记 data/runtime/process_reaper_keep.txt**

## 7. 验收标准（交接确认）

- [ ] CH parts 合并恢复（§0 判据）
- [ ] 回填补齐 br_26/cr_26/ht 系/bbi/wt 系等全部 162 列 daily 历史（audit_all_cols.py 零 0 列）
- [ ] 批 9 数据批 + 批 10 筹码族按上述施工
