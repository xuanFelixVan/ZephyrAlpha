---
ttl: task_bound
title: "板块币圈族挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# L05b 车道：板块族+币圈族数据用途挖矿

> 方法论：onboarding_sop §9A 六问+§9B 12 应用面+三态出口。实勘 2026-10-01，CH c1_market 只读（zephyr_reader）；
> census=data/runtime/consumption_census_ledger.json（读数 2026-09-29：287 active/473 zero/5 retired）。黑户面（未注册）归另一执行车道，本簿只挖用途面。

## 0. 结论速览

实体 26（板块 19+币圈 7）：板块主链全接线且鲜（880 日K 9 端消费/881 独立/分钟 11M 行）；**board_index_tick 断续供给**（仅 4 日+09-30 半日截断）且消费链"注册半件"零调用方；**hl_* 4 表深史躺库零下游**（risk model 不吃）；币圈模块 Owner 2026-09-30 口谕暂停（不扩面不清算）。工单 8 条（top3=W1 hl 下游开闸挂账/W2 board_index_tick 修复+消费闭合/W3 前端去演示化挂账）。三态=板块 16 接线在岗+币圈 5 挂账（defer=口谕）+0 退役。

## 1. 族读数（CH 实证：行数+时间跨度+判定）

| 实体 (c1_market) | 行数 | 跨度 | 判定 |
|---|---|---|---|
| sector_snapshot | 121,810 | 08-14~09-30 | 鲜（880 实时快照增量，tqcenter 全量轮询） |
| kline_sector_880 | 784,462 | 2020-03-17~09-30 | 鲜；含 mkt_index 段 9 只大盘码；宇宙 728 码（09-25 扩面） |
| kline_sector | 86,063 | 2025-07-18~09-30 | 鲜；881 族独立通道（tqcenter，09-11 换道裁定，不冗余不可退役） |
| kline_sector_intraday | 11,166,427 | 07-20 13:28~09-30 15:00 | 鲜；tdx 直连任务退役留观，替代=constituents 等权合成（Windows 班 sector_eqw_intraday 15:40） |
| sector_meta | 2,700 | 08-10~09-30 | 鲜 |
| sector_list | 5,217 | 仅 09-03 | 维表快照（设计单日，非断供） |
| sector_constituent | 249,165 | 维表 | 鲜；880+881 全族 594 码宇宙真源 |
| sector_constituent_snapshot | 962,741 | snapshot_date PIT | 鲜；board_index_supply PIT 子查询在用 |
| sector_constituent_sw_history | 46,133 | in/out_date 区间型（SW2021） | **孤岛**：仅 backfill_sw_member_history 产，全仓零读 |
| sector_state | 429,901 | 2022-09-01~**09-29** | 鲜但滞后 1 日（09-30 缺=close_final 班核对项 W6） |
| sector_preference | 4 | 09-23~09-29 | 微量新产线（pre_open 4 日） |
| sector_fund_flow | 6,490 | 09-15~09-30 | 鲜（akshare THS；09-19 非交易日多余行已被 checker 记档） |
| board_index_tick | 1,533,258 | 09-15 11:15~09-30 09:35 | **断续供给**：仅 09-15/24/28/30 四日，09-16~23+09-25+09-29 全缺，09-30 半日 09:35 截断；全部 source=bridge_synth |
| concept_board(+constituent) | 750+37,040 | 维表 | 鲜；concept_factor_mapper/api/batch_preflight 在读 |
| concept_sector | 375 | 维表 | 少读（akshare 同义面+io_sector_map） |
| industry_class | 31,414 | 维表 | 接线（tushare 产；回测 3 脚本+io_sector_map 读） |
| sector_code_name_map | 1,198 | 维表（名册真源 map_version sha） | 半接线：w178 facts+880_named 视图底座；策略零直读 |
| kline_index_calc | 1,963 | EQW_ALLA 2019-01-03~09-30 | 鲜；等权单条目（基期=1000 链乘） |
| v_kline_sector_880_named | 视图 | 同 880 | 仅 write 脚本引用，零读（留观） |
| crypto_kline_daily | 18,952 | 2025-08-08~**09-29** | 滞后 1-2 日（daily_crypto 08:30 拉 T-1 UTC 班+口谕暂停，勿误判断供=W4） |
| crypto_shadow_gate | 13 | 09-11~09-29 | 鲜；全 trend 档（v0.1），无分布审计 |
| hl_funding_history | 4,733,227 | 2023-05-12~09-30 | 鲜深史（234 币逐小时，可回溯）；**零下游** |
| hl_liquidation_raw | **10** | 09-18~09-30 单币 | 有界采样试点（ws_trades_bounded；7x24 守护挂账下一班） |
| hl_oi_snapshot_daily | 2,574 | 09-18~09-30 | 鲜短史；官方无回补通道（晚一天少一天）；**零下游** |
| hl_perp_snapshot_daily | 2,574 | 09-18~09-30 | 同上（234 币全市场）；**零下游** |
| sentiment_panel | 40 | fear_greed 30 obs（09-01~）+cb_premium 10 obs（09-16~） | 鲜；F15/F25 双源，双 metric 生命周期不同步 |

## 2. 重点表六问+12 面矩阵（板块 4+币圈 5）

六问（Q1 因子/Q2 策略/Q3 模块/Q4 环节/Q5 地图/Q6 盲点）：

| 表 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 |
|---|---|---|---|---|---|---|
| kline_sector_880 | 板块动量/宽度/相对强度 | STR-SECTOR 轮动族、mainline_candidates | sector_state_pipeline/aggregator/momentum/position_sector_context/llm_premarket/api 9 端 | tasks:2377 日批+resample | TDM 板块职能+概念板块图 | 881 与 880 双口径并行无统一对账 |
| board_index_tick | 盘口宽度/等权板指微结构 | 做T 6.1 龙头跟风扩散/6.2 板块内补涨（L2 兜底位） | board_index_supply（**全仓零调用方**）、realtime 产 | ops_board_index_realtime 09:20（班漂移=断档根因） | emotion C1/C2 事件级 L4（实读 daban 非本表） | 断档无停更告警；供给 policy 与实际 source=bridge_synth 语义未对齐 |
| kline_index_calc | 等权超额（vs 上证） | regime 微观相位（auto_mount） | regime_feature_builder（399106 断更补位:584）、walkforward | tasks:3229 日批 | 大盘广度地图 | 等权扩面（板块/域等权）未立项 |
| sector_constituent_sw_history(+code_name_map) | 成分漂移因子（SW 版本区间） | PIT 回测成分归属（防前视） | **sw_history 零读**；name_map=w178 facts+880_named 视图 | 无班（人工 backfill） | SW 产业链图原料 | 两孤岛用途未书面化；name_map 无策略直读 |
| crypto_kline_daily | F14 BTC 动量（alt_regime_signals:261）、MOM/VOL 因子岛（在册零算） | 跨资产 regime、universe eligible 池 | crypto_provider+shadow_gate 读表直判 | daily_crypto 08:30 班 | 95 号蓝图币圈段 | 09-29 止缺口未核对；口谕暂停与调度并存语义模糊 |
| sentiment_panel | F15 极值反转/F25 转债溢价 | F15/F25 regime、C4 双窗联动 | sentiment_panel_provider、alt_source_bootstrap | tasks:2764/2776 daily_event | 币圈+转债情绪地图 | 双 metric 起始日错位（09-01 vs 09-16）无对齐声明 |
| hl_funding_history | 费率因子/套息成本 | **risk/core/leverage_risk_model 的 funding_rate=纯函数入参，不读本表** | hyperliquid_provider 仅产 | daily_crypto 班 | D5 波2 跨资产图 | 4.7M 行深史零消费=census 盲区（473 岛无 hl residual 条目） |
| hl_oi+hl_perp_snapshot | OI 变化率/多空杠杆结构 | cryptomarket 前端（目标源，现为演示数据） | 仅产 | daily_crypto 班 | 同上 | 短史不可回补+零下游双压 |
| hl_liquidation_raw | 清算不对称/瀑布因子 | 无 | 仅产 | 同上 | 同上 | 10 行采样不足以撑因子；7x24 守护挂账 |

12 面（●=适用+工单；○=不适用）：面序=大盘/板块/个股/做T/转债/ETF/期货/币圈/宏观/产业/事件/文本

| 表 | 大盘 | 板块 | 个股 | 做T | 转债 | ETF | 期货 | 币圈 | 宏观 | 产业 | 事件 | 文本 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kline_sector_880 | ●mkt_index 段 | ●9 端 | ○经成分间接 | ○日K | ○ | ○ETF 联动候选 | ○ | ○ | ●regime 输入 | ○ | ○ | ○ |
| board_index_tick | ○ | ●C1/C2 事件级 | ○ | ●6.1/6.2 兜底 | ○ | ○ | ○ | ○ | ○ | ○ | ●触板事件 | ○ |
| kline_index_calc | ●EQW_ALLA 相位 | ○ | ○ | ○ | ○ | ●等权扩面候选 | ○ | ○ | ●广度 regime | ○ | ○ | ○ |
| sw_history+name_map | ○ | ●PIT 成分 | ●归属防前视 | ○ | ○ | ○ | ○ | ○ | ○ | ●SW 图原料 | ○ | ○ |
| crypto_kline_daily | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ●F14+池 | ●跨资产 | ○ | ○ | ○ |
| sentiment_panel | ○ | ○ | ○ | ○ | ●F25 溢价 | ○ | ○ | ●FNG F15 | ●F15/F25 regime | ○ | ○ | ○ |
| hl_funding_history | ○ | ○ | ○ | ○ | ○ | ○ | ●套息成本 | ●费率因子 | ○ | ○ | ○ | ○ |
| hl_oi+perp_snapshot | ○ | ○ | ○ | ○ | ○ | ○ | ●杠杆结构 | ●前端目标源 | ○ | ○ | ○ | ○ |
| hl_liquidation_raw | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ●清算情绪 | ○ | ○ | ●爆仓事件 | ○ |

## 3. 族级粗矩阵

| 族 | 已接线（实证消费端） | 零消费/断供 | 断供/风险 |
|---|---|---|---|
| 板块K线族（880/881/intraday/snapshot） | 880 9 端+intraday 2 端+snapshot 3 端 | — | 881 双口径无对账；intraday tdx 班已退役靠 Windows 班 |
| 板块状态族（state/preference/fund_flow） | state→condition_package+daily_gate_snapshot+pipeline 闭环 | preference 4 行微产 | state 滞后 1 日（W6） |
| 板块维表族（meta/list/constituent×2/name_map/industry_class/concept×3） | 全部 ≥1 端 | sw_history 零读；v_named 零读 | sw_history 用途未书面化（W7） |
| 等权指数（kline_index_calc） | 3 端 | 扩面未开 | 单条目单点故障（internal 计算无副源） |
| 板指 tick（board_index_tick） | supply 模块在（零调用） | **4/12 交易日断档** | 无停更告警（W2） |
| 币圈影子（kline/shadow/sentiment） | F14/F15/F25+shadow 判定链 | MOM/VOL 因子岛在册零算 | 09-29 止缺口（W4）；口谕暂停 |
| Hyperliquid（hl×4） | 0 | **全族零下游** | 短史不可回补+liq 采样不足（W1 挂账） |

## 4. 接线工单（8 条，价值降序；币圈项 defer_reason=Owner 2026-09-30 口谕"不扩面不清算"）

| # | 工单 | 目标消费端 | 三态 |
|---|---|---|---|
| W1 | hl_* 下游开闸：FCT-CRYPTO-MOM-001/002+VOL-001 三岛因子实算+leverage_risk_model funding 入参接 hl_funding_history | 因子册+risk | **挂账**（口谕；90 天门自 10-01 计龄） |
| W2 | board_index_tick 断档修复（补 09-16~29+09-30 半日；ops_board_index_realtime 09:20 班漂移核查）+board_index_supply 正式接线（做T 6.1/6.2 L2 兜底+C1/C2 事件级改供本表） | strategy_pipeline 做T+emotion | **接线**（供给修复先行） |
| W3 | cryptomarket 前端去演示化：cm-engine CRYPTO_D 硬编码→hl_perp_snapshot_daily+sentiment_panel API 化 | frontend | 挂账（口谕随 W1） |
| W4 | crypto_kline_daily 09-30 缺日核查（daily_crypto 08:30 班 vs 口谕暂停，勿误判断供） | F14 源 | 接线（核查项） |
| W5 | kline_index_calc 扩面候选（板块等权/域等权第二条）立项登记 | regime/因子 | 挂账（待需求） |
| W6 | sector_state 09-30 缺日核对（close_final 班） | daily_gate_snapshot | 接线（核查项） |
| W7 | sw_history PIT 成分接回测（跨期成分漂移去前视，SW2021 区间已备） | 回测引擎 | 挂账（90 天门） |
| W8 | sector_code_name_map 策略直读暂缓声明（named 视图+facts 已覆盖） | — | 挂账（低危） |

## 5. 六向台账

- Q1 因子：候选 7（MOM×2/VOL×1 在册零算+费率/OI 变化率/清算不对称/板指宽度），落地 0。
- Q2 策略：做T 6.1/6.2（供链半通）、F14/F15/F25 regime（通）、cryptomarket 展示（演示态）、STR-SECTOR-001+census 岛 FCT-CRYPTO×3。
- Q3 模块：880→9 端；等权→3 端；intraday→2 端；sentiment→2 端；hl→0 端（grep 全仓实证：仅 hyperliquid_provider+DDL）。
- Q4 环节：daily_crypto 08:30/daily_event/ops_board_index_realtime 09:20/sector_eqw_intraday 15:40/sector_state close_final+pre_open 双班。
- Q5 地图：TDM 跨资产职能（D5 波2）/95 号蓝图币圈段/概念板块图（750 板在位，wo006 node_binding 候选在用）。
- Q6 盲点：①hl_* 无 census residual 条目（普查盲区本体）；②board_index_tick 断档无停更告警；③shadow_gate 13 日全 trend 无分布审计；④881/880 双口径无对账面。

## 6. 自审闸三态

- **接线（在岗，16）**：sector_snapshot/kline_sector_880/kline_sector/kline_sector_intraday/sector_meta/sector_list(维表设计)/sector_constituent(+snapshot)/concept_board(+constituent)/concept_sector/industry_class/sector_fund_flow/sector_state(+preference)/kline_index_calc。
- **接线（币圈影子，3）**：crypto_kline_daily(W4 核查)/crypto_shadow_gate/sentiment_panel——F14/F15/F25 消费实证可查。
- **挂账（8，defer_reason 必填）**：hl_funding_history/hl_oi_snapshot_daily/hl_perp_snapshot_daily/hl_liquidation_raw（defer=Owner 09-30 口谕+liq 待 7x24 守护班）、cryptomarket 前端（随 W1）、sw_history（defer=回测需求未立项）、EQW 扩面（defer=待需求）、name_map 直读（defer=视图已覆盖）。
- **判退役候选（0）**：v_kline_sector_880_named 零读但系 name_map 兼容出口（留观非退役）；tdx intraday 任务退役留观归接线车道管辖。
- 六问逐问跑过留痕（§2/§5）；12 面两态均留痕（§2 下表）；查无也是结论（hl 零消费、sw_history 零读均实证记档）。
