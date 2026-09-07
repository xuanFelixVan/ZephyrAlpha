---
doc_type: architecture_view
title: 交易决策地图·建仓流 L4·执行
version: "1.0.0"
status: active
date: 2026-09-07
owner: auto-generator
ttl: permanent
source: config/trading_decision_map.yaml
---

# 交易决策地图 · 建仓流 L4·执行（自动派生）

> **本文件由生成器自动派生，禁止手编**。真源=`config/trading_decision_map.yaml`（改动后 git commit → 运行时启动自动重生成）。
> 规模：14 节点｜🔴设计态（红节点）12｜📄paper 实盘执行 5｜图例：橙虚线=设计态，蓝底=📄paper 实盘执行节点（D18 治理阶梯）。
> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/10_trading_map/_zoomable_html/trading_map_04_e_l4_exec.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 关系图

```mermaid
flowchart TD
  TDM_E_L4["买卖点与执行<br/>何时进场/怎么下单"]
  TDM_E_L4_01["分批建仓<br/>置信度分几批进、每批多少（回踩 A/B/C 为置信度调节因子）"]
  TDM_E_L4_02["买入时序<br/>今天什么窗口下单（尾盘集中为主；竞价铁律 9:15-9:20 可撤假象多/9:20-…"]
  TDM_E_L4_03["价格锚定<br/>限价还是市价（限价为主，市价仅应急）"]
  TDM_E_L4_04["资金分配多标的<br/>多标地下单排序与资金可用性兜底"]
  TDM_E_L4_05["打板执行专项 📄paper<br/>排板/扫板/打回封选哪个+封单质量验证+撤单纪律（换手板>缩量板/封单要实且递增/黄…"]
  TDM_E_L4_06["执行算法 📄paper<br/>大单怎么拆（EXA 六件选型：TWAP/VWAP/ICEBERG/IS/POV/AL…"]
  TDM_E_L4_07["条件触发队列<br/>买入/卖出/执行/风控扳机怎么统一注册与触发（横切基础设施）"]
  TDM_E_L4_08["突破失败降级<br/>突破失败后批次停不停、止损评估启不启"]
  TDM_E_L4_09["执行硬约束<br/>执行硬约束全过了吗（T+1/涨跌停/价格笼子/成本模型实时估算——佣金+印花税+滑点…"]
  TDM_E_L4_10["订单生命周期状态机 📄paper<br/>每笔订单当前处于九态的哪一态（New/PendingNew/Accepted/Par…"]
  TDM_E_L4_11["部分成交与撤改处理 📄paper<br/>部分成交后撤还是等、撤改单竞态怎么处理"]
  TDM_E_L4_12["订单级预检 📄paper<br/>这笔单发出前的最后校验（资金可用/持仓限制/风控限额/禁止清单）过了吗"]
  TDM_E_L4_13["执行容灾对账<br/>我以为发出的、券商说发出的、实际成交的三方对上账了吗（断线重连/对账/RTO<5mi…"]
  EXT_TDM_E_L2_03_1(["⧉ TDM-E-L2-03-1（见对应文件）"])
  EXT_TDM_E_L2_07_1(["⧉ TDM-E-L2-07-1（见对应文件）"])
  EXT_TDM_E_L3_10(["⧉ TDM-E-L3-10（见对应文件）"])
  EXT_TDM_E_L3(["⧉ TDM-E-L3（见对应文件）"])
  EXT_TDM_P_P3_04(["⧉ TDM-P-P3-04（见对应文件）"])
  EXT_TDM_F_C2_01(["⧉ TDM-F-C2-01（见对应文件）"])
  EXT_TDM_X_S2_06(["⧉ TDM-X-S2-06（见对应文件）"])
  EXT_TDM_E_L2_03_1 --> TDM_E_L4
  EXT_TDM_E_L2_07_1 --> TDM_E_L4
  EXT_TDM_E_L3_10 --> TDM_E_L4
  TDM_E_L4_01 -->|顺序| TDM_E_L4_02
  TDM_E_L4_02 -->|顺序| TDM_E_L4_03
  TDM_E_L4_03 -->|顺序| TDM_E_L4_04
  TDM_E_L4_04 -->|喂给| TDM_E_L4_05
  TDM_E_L4_04 -->|喂给| TDM_E_L4_06
  TDM_E_L4_07 -->|喂给| TDM_E_L4_05
  TDM_E_L4_07 -->|喂给| TDM_E_L4_06
  TDM_E_L4_08 --> EXT_OUT_TDM_X_S1([→ TDM-X-S1])
  TDM_E_L4_04 -->|喂给| TDM_E_L4_12
  TDM_E_L4_12 -->|喂给| TDM_E_L4_05
  TDM_E_L4_12 -->|喂给| TDM_E_L4_06
  TDM_E_L4_05 -->|喂给| TDM_E_L4_10
  TDM_E_L4_06 -->|喂给| TDM_E_L4_10
  TDM_E_L4_10 -->|喂给| TDM_E_L4_11
  TDM_E_L4_10 -->|喂给| TDM_E_L4_13
  TDM_E_L4_11 -->|喂给| TDM_E_L4_13
  TDM_E_L4_13 --> EXT_OUT_TDM_F_C3_01([→ TDM-F-C3-01])
  EXT_TDM_E_L3 --> TDM_E_L4
  TDM_E_L4 -->|喂给| TDM_E_L4_01
  TDM_E_L4_10 -->|喂给| TDM_E_L4_08
  TDM_E_L4_09 -->|喂给| TDM_E_L4_12
  TDM_E_L4_10 --> EXT_OUT_TDM_P_P1_01([→ TDM-P-P1-01])
  EXT_TDM_P_P3_04 --> TDM_E_L4
  EXT_TDM_F_C2_01 --> TDM_E_L4
  EXT_TDM_X_S2_06 --> TDM_E_L4_12
  classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
  classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5;
  classDef paper fill:#e8f5e9,stroke:#2e7d32,stroke-width:2.5px,color:#000;
  class TDM_E_L4_05,TDM_E_L4_10 production;
  class TDM_E_L4,TDM_E_L4_01,TDM_E_L4_02,TDM_E_L4_03,TDM_E_L4_04,TDM_E_L4_06,TDM_E_L4_07,TDM_E_L4_08,TDM_E_L4_09,TDM_E_L4_11,TDM_E_L4_12,TDM_E_L4_13 design;
  class TDM_E_L4_05,TDM_E_L4_06,TDM_E_L4_10,TDM_E_L4_11,TDM_E_L4_12 paper;
```

## 节点明细

| node_id | 名称 | 怎么算（大白话） | 时点 | 档位 | 模块锚 |
|---|---|---|---|---|---|
| TDM-E-L4🔴 | 买卖点与执行 | 执行层总枢纽：分批建仓/时序/价格锚定/资金分配/打板专项/执行算法/条件队列/突破降级/硬约束/订单九态/部分成交/预检/容灾对账 13 子环节。 管'什么时候、怎么把单下出去'。 | 盘中 | — | — |
| TDM-E-L4-01🔴 | 分批建仓 | 置信度定分批：高置信（A 级回踩+三维共振）=首批 70%；中置信=50%；低置信=30% 试探。 剩余额度等确认信号（涨 2% 或站稳分时均线）再进。 回踩 A/B/C 是置信度调节因子。 | 盘中 | auto | — |
| TDM-E-L4-02🔴 | 买入时序 | 时序窗口表：尾盘 14:30-14:55 为集中窗口（全天信息确认后，隔夜风险最小）；竞价铁律=9:15-9:20 可撤挂单密集不参与、9:20-9:25 不可撤观察不动作；开盘 30 分钟只执行盘前计划单不新开。 | 盘中 | auto | — |
| TDM-E-L4-03🔴 | 价格锚定 | 限价为主（成本可控），市价仅应急（跌停逃命/强平）。 限价锚：买=卖一价+1 tick 保证成交又不追高；突破买=突破价上方 0.5% 挂单等着成交。 | 盘中 | auto | — |
| TDM-E-L4-04🔴 | 资金分配多标的 | 多标的资金排序：顺位高的先下单占资金；资金不足时按'置信度×顺位'加权分配；预留 10% 机动资金不分配（应对盘中机会）。 | 盘中 | auto | — |
| TDM-E-L4-05 | 打板执行专项 | 打板三式：排板（涨停前挂单排队，封单/流通盘>2% 才排）、扫板（封板瞬间市价扫入，只扫首次封板）、打回封（炸板后回封确认再进）。 换手板优于缩量板（换手充分=接力意愿强）；撤单纪律=封单骤减 20% 立即撤。 | 盘中 | paper | MOD-EX-001 |
| TDM-E-L4-06🔴 | 执行算法 | 大单拆分选型表：TWAP（时间均匀，常规）、VWAP（跟量，流动性好时）、ICEBERG（隐藏，防暴露）、IS（急单，前重后轻）。 >500 万单必拆；单笔≤盘口一档 50%；冲击成本预算 0.3%。 | 盘中 | paper | — |
| TDM-E-L4-07🔴 | 条件触发队列 | 横切基础设施：所有触发器（价格/时间/指标/风控）统一注册到条件队列，tick 驱动按优先级触发（风控>卖出>买入）。 一处注册全图复用，防各策略各写各的触发器打架。 | 持续 | auto | — |
| TDM-E-L4-08🔴 | 突破失败降级 | 突破失败判定：突破价后 30 分钟内跌回突破位下方=失败→停后续批次+启动止损评估（-3% 或前低）。 突破买入的批次控制——首仓失败不加仓。 | 盘中 | auto | — |
| TDM-E-L4-09🔴 | 执行硬约束 | 五道硬约束过一遍才发单：T+1（当日买入不可卖）、涨跌停价格笼子（申报价±2% 限制）、成本模型实时估（预期冲击+佣金是否吃掉预期收益 1/3）、资金可用、持仓限额。 | 持续 | auto | — |
| TDM-E-L4-10 | 订单生命周期状态机 | 订单九态机：New/PendingNew/PartiallyFilled/Filled/Cancelled/PendingCancel/Rejected/Expired/Suspended。 每态有明确的超时与重试策略（如 PendingNew>3 秒重发确认）。 | 持续 | paper | MOD-L06-001 |
| TDM-E-L4-11🔴 | 部分成交与撤改处理 | 部分成交三规则：成交<50% 且价格远离=撤单重挂；成交>50%=保留等剩余；改单与撤单竞态=以券商回报为准+本地加锁。 部分成交的仓位按已成交部分管理。 | 盘中 | paper | — |
| TDM-E-L4-12🔴 | 订单级预检 | 发单前最后五查：资金可用≥委托额、持仓不超该股限额、不触风控熔断状态、非禁止清单（ST/黑名单）、价格在笼子内。 任何一条不过=拒单并记录原因。 | 盘中 | paper | — |
| TDM-E-L4-13🔴 | 执行容灾对账 | 三方对账：本地订单簿 vs 券商委托回报 vs 实际成交。 断线重连后先全量对账再恢复交易；孤儿单（券商有我无）=立即同步并评估处理；日终对不平=挂起次日竞价处理。 | 持续 | auto | — |

## 挂载清单

**模块锚（MOD）**：MOD-EX-001 src/zephyr/ex_core/daban_execution.py、MOD-L06-001 src/zephyr/ex_core/async_fill_dispatcher.py

**策略挂载（STR）**：STR-MOMTREND-004、STR-MULTIFACTOR-028、daban-sleeve
