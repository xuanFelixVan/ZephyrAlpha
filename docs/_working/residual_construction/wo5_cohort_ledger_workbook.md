---
ttl: task_bound
title: WO-5 投资者行为日账本挖干作业簿 v1——五人群结算层/forecast 通电/盘中判定与 twin 校准
owner: ZephyrAlpha-Owner
session: st-residual-20260917
date: 2026-09-17
status: mining_b1
---

# WO-5 投资者行为日账本 · 挖干作业簿

> **真源**：[pending_items_plan.md](pending_items_plan.md) WORK-ORDER-5（粒度设计/三期路线/数据依赖分工在主单，本作业簿管实现层实底与 schema 裁定）。B1 批全部落点带实底，接单会话免再勘察。

## 0. 挖矿日志（批次 B2）

- 母节点：cohort_daily_ledger（行=五人群，列=每日净行为量化；结算/判定分层）。
- B2 内部动作=两个并行深度勘察：资金面数据族 9 问 + 行为侧消费端 8 问。
- 外网动作：本批未出网（长尾 M-6 记档：cohort 代理偏差的学术修正法，需引文）。

## 1. 重大对账修正（转达数据线）

**A19"四类资金没有"需修正为：原料已在库在跑，缺的是聚合视图与账本。** `c1_market.money_flow`（任务 `money_flow_incremental` tasks.yaml:170 + 全量刷新 :1107，主源 tushare pro.moneyflow 2026-08-14 切换、akshare 降 fallback）个股粒度、**完整单量分类字段**（main/super_large/large/medium/small_net_inflow 及占比，DDL 真源 `schemas/categories/intraday/market_money_flow.py:47-84`），2026-06-01 起 45.0 万行/5,574 标的。大盘级=个股聚合。**一期零新数据依赖。**

## 2. 六向台账

### ①上游（五人群的原料实底）

| 人群 | 原料表 | 状态 | 起始 | 已知偏差 |
|---|---|---|---|---|
| 散户 | `money_flow.small_net_inflow`（聚合）+ `alt_stock_comment.attention_index`（注意力） | ✅在跑 | 2026-06-01 / 09-11 | 机构算法拆单藏进小单（系统性低估机构、高估散户） |
| 杠杆资金 | `margin_trading`（融资买入额/余额/偿还额） | ✅在跑 | 2026-07-20 | 追涨属性强，极端日失真 |
| 游资 | `dragon_tiger`+`dragon_tiger_seat`（seat_name 营业部名）+ daban 链（连板高度/涨停数/炸板率） | ✅在跑 | 席位 2022 起 | 龙虎榜只覆盖异动股；**G5 词表坑见下** |
| 机构配置盘 | `block_trade`/`block_trade_detail`（折价率自算=price JOIN kline_daily close） | ✅在跑 | 2026-08 起 | 大宗是机构**存量调仓**代理，非全部机构行为；ETF 份额缺位（G4） |
| 产业资本 | 增减持/回购公告表 | ❌未盘点 | — | 一期留行位不填，挂长尾 M-8 |

- 北向：日频已死（`hk_connect_flow` 止 2024-08-16，任务 disabled 留痕），季度 `northbound_hold_snapshot` 在跑——机构行一期不用它。
- 千股千评：`alt_stock_comment`（org_participation/composite_score/main_cost/attention_index）2026-09-11 起，**无历史回补通道**（接口只回当日快照）——注意力代理从零积累，如实接受。

### ②下游（账本喂给谁）

- **二期主消费方已通电**（重大利好）：forecast 台账三表写方真实在跑——`judgment_ledger`（MOD-PLAN-026 发射器）+ `intraday_l1_tracker`（60min bar 唤醒）+ `next_day_forecaster`（daily_kline 唤醒）+ `judgment_settler`（三表同锚结算），接线在 `pipeline_events:747-786/:835-851`。"概率没通电"实义=**next_day_forecast 的 v0 判定只用 kline_index+breadth 的 3×3 条件桶，cohort 特征尚未成为输入**——通电=给 forecaster 加特征集，不是造发射链。
- 已知结算缺口（顺带登记）：`realized_tail_return` 恒 NULL（需 14:30 分钟源，Phase 2）；指数分钟用 510300 代理；limit_up_pool 空时用全市场涨停数代理（`intraday_l1_tracker` 头注自曝）。
- `daily_plan` 表无自动发射者（场景引擎 MOD-PLAN-018 未接）——不在本批。
- 三期消费方：`market_twin_simulator` **全注入式 BDI**（三函数闭包+邻接表+contagion_weight），**无校准接口**（BDIRuleBook 零调用方，输出内存对象不落表）——三期先建校准入口再喂参数。

### ③算法/机制

- 聚合先例：`alt_regime_signal` 长表（signal_id/signal_date/signal_value/state/detail JSON/source，ORDER BY (signal_id, signal_date)）——**账本表结构直接抄此先例**（裁定 S1）。
- 轮动状态空间（二期）：`kline_sector_880`（tqcenter 日线）× `sector_constituent`（成分）× `sector_fund_flow`（五时点快照差分=区间净流入，重钥桥 `sector_code_bridge` THS 881↔880 已 100% 实证）。注意 sector_fund_flow 走 Windows 计划任务不在 tasks.yaml（`register_counter_trend_feeder_tasks.ps1`）。
- 外网未出网：长尾 **M-6**（散户代理偏差修正的学术方法）。

### ④后端

- 缺：①`cohort_ledger_builder`（聚合金，建议 `src/zephyr/alt_data/cohort_daily_ledger.py`，仿 `alt_regime_signals.py` 结构）②长表 DDL（库归属裁定 S2：**c1_backtest**——多表加工派生层，按 data_ops SOP 库前缀路由惯例）③调度任务 `cohort_ledger_daily`（schedule=daily_capital 尾部，deps=[money_flow_incremental, margin_trading_incremental, dragon_tiger_incremental, block_trade_incremental]）。
- 二期：`next_day_forecaster` 特征集扩展 + 游资轮动转移矩阵件。
- 三期：twin 校准接口（新件）+ 盘中判定层。

### ⑤前端（只登记）

- 账本日行卡片挂 dashboard（dashboard_feeds 同路）；作战室日刊可引 cohort 摘要。登记不施工。

### ⑥数据字段

- 全部上游字段已核对（见 ①表）。**G4 ETF 份额：全仓无表无任务**（唯一机构日频干净代理）——数据线立项候选。
- **G5 seat_type 词表坑**：`dragon_tiger_seat.seat_type` 词表仅 institution/broker/connect（DDL :52），而 `event_dragon_tiger` 期望 quant_inst——游资身份识别靠 `seat_registry.yaml`（17 席位档案已有）+ `seat_pattern_analyzer`/`lhb_premium_analyzer`（design/testing，均无下游）。账本一期游资行用"席位聚合活跃度"不依赖身份分类，G5 留给数据线 A7。
- **G6 晋级率/炸板率无独立日频列**：只活在 `alt_regime_signal` detail JSON 与 `market_breadth_snapshot`（attempted/sealed 盘中分子分母）——账本聚合时自算（daban_board_event 推进或 breadth 快照收盘定格），不另立任务。

## 3. Schema 裁定

- **S1 长表**：`c1_backtest.cohort_daily_ledger`，列=trade_date / cohort_id（retail/leverage/hot_money/inst_config/industry）/ metric_id（如 net_inflow_sum / net_inflow_median / activity_count / discount_rate_avg / attention_median）/ metric_value Decimal(18,4) / state(净正|净负|中性) / proxy_source（哪个代理算的）/ bias_note（已知偏差短注）/ detail JSON / ingest_ts。RMT 只增不改，ORDER BY (cohort_id, metric_id, trade_date)。理由：加人群/指标免 ALTER；proxy 标注是回测纪律的落点；抄 alt_regime_signal 成熟先例。
- **S2 分层对齐**：一期只做**结算层**（盘后日频，回测唯一真源）；判定层（盘中分钟估计，estimated=True）三期；小时级只是查询窗口（主单已定）。
- **S3 状态语义分期**：一期 state 只有净正/净负/中性（纯规则可回测）；进攻/防守/抱团/轮动/退潮语义态二期接轮动模型后再落，禁一期拍脑袋语义。
- **S4 口径**：全部金额单位=万元（money_flow 原生口径），表 detail JSON 记单位；聚合口径=全市场等权求和+截面中位数双值（防极值股劫持）。

## 4. 一期验收（含老蔡对账）

1. `cohort_daily_ledger` 表建成（DDL 走 schemas 真源+apply 脚本），任务在跑、marker 留痕。
2. **老蔡样本对账（2026-09-16/17 盘面）**：散户行 small_net_inflow 全市场聚合，能复算"昨日小资金流入 ~75 亿 / 今日流出 ~83 亿"的**方向与量级**（口径差允许：tushare 万元 vs 东财亿元、小单定义差异——对账报告写明口径映射）。
3. 游资行能复算"电力→玻璃基板→农业"轮动的当日足迹（dragon_tiger net_buy 板块分布 top3 + daban 连板高度）。
4. 回放 2026-06-01 以来全历史，行数=天数×人群×指标无缺口（缺源日期如实标 proxy_source=missing）。

## 5. 施工顺序

1. **一期结算层**（1-2 会话）：DDL+builder+任务+老蔡对账报告。依赖：零（全部原料在库）。
2. **二期通电**（1 会话）：forecaster 特征集加 cohort 特征 + 游资轮动转移矩阵 v0（880 板块×资金差分状态空间）。前置：一期跑满 ≥20 交易日。
3. **三期判定层+twin**（1-2 会话）：盘中分钟估计层 + twin 校准接口（BDI 闭包参数注入件）。前置：二期 forecast 台账攒够可校准样本。

## 6. 长尾矿脉（未挖续挖）

- **M-6**：散户代理偏差修正学术法（外网引文）。
- **M-7**：ETF 份额数据源（数据线候选，机构行升级）。
- **M-8**：产业资本行（增减持/回购公告表盘点）。
- **M-9**：chip 筹码分布落表（现 trial 不落表零消费；获利盘结构可作二期特征）。
- **M-10**：seat_type 词表扩展/席位分类器（数据线 A7 范围）。

## 7. 挖后自审闸

- **北极星**：把"读博主复盘了解今日市场"变成机器日落一行的自动账本，消灭 Owner 读叙事的人工环节；且二期顺手治 forecast"概率没通电"。
- **过度工程三问**：①收益实算=行为序列是 regime/执行层之外第三个决策输入面，且是全市场截面（超越任何单博主）；②已有产物覆盖=否——原料全在但聚合账本不存在，alt_regime_signal 是信号族不是人群账；③成本实算=一期 1-2 会话、零新数据依赖（对账修正后成本较主单预估下降）。
- **裁定：施工**（一期先行；真实判定层/校准接口按 §5 前置解锁）。
- **红蓝预登记**：单量分类的机构拆单偏差可能让散户行系统性失真——缓解=每行 proxy_source+bias_note 强制标注、股东户数到位后交叉校准、月度 IC 考试不过的行自动降级"仅描述不进决策"（主单回测纪律）。
