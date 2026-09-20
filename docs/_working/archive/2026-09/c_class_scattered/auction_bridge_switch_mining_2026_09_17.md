---
title: 竞价族桥接切换挖矿盘点与施工终态
ttl: task_bound
completes_when: 台账 §2.2-B auction 两项勾选且 9/18 退役日首日验证通过后随批次归档
---

# 竞价族桥接切换·挖矿盘点与施工终态（2026-09-17）

> 状态：✅ 施工完成（2026-09-17 收盘后窗口，Owner 夜间施工令，方案 A' 自裁落地）。
> 交付：ch_auction_derive 新模块 + qmt_bridge 双 capability + tasks.yaml 切源 + 回补 32 天 16.6 万行
> + E2E 对拍（价/量/额零失配；昨收/涨跌停 99.42%，除权除息边界 §9）+ 20 单测全绿 + 红蓝两轮。
> 盘点会话：st-auction-bridge-20260917。所有数字为 2026-09-17 凌晨实测，非推测。
> 关联真源：`docs/_working/2026-09-08-qmt-bridge-migration-ledger.md`（§2.2-B auction 两项已勾选、§5 退役日 SOP、§8.6 任务四竞价取证）。

## 1. 问题

2026-09-18 券商关停 miniQMT 通道。两张集合竞价专用表的写入任务仍是 `source=miniqmt`（xtdata.get_full_tick）：

- `auction_data_snapshot` → `c1_market.auction_snapshot`（9:15-9:25 每 10 秒，基础字段）
- `auction_book_snapshot` → `c1_market.auction_book`（9:15-9:25 每 10 秒，五档）

不切换则 9/18 09:15 起两表零产出。下游实读方：`plan_engine/scenario_planner.py`（3 处读 auction_book）、`plan_engine/auction_hit_recorder.py`、warroom（读 scenario_plan 输出，不直读表）。

## 2. 实证（2026-09-17 凌晨复核）

### 2.1 桥 dump 覆盖两个竞价窗口（可续命前提成立）

`E:\qmt_bridge_sim\ticks3.csv`（9/16 当日文件，745,768 行）全量实扫：开盘竞价 09:15-09:25 **18,097 行**（每分钟均有）；尾盘 14:57-15:00 **14,974 行**（15:00 撮合 8,043 行）。与台账 9/9 取证互证。桥 dump 每日 09:15 随沙箱终端启动重建——终端不开则无数据。

### 2.2 CH 存量

- `auction_snapshot`：9/9~9/15 每天约 5,220 行（每股 1 行终态，ReplacingMergeTree(symbol,trade_date) 覆盖语义）；9/16=10,440
- `auction_book`：日常约 15 万行/日；⚠ 9/15 仅 5,220 行（单轮）——当日采集链 09:25 后才起，开盘竞价几乎全丢。**运营教训：链路必须 09:15 前就位**
- `tick_depth_5`：9/16 全天 1,222 万行（data_source 全='miniqmt'，xtdata 模式）；竞价窗口 9/16=240,810 行、9/14=22,643

### 2.3 列结构对照与关键实证

- `auction_snapshot` 9 业务列 ⊂ tick_depth_5 全有，100% 可派生；`auction_book` 五档 20 列+价量额 ⊂ tick_depth_5 全有，缺口 6 列（open/high/low/pre_close/upper_limit/lower_limit）→ §9 自算
- **量纲同源零换算**：9/16 平银 tick_depth_5.stock 1,499 手/1,768,800 元 == auction_book 逐位一致
- **裸码跨市场混线**：`000001`=平安银行(stock) 与 上证指数(index) 同码，派生必须滤 `market_type IN ('stock','stock_bj')`
- **CH 别名遮蔽陷阱**：SELECT `'A_share' AS market_type` 会被代入 WHERE 改写过滤（回补 32 天全 0 行事故）——常量列禁别名
- **撮合形态**：窗口内 volume 于 09:25 从 0 跳变为撮合量，argMax(timestamp) 即终态

## 3. 方案（Owner 批：A' = "一个模块解决"）

两张表、两个任务、全部消费端、调度名、catchup_guard、资源槽、仪表盘全不动。只改两处：

1. tasks.yaml 两任务 `source: miniqmt → qmt_bridge`
2. `qmt_bridge_provider` 新增 capability `auction_data`/`auction_book`，实现 = 新模块 `ch_auction_derive` 对 tick_depth_5 的 INSERT SELECT 派生（懒导入解耦同 ch_tick_kline 模式）

## 4. 裁决点终态（施工中自裁，依据留痕）

1. 缺 6 列：open/high/low=0（miniqmt 原产语义）；pre_close=昨收 round 2 位；涨跌停=板块规则（**ST 现行同幅已删**——stk_limit 2026-09-15 全表实证：00/60 ST=0.1、30/68 ST=0.2、92=0.3）；除权除息日 840 行（0.58%）与官方值有差=盘前固有边界
2. miniqmt_provider 三个竞价方法已标 `[RETIRED-2026-09-18]`
3. 调度维持 auction_highfreq 每 10 秒（幂等）
4. 历史回补档 1 已执行（32 空窗日）；档 2（1min 首 bar 量标定）立卡后置；档 3 零成本已有
5. 尾盘竞价维持无专用表（tick_depth_5 即真源）
6. provider 历史日防覆盖闸（红队 P1#3）：_call_derive_auction 对 <end 的日期强制 day_has_auction_rows 闸

## 5. 影响面清单（下载链路零牵连）

| 对象 | 处置 |
|---|---|
| tasks.yaml 两任务 / qmt_bridge_provider | ✅ 已落地 |
| scenario_planner / auction_hit_recorder / warroom / api_server | 零改动 |
| catchup_guard / trading_calendar / data_slot_auction_highfreq | task_id 不变，零改动 |
| market_breadth_collector（miniqmt 直连） | 另案=台账档 2-D |
| miniqmt 竞价方法+测试 | RETIRED 标注 |
| **下载/回补链路** | **零牵连**（快照任务与下载族无共享代码路径） |

## 6. 施工执行记录（✅ 全部完成）

1. ✅ 能力反查留审计；claim 全程在册
2. ✅ ch_auction_derive + 20 单测（CH 全 mock；别名遮蔽/逗号/市场过滤回归测试固化）
3. ✅ tasks.yaml source 两行（红线 1：其余任务零改动）
4. ✅ miniqmt 竞价方法 RETIRED 标注
5. ✅ 登记：depgraph file 节点 ×3（14462966/14462967/14539619）、模块翻译 ×3（7045/7046/7053）、creation_token 批量
6. ✅ E2E 对拍（§7）
7. ✅ 台账 §2.2-B 勾选 + 本文档
8. ✅ 红蓝两轮（§10）

## 7. E2E 对拍终局（9/16 派生 SELECT 零写入 vs miniqmt 原产）

- **快照**：common 5,219 标的，价/量/额零失配
- **盘口**：common 144,431 键，last_price/volume/amount 零失配
- **昨收/涨跌停**：99.42% 一致；840 行失配全=除权除息日（688778 实证：9/15 收 45.48、9/16 除息 0.30→官方 45.18；stk_limit 官方值 T+1 晨间入库，竞价时段不可用）
- **回补实弹**：32 空窗日 ×约 5,200 行 ≈16.6 万行，零失败；5 日已有数据正确跳过
- 运营红旗移交：stk_limit 自 9/16 起无新行（收集器疑似停摆）

## 8. 竞价历史回补研究（Owner 问：能不能回补十年）

### 8.1 自有 tick 派生（✅ 已执行）
tick_data 88.4 亿行（2025-01 起）但竞价窗口仅 2026-06 起 40 个密集日（盘后回补通道不含盘前=结构性缺口）。实补 32 空窗日。9/15 及 7/8 月缺采日永久缺失。

### 8.2 竞价末态回补 2021-09 起（立卡后置）
1min 线 2021-09 起 14.8 亿行。竞价价=首 bar open 精确（11.82==11.82 实证）；竞价量=混合口径（2,034 vs 2,763）需 40 真值日标定。体量约 600 万行。

### 8.3 2015-2021：日线代理
kline_daily 深到 2000 年，日线 open=竞价撮合价零成本已有。**十年竞价过程数据任何渠道不存在**（官方不供），过程数据自桥时代起积累；十年回测业界惯例即 open 级代理。

## 9. 6 列缺口自算（✅ 落地终版）

这 6 列是 miniQMT 快照顺带附送的"日内统计字段"（非日线数据）。全部自算零新模块：open/high/low=0（原产语义）；pre_close=kline_daily 昨收 round 2 位（4dp 伪影必须 round）；涨跌停=昨收×板块规则（主板 10%/创业科创 20%/北交所 30%，现行 ST 同幅）。

**做T 影响**：相关但 9/18 不打断——intraday_t0 为纯函数（数据上游注入），daban 链有独立涨停价解析。

## 10. 红蓝两轮

- **第一轮**（独立红队）：报 P0"切换未接线"=stash 风暴期观测假象（施工文件被他会话 stash 卷走，已复验落地）；真 P1×1（resume 区间覆盖原产→历史日闸已加）+P2×2（None client RuntimeError、60 天回看窗）已修
- **第二轮**（复检）：确认一轮修复全部真实落地（历史日闸/None 守卫/60 天回看窗/tasks 切源/20 测试绿），新发现 P1×1（FetchResult 缺 rows_fetched→scheduler 游标冻结+每交易日 120 条 0 行告警——一行修复已入 92812a31a0）+P3×5（闸 fail-closed/迁址残留 5 处/测试缺口 3 件——全部已修，23 测试全绿）。两轮后残留：仅他车道 test_index_constituent_scd2×4 既有红（12caf83a11 之后再被改出，非本批引入）

## 11. 明晨（9/18 退役日）观察清单

- [ ] 09:15 前：大 QMT 沙箱终端已开+三策略活（Owner 已承诺；9/15 迟启教训）
- [ ] 09:15-09:25：ticks3.csv 出行+tick_depth_5 竞价窗口有数+两竞价表派生落库（桥源首日）
- [ ] 14:57-15:00：尾盘窗口有数
- [ ] TICK_SOURCE=bridge env 确认
- [ ] 做T 注入面无 miniqmt 快照字段残留
- [ ] stk_limit 收集器停摆核查（9/16 起无新行）
- [ ] QUOTE_V17/v20 合并对拍挂账项
