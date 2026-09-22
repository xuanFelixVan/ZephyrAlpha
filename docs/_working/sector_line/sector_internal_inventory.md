---
ttl: task_bound
title: 板块线内部盘点册——仓内板块资产四态取证
created: 2026-09-22
sid: st-secmine-20260922
lane: sector_line
status: draft（只读取证，未动任何仓资产）
doc_version: v0.2（§12 挖干补遗+两处改判）
evidence_note: 全部行数/时戳为 2026-09-22 当日经 DatabaseService reader 连接实测；代码状态以文件头 15 字段+CONSUMERS 注记为证
---

# 内部盘点册②——仓内板块资产逐项四态

> 四态口径：**A=通**（可用现役，数据当日新鲜/模块 production）｜**B=半通**（可用但有已知缺口/接线不全）｜
> **C=断**（断供/停更，有缺口窗）｜**D=缺**（在册无实物或空表，需新建）。
> 判读铁律：卡在册≠没断供、空表≠没建（逐项实测留证）。

## §0 一句话总结

板块层**不是空地**：数据采集面（880 板块日K 六年深史+实时快照+成分股+概念板块+申万分类）
基本 A 态，信号模块面 16 件全落码，设计祖先（22 号 spec v1.9.8）公式级齐备——**真正缺的是
"接线与聚合"**：16 个信号模块 CONSUMERS 以"待 G05"为主，L2 门三原料无着落，sector_state /
sector_preference 两张输出表不存在，能力反查面零在编。这与 Owner-Max 定桩"板块层=全链条
最薄段"精确互证：**薄在集成，不薄在原料**。

## §1 板块行情/指数数据表（D1）

| 表 | 覆盖实测（2026-09-22） | 态 | 证据/备注 |
|---|---|---|---|
| c1_market.kline_sector_880 | 2020-03-17→**2026-09-22**，469 码×1 周期，44.3 万行 | **A** | 880/881 板块日K，**六年深史且当日新鲜**；q3/q5/q20 与 RRG 的真源数据（22 号 spec §3.1④⑧）；唯一采集源=tqcenter（mootdx ext 接口失效，data_sources_registry 实测注记 2026-07-22） |
| c1_market.kline_sector | 2025-07-18→2026-09-22，596 码日K，7.9 万行 | **A** | 另一口径板块日K（与 880 关系待辨析——两套板块码本 469 vs 596，§5 建议单列辨析项） |
| c1_market.kline_sector_intraday | 2026-07-20→**09-15**，727 码×5 周期，973 万行 | **C** | 盘中板块K停 09-15，缺口 7 个交易日；资源册有 manual_sector880_backfill 手动回补任务位 |
| c1_market.sector_snapshot | 2026-08-14→**09-22 15:55**，596 码，11.2 万行 | **A** | 实时截面（up_home/down_home/内外盘/涨速 18 字段），非多日序列；快照管实时、K线管序列（22 号 spec §2.5 分工） |
| c1_market.board_index_1m | **0 行** | **D** | 空表（自算板块分钟指数未产出） |
| c1_market.board_index_tick | 单日 2026-09-15，465 码 | **C** | 试点单日即停 |
| c1_market.concept_board / concept_board_constituent | 375 概念→4829 股，**09-22 新鲜** | **A** | 概念维度齐备（valid_from/valid_to 版本化） |
| c1_market.concept_sector | 单日 2026-09-02，375 码 | **B** | 静态单日清单，非滚动 |
| c1_market.sector_list | 单日 2026-09-03，5217 行 | **B** | 单日快照 |
| c1_market.sector_meta | 90 个同花顺行业，**09-22 新鲜** | **A** | 板块元数据（成分数/流通市值） |

## §2 分类表（D1 续）

| 表 | 覆盖实测 | 态 | 证据/备注 |
|---|---|---|---|
| c1_market.industry_class | 10472 股×申万 L1-L3（499 行业名），09-20 | **A**（带已知坑） | 已知符号格式混用（5534 裸码+4938 带后缀并存）、1 行 industry_sw='nan' 坏行、新旧批冲突 1 例——09-16 复诊结论=Executor 按 valid_from 最新者胜已防御（position_recipe_grid_schema.yaml 实证注记） |
| c3_fundamental.industry_class_suppl | 10141 股，09-22 | **A** | 补充行业分类 |

## §3 行业 ETF（D2）

| 表 | 覆盖实测 | 态 | 证据/备注 |
|---|---|---|---|
| c1_market.etf_list | 2184 只（5 类型），09-10 | **A** | 含指数跟踪关系（index_code/index_name） |
| c1_market.etf_nav | 2021-07-29→09-21，1694 码 | **A** | |
| c1_market.kline_etf_daily | 2021-03-08→**09-22**，1675 码，9.9 万行 | **A** | 五年日K |
| kline_etf_1min/5min/15min/30min/60min | 1min 2.9 亿行等五族 | **A** | 分钟面齐全 |

**勿重考红线**：行业 ETF T0 三宇宙实证（行业ETF 6 绿）已由 st-bizmine 落地——真源
`docs/_working/archive/2026-09/bizmine_night/etf_t0_retest/etft0_screen_results.csv`
（+bizmine_campaign_ledger.md）。
本线**只引用不复考**；若板块偏好落地需要 ETF 载体，直接消费该已考资产。

## §4 L2 板块门现状（D3）——实证当前状态

- **桥接在位**：`src/zephyr/strategy_pipeline/daily_gate_snapshot.py` `_collect_l2`——复用 L1
  regime 快照 dominant → 查 `_DOMINANT_TO_WATER_TEMP` 七键映射（r1/r2→NEUTRAL、r3/r12→
  RISK_ON、r4→RISK_OFF、r10→CRASH、r11→PANIC_REPAIR）→ `sector_gate.water_temp_response()`
  查表响应面（方案甲，Owner 已批，真源 docs/_working/daily_loop_campaign/wiring_proposals_L2_sector_gate.md）。
- **三原料无着落（核心缺口）**：admission_gate 需要 top/retained_sectors/score 三原料，代码如实标
  `gate_level="not_evaluated"`——**板块门从未真正评过**，只有水温响应面在空转。
- **阈值 proposed**：`threshold_provenance="v2.1_proposed_pending_G05"`——v2.1 阈值未经 G05
  回测校准（与 22 号 spec §3.1⑩ v2.1 同源）。
- 判定：**B 半通**（桥接零新读设计成立；门的"评"功能因原料缺位而恒 absent/not_evaluated）。
- 依赖事实：dominant 观测值域实测=regime_snapshot_history 中 **{r1,r2,r3,r4,r10,r11,r12} 恰好
  7 键全覆盖**（r5~r9 从未出现），映射表对观测域零缺口；anchored 表当前只产 r1~r4 四档。

## §5 资金线板块维度（D4）

| 表/件 | 覆盖实测 | 态 | 证据/备注 |
|---|---|---|---|
| c1_market.sector_fund_flow | 90 行业，**仅 2026-09-15→09-22（6 天）** | **C**（短史） | 行业资金流今日仍在产但历史极浅；HHI/净流入集中度等历史分位计算受限 |
| c1_market.money_flow | 个股五层净流入，2026-06-01→09-22，5579 股 | **A** | 板块级净流入正确路径=money_flow×sector_constituent 聚合（22 号 spec §3.1⑥ 裁定，勿另建采集管道） |
| c1_market.market_fund_flow_daily | 120 行，2026-03-27→**09-17** | **C** | 大盘资金流停更 5 天 |

## §6 涨停扩散/情绪原料（D5 交叉轴）

| 表 | 覆盖实测 | 态 |
|---|---|---|
| c1_market.limit_up_pool | 2026-09-01→**09-22**（含 industry 列） | **A** |
| c1_market.limit_up_down | 2026-07-20→**09-22** | **A** |
| c1_market.daban_board_event | 2026-09-01→**09-15** | **C**（断 7 天，与情绪班同款断点，两班共用该修复依赖） |
| c1_market.sentiment_panel | 仅 2 指标 25 行 | **B**（fear_greed 为币圈异轴，禁顶替 A 股情绪——t0 判例红线，情绪班已重申） |

## §7 板块→个股选择现有件（D6）——16 模块+接线实证

`src/zephyr/signal_ashare/sector/` 16 件全落码：sector_analyzer（六方法
evaluate_strength/judge_continuity/warn_rotation/evaluate_launch_conditions/adapt_market_style/
detect_breakdown）、sector_momentum（q3/q5/q20 多TF 0.4/0.3/0.3）、sector_momentum_persistence、
sector_rrg（JdK DualEma 10/26 四象限+zscore）、sector_rotation_state、sector_breadth（资金性质
板块级聚合+capital_nature_multiplier）、sector_divergence（电风扇速度计+5 状态+CONSENSUS_CLIMAX）、
sector_siphon（HHI 虹吸）、sector_leader（龙头/中军/跟风）、sector_pullback（回踩 A/B/C）、
sector_crowding_launch、sector_volume_anomaly、sector_gate（水温响应面）、sector_adjustment、
sector_attribute_rules、sector_detail_enricher。

**接线实证（谁真的在消费）**：
| 消费方 | 消费什么 | 证据 |
|---|---|---|
| src/zephyr/pf_alloc/batched_position_builder.py | 回踩 A/B/C 消费侧 | 文件在位（22 号 spec 回填⑤已接线） |
| src/zephyr/plan_engine/boundary_revision_engine.py | sector_divergence 电风扇>75 分位降档 + TRIGGER_SECTOR_TOP_RISK | import 实证（L92/L139/L338） |
| src/zephyr/signal_fundamental/sector_rotation_score_mapping.py | 板块→个股 score 映射 | 文件在位 |
| data/sector_report_builder.py（production） | sector_limit_up_ratio 涨停比归一化 | 文件头 MATURITY=production |
| data/sector_factor_manager.py | 板块因子管理 | 文件头 MATURITY=**testing** |

**总判定：B 半通**——件齐、三处真实接线、但 16 模块 CONSUMERS 注记 majority="待 G05 选股
引擎"，板块强度→选股漏斗的系统性消费未成网。

## §8 大盘状态输入（D7）

| 表 | 覆盖实测 | 态 |
|---|---|---|
| c1_backtest.regime_state_anchored | 2026-09-22 当日新鲜（dominant=r1~r4 档+vol_pct+MA20/60/120），4473 行 | **A** |
| c1_backtest.regime_snapshot_history | 3627 行（r1~r12 全值域真源） | **A** |
| c1_market.index_quote | 614 码，07-14→09-22 | **A** |

## §9 情绪输入与设计祖先（D8）

- **emotion_index**：情绪班（st-emomine-20260922）在飞，契约 v0.1 已定（六成分等权、stage 四态、
  version 语义化），落库 DDL 草案已出（c1_market.emotion_index），**成品未出**——本线开发期按
  契约形态 mock，集成夜换真值（总包 §2 约定）。态=**D 缺（在途）**。
- **设计祖先**：`docs/_working/archive/2026-09/design_memos/22_sector_rotation_spec.md` v1.9.8——
  11 项公式级裁定（RRG DualEma 10/26、q3/q5/q20、5 状态规则、三级门槛 v2.1 0.60/0.80、水温
  5 档响应、虹吸 HHI、回踩 A/B/C、龙头传导）+ 40 条外部引源 + §2.5 已施工设施盘点。骨架稿③
  以其为算法真源，不重复发明。

## §10 能力反查面（D9）——注册盲区

capability_lookup.find 实测（2026-09-22，session=st-secmine-20260922，审计已留痕）：
`sector 板块` / `行业轮动 industry rotation` / `板块轮动 sector rotation` / `emotion_index 情绪指数` /
`ETF` / `轮动 rotation` / `行业 industry` **全部返回空**；对照组 `回测 backtest` 正常命中
（backtest_engine_core 全字段返回）。

**结论**：§7 的 16 个板块模块+§1 的板块数据面在能力反查面**零在编**——后来者反查"板块"将
得到"该关键词资产不存在"的错误答案，重蹈"编排器惨案"（三 AI 不知已建成而重复施工）。
**修复建议**：16 模块的 capability 注册别名补 sector/板块/轮动关键词（归 ulib/图书馆班写域，
本线只登记不施工，见缺口清单⑤）。

## §11 四态总账

| 维度 | A 通 | B 半通 | C 断 | D 缺 |
|---|---|---|---|---|
| 板块行情/指数（§1 明细行计） | 5 | 2 | 2 | 1 |
| 分类 | 2 | 0 | 0 | 0 |
| 行业 ETF | 4 | 0 | 0 | 0 |
| L2 门 | — | 1 | — | — |
| 资金线 | 1 | 0 | 2 | — |
| 涨停/情绪原料 | 2 | 1 | 1 | — |
| 板块→个股件 | — | 1（16 模块整体） | — | — |
| 大盘状态 | 3 | 0 | 0 | 0 |
| 情绪输入/骨架 | — | — | — | 1（在途） |

**断供清单（若板块层开建须先修）**：kline_sector_intraday（09-15 起）、daban_board_event
（09-15 起）、market_fund_flow_daily（09-17 起）、sector_fund_flow 深史（仅 6 天）。

## §12 挖干补遗（Owner 追问"挖干了吗"触发的第二轮反向扫描，2026-09-22 晚）

> 首轮盘点按总包 §0② 六维清单正向筛表（正则族）；本轮反向全量过目 233 张表+调度面+
> 策略/前端消费面+架构文档面，补齐首轮四个未干角落。**全部为新增，不改前文判定（除两处改判见末尾）**。

### 12.1 反向扫出的板块聚合原料表（首轮正则族漏网）

| 表 | 覆盖实测（09-22） | 态 | 板块层用途 |
|---|---|---|---|
| c1_market.dragon_tiger / dragon_tiger_seat | 08-07→**09-22** / 2022-01→09-21（618k 行 4.5 年深史） | **A** | 龙虎榜游资席位→板块 hot money 维度（seat 深史可回溯） |
| c1_market.margin_trading | 2026-07-20→**09-18**（滞后 1-2 日，与情绪班 C5 同款 as-of 处理） | **A** | 两融余额→板块杠杆资金分布（个股级可经成分聚合上溯） |
| c1_market.northbound_hold_snapshot | 2024-09-30→**2026-06-30**（季度快照，停 3 个月） | **C** | 北向持股→机构板块偏好；停更疑似北向披露规则调整（外部方法论册 #16 同源风险），修复归数据线 |
| c1_market.daily_valuation | 08-03→**09-21** | **A** | 个股估值→板块估值分位（防御/进攻风格判别原料） |
| c3_fundamental.analyst_forecast | 104k 行（日期列非 trade_date，画像未展开） | **B** | 分析师预期→景气度标尺原料（国盛三标尺之景气维，外部方法论册 #9/#10） |
| c3_fundamental.shareholder_count / top10_shareholders | 514k / 1.5M 行 | **A** | 股东/筹码集中度→板块筹码维（远期） |
| c1_market.stock_daily_basic | 7.1M 行 | **A** | 换手率/量→板块换手聚合（拥挤度标尺原料） |

**补遗结论**：三标尺（动量/景气/拥挤度）的**景气与拥挤度两维原料在库**——板块强弱量化
若要升三标尺全家桶，原料不缺（此前盘点只覆盖动量维原料）。

### 12.2 调度面实证（产奶量=调度健康的直接证据，近 3 日）

| 表 | 09-19 | 09-20 | 09-21 | 09-22 | 判定 |
|---|---|---|---|---|---|
| kline_sector_880 | — | — | 468 | 468 | **在产满量** |
| kline_sector | — | — | 594 | 594 | **在产满量** |
| sector_snapshot | — | — | 4680 | 2808（盘中递增） | **在产** |
| sector_fund_flow | 450 | 360 | 356 | 448 | **在产** |
| kline_sector_intraday | 0 | 0 | 0 | 0 | **死产 7 天** |

调度真源定位=`src/zephyr/data/config/tasks.yaml`（非 config/ 根）。板块相关任务全在册：
kline_sector_incremental(947)、concept_sector_refresh(1033)、realtime_snapshot_incremental(1044)、
daban_board_event_derive(1658)、sector_list_refresh(1796)、kline_sector_1min_incremental(2431，
mootdx TCP 直连+include_industry_boards 132 条行业板)。
**"在册未产"两件**：kline_sector_1min_incremental（在册在调但近 3 日零产——mootdx 通道
或调度车道问题，根因归数据线/排期班）、daban_board_event_derive（同款，09-15 起停）。

### 12.3 策略/前端消费面（首轮未扫）

- **策略层零直连**：src/zephyr/strategies/ 无 sector 消费（板块→策略的既有通道仍只有
  §7 三处接线：pf_alloc/plan_engine/score_mapping）。
- **前端有板块面**：dashboard api_server 表字典含 kline_sector/kline_sector_880/concept_board
  等中文名映射（L1437-1455），个股页有行业/板块标签（stock_basic）。展示层消费=已有，
  板块分析面板=D-05 候选（sector_leader CONSUMERS 注记）。

### 12.4 架构文档面

11_d_data_eng.md（数据域文档覆盖板块采集器）、62_d_plan.md、asset_catalog.md 等含"板块"
章节——均已被 22 号 spec §2.5/§8.3/附录（63 号审计批次 C 消费登记）消化引用，本轮不再
重复挖掘；battle_map_05 的 BM-SEL-08/09 环节定义以 spec §8.2 映射为准。**架构文档面判定：
已挖干（通过 22 号 spec 这个枢纽全覆盖）**。

### 12.5 两处改判（证据升级）

1. **sector_fund_flow：C 断（短史）→ B 半通（在产+短史）**——产奶量实证每日 350-450 行
   在产，历史浅是"采集 09-15 才开"而非断供；缺口性质从"修复"改为"等史生长+money_flow
   聚合回溯双轨"（缺口清单 G7 已同步）。
2. **kline_sector_intraday/daban 断供根因面收窄**：任务在册在调但零产=非调度缺登记，
   是通道/执行层故障——修复面从"补任务"收窄为"查 mootdx 通道与 derive 依赖链"（G2/G3 已同步）。
