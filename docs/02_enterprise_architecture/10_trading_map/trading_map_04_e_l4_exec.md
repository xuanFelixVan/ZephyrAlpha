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
  classDef red fill:#2a1f14,stroke:#d97b29,color:#e8a04c,stroke-dasharray: 5 5;
  classDef paper fill:#14263a,stroke:#3d8bff,color:#9cc3ef;
  class TDM_E_L4,TDM_E_L4_01,TDM_E_L4_02,TDM_E_L4_03,TDM_E_L4_04,TDM_E_L4_06,TDM_E_L4_07,TDM_E_L4_08,TDM_E_L4_09,TDM_E_L4_11,TDM_E_L4_12,TDM_E_L4_13 red;
  class TDM_E_L4_05,TDM_E_L4_06,TDM_E_L4_10,TDM_E_L4_11,TDM_E_L4_12 paper;
```

## 节点明细

| node_id | 名称 | 决策问题 | 时点 | activation | ai_autonomy | 模块锚 | 策略挂载 |
|---|---|---|---|---|---|---|---|
| TDM-E-L4🔴 | 买卖点与执行 | 何时进场/怎么下单 | 盘中 | — | — | — | daban-sleeve(proposed) |
| TDM-E-L4-01🔴 | 分批建仓 | 置信度分几批进、每批多少（回踩 A/B/C 为置信度调节因子） | 盘中 | intraday | auto | — | — |
| TDM-E-L4-02🔴 | 买入时序 | 今天什么窗口下单（尾盘集中为主；竞价铁律 9:15-9:20 可撤假象多/9:20-9:25 只挂不撤/14:57-15… | 盘中 | intraday | auto | — | STR-MULTIFACTOR-028(proposed)、STR-MOMTRE… |
| TDM-E-L4-03🔴 | 价格锚定 | 限价还是市价（限价为主，市价仅应急） | 盘中 | intraday | auto | — | — |
| TDM-E-L4-04🔴 | 资金分配多标的 | 多标地下单排序与资金可用性兜底 | 盘中 | intraday | auto | — | — |
| TDM-E-L4-05 | 打板执行专项 | 排板/扫板/打回封选哪个+封单质量验证+撤单纪律（换手板>缩量板/封单要实且递增/黄金排队窗口 5-15 分钟/封单被快… | 盘中 | intraday | paper | src/zephyr/ex_core/daban_execution.py（MOD-EX-001） | — |
| TDM-E-L4-06🔴 | 执行算法 | 大单怎么拆（EXA 六件选型：TWAP/VWAP/ICEBERG/IS/POV/ALT；参与率纪律≤市场量 10-20%… | 盘中 | intraday | paper | — | — |
| TDM-E-L4-07🔴 | 条件触发队列 | 买入/卖出/执行/风控扳机怎么统一注册与触发（横切基础设施） | 持续 | continuous | auto | — | — |
| TDM-E-L4-08🔴 | 突破失败降级 | 突破失败后批次停不停、止损评估启不启 | 盘中 | intraday | auto | — | — |
| TDM-E-L4-09🔴 | 执行硬约束 | 执行硬约束全过了吗（T+1/涨跌停/价格笼子/成本模型实时估算——佣金+印花税+滑点） | 持续 | continuous | auto | — | — |
| TDM-E-L4-10 | 订单生命周期状态机 | 每笔订单当前处于九态的哪一态（New/PendingNew/Accepted/Partial/Filled/Pendin… | 持续 | continuous | paper | src/zephyr/ex_core/async_fill_dispatcher.py（MOD-L06-001） | — |
| TDM-E-L4-11🔴 | 部分成交与撤改处理 | 部分成交后撤还是等、撤改单竞态怎么处理 | 盘中 | intraday | paper | — | — |
| TDM-E-L4-12🔴 | 订单级预检 | 这笔单发出前的最后校验（资金可用/持仓限制/风控限额/禁止清单）过了吗 | 盘中 | intraday | paper | — | — |
| TDM-E-L4-13🔴 | 执行容灾对账 | 我以为发出的、券商说发出的、实际成交的三方对上账了吗（断线重连/对账/RTO<5min） | 持续 | continuous | auto | — | — |

## 挂载清单

**模块锚（MOD）**：MOD-EX-001 src/zephyr/ex_core/daban_execution.py、MOD-L06-001 src/zephyr/ex_core/async_fill_dispatcher.py

**策略挂载（STR）**：STR-MOMTREND-004、STR-MULTIFACTOR-028、daban-sleeve
