---
ttl: permanent
doc_type: architecture_view
title: 技术指标施工计划
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.1"
date: 2026-08-15
topic: technical_indicator_build_plan
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：指标计算库 7 文件（基类 + 5 大类 + 自动注册）对齐通达信口径，全周期覆盖（1min~月线 9 周期，120min 由 60min 两根聚合）；施工期 243 单元测试转绿，2026-08-16 复核实测套件已增至 418 用例（413 过 5 跳过）；2026-08-13 第一批（会话 AI-REG-IND-001）新建技术指标注册表 40 条目/58 输出列（复核当日实测 41 条）。
>
> **最终成果**：技术指标全周期计算能力生产态 + 注册表落地；分钟级指标回算与 18 号冷归档联动执行。
>
> **未做事项及原因**：00_index 对本目录篇的"8 大类"描述未同步——重建后分类口径以代码真源为准（5 大类），仅剩索引描述同步项（目录篇 §7 已登记）。

# 技术指标施工计划

> **性质**：architecture_view / 施工计划（施工流程组织：目标→现状→改动→验证→不做）。
> **配套**：[16_technical_indicator_catalog.md](16_technical_indicator_catalog.md)（指标目录——what，本文是 how）；[18_cold_archive_build_plan.md](18_cold_archive_build_plan.md)（冷归档——为本文回算腾存储空间）。
> **历史说明**：00_index 标本文"active v1.3.0"，磁盘仅存 0.1.0 骨架——完整版曾丢失，本版重建为 1.0.0。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G01 数据与特征层（地基层·1x 段位） |
| 依赖 | [16_technical_indicator_catalog](16_technical_indicator_catalog.md)（指标目录） |
| 状态 | ✅ active v1.0.1（计算/存储/测试已完成；调度挂接+分钟周期回算进行中） |

## 2. 施工范围

覆盖传统技术指标（40 指标/58 输出列/5 大类，清单见 catalog §6）的：
- 计算逻辑实现（`src/zephyr/factor/technical_indicators/`）——✅ 已完成
- 存储表设计（ClickHouse 单表 + period 列，`c1_market.technical_indicator`）——✅ 已完成
- 调度任务（增量 + 全量回算）——🟧 Provider 已完成，任务挂接未闭环
- 验证测试（`tests/zephyr/factor/technical_indicators/`，243 用例 + provider 16 用例）——✅ 已完成

## 3. 施工步骤（含现状）

| # | 步骤 | 状态 |
|---|---|---|
| 1 | 指标计算库 7 文件（indicator_base + 5 大类 + __init__ 自动注册），对齐通达信口径 | ✅ 完成（production） |
| 2 | 存储表 schema（单表+period+trade_time+双键分区）+ apply_schema --verify | ✅ 完成 |
| 3 | InternalComputeProvider（9 周期 _PERIOD_MAP、120min 两根聚合、100 只/批防 OOM、ALL_PERIODS 顺序） | ✅ 完成 |
| 4 | 测试锁定（40 指标/58 列契约 + 数值用例 + Registry↔DDL 双向交叉校验） | ✅ 完成（243+16 用例） |
| 5 | **调度闭环**：scheduler.py 补 source=="internal" 分支 + tasks.yaml 登记 technical_indicator_incremental（每日盘后日线）/ technical_indicator_full_refresh（周末 9 周期） | 🔨 待施工（P0，catalog §7①） |
| 6 | 存储空间腾空（18 号冷归档阶段 1：tick 2022-2024 + K 线 2019 年前 → 腾 147.8 GiB） | 🟧 进行中（18 号主导） |
| 7 | 分钟周期全量回算（顺序与预算见 §3.1） | 🟧 进行中（60min/120min 已在跑；1min 90 天滚动回算进程运行中——2026-08-12 实测 `.runtime/tmp/backfill_indicators.py --period 1min --days 90` 在役） |
| 8 | REG-IND-001 YAML 注册表施工（条目从 catalog §6 迁入） | 🔨 待施工（62 号 P1-A） |

### 3.1 回算需求与周期优先级

**总量口径**：6 个分钟周期回算需求 **~198 GiB → 缩减后 ~162 GiB**（18 号 §1.1/§2.4）。口径注意：198/162GB **只含 6 个分钟周期**（60min 64M 行/120min 32M/30min 55M/15min 66M/5min 63M/1min 83M = 363M 行；每行 547 字节，浮点列+大量 NULL 致 LZ4 压缩比仅 1.087）；日/周/月三线体积小未计入，与 catalog §4"全量回算覆盖 9 周期"不矛盾。
**缩减依据**（18 号 §2.4 裁定）：分钟周期指标只算 **2019 年后**（与 K 线归档分界线对齐，60min 64M→19M 行、省 70%）；日/周/月指标全量保留（同日 K 永久保留的机构标准）。
**回算顺序**（Provider ALL_PERIODS + 18 号 §步骤 5）：daily→weekly→monthly→60min→120min（先高频刚需）→ 空间释放后 30min（滚动 5 年，55M 行/30 GiB）→ 15min（3 年，66M/36 GiB）→ 5min（1 年，63M/34 GiB）→ 1min（90 天，83M/45 GiB）。
**why 该优先级**：三级时间框架栈的使用频率——日线是交易层刚需先回算；60min/120min 是入场层次之；1min 剥头皮层保鲜期最短（90 天滚动即可），放最后且窗口最小。
**"是否先只回算日线+1分钟"的裁定**：不采用——日/60min/120min 先行但不是只算这两个；30/15/5/1min 按存储空间就绪后依序跟进（18 号步骤 5 已定）。先日线+1分钟的跳跃式顺序会让入场层（60/30min）数据断档，违背栈映射的连续性。

**复权口径分层声明**（2026-08-21 第十统筹补，63 号 Q3 裁定）：本计划所称"未复权 K 线"语义=**原始口径价 + adj_factor 点乘**，即三层架构——①事实层=kline_daily/weekly/monthly 原始价（未复权，回测撮合与成本唯一合法输入）；②解释层=c1_market.adj_factor 独立复权因子表（PIT 可复现）；③视图层=复权序列（信号/指标计算用 close×adj_factor 面板，同 #197 复权面板口径）。kline_weekly_hfq/kline_monthly_hfq=生产侧已建**视图层缓存资产**（后复权=锚定上市首日时间稳定；前复权锚定"今天"每日漂移禁入回测存储），指标栈当前未切换消费（生产侧 active/消费侧 dormant），切换属专项裁定。

### 3.2 与 18 号冷归档的衔接

D 盘可用 83.2 GB 装不下 162 GiB 回算 → 18 号两阶段：**阶段 1**（回算前）归档 tick_data 2022-2024 + 各 K 线 2019 年前，腾 147.8 GiB（D 盘可用 ~231 GB，留 69 GB 缓冲）；**阶段 2**（回算完成后）归档分钟指标 2019 年前，再腾 ~36 GiB。technical_indicator 表在阶段 1 排除归档（"正在回算中"）。衔接裁定 ARCH-DATA-COLD-001（修订 INV-RET-001/003 铁律允许"归档验证后 DROP PARTITION"；该编号尚未登记 registry，按弱引用格式无 # 前缀，登记落盘后恢复——见 18 号 §8.1/§10 开放问题 2）。

## 4. 验证计划

| 层 | 验证内容 | 现状 |
|---|---|---|
| 单元测试 | 243 用例：5 大类逐指标数值正确性（EMA/MACD/SAR 翻转/KDJ J=3K−2D/BOLL ddof=0/VR 平盘等）+ 契约（空数据/缺列/信号取值集合 {0,±1}） | ✅ 已绿 |
| 契约锁定 | `_EXPECTED_TOTAL=40` / `_EXPECTED_COLUMN_TOTAL=58` + Registry↔DDL 双向交叉校验（注册表列==schema 列，防漂移） | ✅ 已绿 |
| Provider 测试 | 16 用例：9 周期覆盖契约、120min→kline_60min 映射、聚合 OHLCV 规则、trade_time 取首根、多标的/奇数根 | ✅ 已绿 |
| 回算后验证 | ①行数对账（各周期行数 vs §3.1 预算）②抽样比对通达信同标的同周期指标值 ③NULL 率检查（预热期外 NULL 率应≈0）④分区分布检查（period×月） | 🔨 回算完成后执行 |
| 调度验证 | 步骤 5 完成后：incremental 任务每日盘后产出日线行数>0；full_refresh 周末跑通 9 周期 | 🔨 待调度闭环 |

## 5. 不做什么

- 不引 TA-Lib（口径对齐通达信 + Windows 部署负担，catalog §2）；
- 不做指标参数的自动寻优（指标是数据不是策略，参数取通达信共识默认值）；
- 不做实时盘中指标流式计算（盘中用 intraday_snapshot_factors 的 3 秒快照截面因子，两条路线不混）；
- 不回算 2019 年前分钟周期（18 号 §2.4 裁定，与 K 线归档分界对齐）；
- 不在本计划内做 REG-IND-001 施工（归 62 号注册表体系，本文只供料）。

## 6. 开放问题

1. 调度闭环（步骤 5）的施工窗口——随下次数据链路施工批次执行，还是单独立项？（建议并入，因同影响 hk_trade_calendar 等 internal 任务）
2. 1min 周期 90 天滚动窗口是否够用——剥头皮层策略未上线，待 G11/后续批次有真实需求再评。
3. 回算机时安排——363M 行单机计算，与日常采集任务的资源冲突窗口（建议周末 full_refresh 时段）。
4. 00_index 同步（越界登记）：00_index 标本文"active v1.3.0"，与本版 1.0.0 不一致，需同步（详见 33 号 §7 新发现 7 的统一登记）。

## 7. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿骨架 | 施工计划骨架。**注意**：本文件曾因未 git commit 丢失，后从代码引用重建骨架 |
| 2026-08-12 | 1.0.0 | 骨架→active：§3 回填 8 步施工步骤（5 项已完成/3 项进行中或待施工，含 1min 回算在役实测）；§3.1 回填 198→162GB 回算需求口径与周期优先级（含"先日线+1分钟"否决裁定）；§3.2 回填 18 号冷归档两阶段衔接；§4 回填五层验证计划；§5/§6 新增 | 完整版（v1.3.0）曾丢失，重建；198/162GB 仅含 6 分钟周期的口径差异显式化；调度未闭环入开放问题不擅自施工 |
| 2026-08-15 | 1.0.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08）；§3.2 衔接裁定编号改弱引用格式 | 通读+自审零发现（表格化已充分、裁定/开放问题无冗余），不为压而压；ARCH-DATA-COLD-001 未登记 registry，去 # 前缀与 18 号 §8.1 处理一致（门禁 ARCH-REFERENCE 原子性要求） |
