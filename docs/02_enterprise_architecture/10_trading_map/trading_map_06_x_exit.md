---
doc_type: architecture_view
title: 交易决策地图·离场流 X·信号/执行/R1 应急
version: "1.0.0"
status: active
date: 2026-09-07
owner: auto-generator
ttl: permanent
source: config/trading_decision_map.yaml
---

# 交易决策地图 · 离场流 X·信号/执行/R1 应急（自动派生）

> **本文件由生成器自动派生，禁止手编**。真源=`config/trading_decision_map.yaml`（改动后 git commit → 运行时启动自动重生成）。
> 规模：15 节点｜🔴设计态（红节点）7｜📄paper 实盘执行 4｜图例：橙虚线=设计态，蓝底=📄paper 实盘执行节点（D18 治理阶梯）。
> 网页版（可缩放）：[_zoomable_html/trading_map_06_x_exit.html](_zoomable_html/trading_map_06_x_exit.html)

## 关系图

```mermaid
flowchart TD
  TDM_X_S1["卖出信号收集评分<br/>哪些卖出信号触发了/强度如何"]
  TDM_X_S2["离场执行<br/>怎么卖（一次性/分批/竞价/尾盘）"]
  TDM_X_R1["应急保命<br/>暴跌/流动性危机是否触发无条件降仓"]
  TDM_X_S1_01["信号收集与六桶分类<br/>卖出信号有哪些触发了、各属哪一类"]
  TDM_X_S1_02["止损族判定<br/>止损线触发了吗（Chandelier/时间/支撑/竞价/分时）"]
  TDM_X_S1_03["止盈族判定<br/>止盈条件到了吗（移动止盈/峰值回撤/目标位）"]
  TDM_X_S1_04["破位与情绪退潮信号<br/>突破失败了吗、情绪退潮了吗、主力派发了吗"]
  TDM_X_S1_05["信号融合与紧迫度评分<br/>综合卖出意愿多强、多急"]
  TDM_X_S1_06["强制清仓绕过通道<br/>是否触发无条件离场（绕过一切评分）"]
  TDM_X_S2_01["执行方式路由 📄paper<br/>这笔卖出怎么执行（一次性/分批/竞价/尾盘）"]
  TDM_X_S2_02["T+1与涨跌停约束 📄paper<br/>跌停卖不出怎么办、今日可卖额度多少"]
  TDM_X_S2_03["执行时段路由<br/>现在是什么时段、该走哪条卖出通道"]
  TDM_X_S2_04["本地条件单管理 📄paper<br/>止损止盈条件单怎么挂才不被仓位冻结卡死"]
  TDM_X_S2_05["分批止盈执行 📄paper<br/>分批怎么切、每批卖多少"]
  TDM_X_S2_06["卖出闭环与退出效率<br/>卖对了吗（卖飞率/避损率/捕获率）"]
  EXT_TDM_E_L4_08(["⧉ TDM-E-L4-08（见对应文件）"])
  EXT_TDM_E_L1_AGG(["⧉ TDM-E-L1-AGG（见对应文件）"])
  EXT_TDM_P_P2(["⧉ TDM-P-P2（见对应文件）"])
  EXT_TDM_P_P1_04(["⧉ TDM-P-P1-04（见对应文件）"])
  EXT_TDM_P_P1_06(["⧉ TDM-P-P1-06（见对应文件）"])
  EXT_TDM_P_P2_04(["⧉ TDM-P-P2-04（见对应文件）"])
  EXT_TDM_P_P2_03(["⧉ TDM-P-P2-03（见对应文件）"])
  EXT_TDM_F_C2_01(["⧉ TDM-F-C2-01（见对应文件）"])
  EXT_TDM_E_L4_08 --> TDM_X_S1
  EXT_TDM_E_L1_AGG --> TDM_X_S1
  EXT_TDM_P_P2 --> TDM_X_S1
  EXT_TDM_P_P1_04 --> TDM_X_S1
  EXT_TDM_P_P2_04 --> TDM_X_S2
  EXT_TDM_P_P2_04 --> TDM_X_S2_01
  EXT_TDM_P_P1_06 --> TDM_X_S1
  EXT_TDM_P_P2_03 --> TDM_X_S2_01
  TDM_X_S1 -->|顺序| TDM_X_S2
  TDM_X_S1_01 -->|喂给| TDM_X_S1_02
  TDM_X_S1_01 -->|喂给| TDM_X_S1_03
  TDM_X_S1_01 -->|喂给| TDM_X_S1_04
  TDM_X_S1_02 -->|喂给| TDM_X_S1_05
  TDM_X_S1_03 -->|喂给| TDM_X_S1_05
  TDM_X_S1_04 -->|喂给| TDM_X_S1_05
  TDM_X_S1_05 -->|顺序| TDM_X_S2_01
  TDM_X_S1_06 -->|喂给| TDM_X_S2_01
  TDM_X_S2_01 -->|喂给| TDM_X_S2_02
  TDM_X_S2_01 -->|喂给| TDM_X_S2_03
  TDM_X_S2_01 -->|喂给| TDM_X_S2_04
  TDM_X_S2_01 -->|喂给| TDM_X_S2_05
  TDM_X_S2_01 -->|喂给| TDM_X_S2_06
  TDM_X_S2_05 -->|喂给| TDM_X_S2_06
  TDM_X_S2_06 --> EXT_OUT_TDM_F_C3_01([→ TDM-F-C3-01])
  TDM_X_S1_04 -->|喂给| TDM_X_S1_06
  TDM_X_R1 -->|喂给| TDM_X_S1_06
  TDM_X_R1 --> EXT_OUT_TDM_F_C2_01([→ TDM-F-C2-01])
  TDM_X_R1 --> EXT_OUT_TDM_P_P2_01([→ TDM-P-P2-01])
  TDM_X_S2_02 -->|喂给| TDM_X_S2_06
  TDM_X_S2_03 -->|喂给| TDM_X_S2_06
  TDM_X_S2_04 -->|喂给| TDM_X_S2_06
  EXT_TDM_F_C2_01 --> TDM_X_S2_01
  TDM_X_S2_06 --> EXT_OUT_TDM_E_L4_12([→ TDM-E-L4-12])
  EXT_TDM_E_L1_AGG --> TDM_X_S1_04
  TDM_X_R1 ==>|广播| TDM_X_S2
  classDef red fill:#2a1f14,stroke:#d97b29,color:#e8a04c,stroke-dasharray: 5 5;
  classDef paper fill:#14263a,stroke:#3d8bff,color:#9cc3ef;
  class TDM_X_S1,TDM_X_S2,TDM_X_R1,TDM_X_S1_06,TDM_X_S2_02,TDM_X_S2_03,TDM_X_S2_04 red;
  class TDM_X_S2_01,TDM_X_S2_02,TDM_X_S2_04,TDM_X_S2_05 paper;
```

## 节点明细

| node_id | 名称 | 决策问题 | 时点 | activation | ai_autonomy | 模块锚 | 策略挂载 |
|---|---|---|---|---|---|---|---|
| TDM-X-S1🔴 | 卖出信号收集评分 | 哪些卖出信号触发了/强度如何 | 持续 | — | — | — | — |
| TDM-X-S2🔴 | 离场执行 | 怎么卖（一次性/分批/竞价/尾盘） | 盘中 | — | — | — | — |
| TDM-X-R1🔴 | 应急保命 | 暴跌/流动性危机是否触发无条件降仓 | 持续 | — | — | — | — |
| TDM-X-S1-01 | 信号收集与六桶分类 | 卖出信号有哪些触发了、各属哪一类 | 持续 | continuous | auto | src/zephyr/sell_decision/core/sell_signal_collector.py（MOD-S… | — |
| TDM-X-S1-02 | 止损族判定 | 止损线触发了吗（Chandelier/时间/支撑/竞价/分时） | 持续 | continuous | auto | src/zephyr/sell_decision/core/stop_loss_strategy.py（MOD-SELL… | — |
| TDM-X-S1-03 | 止盈族判定 | 止盈条件到了吗（移动止盈/峰值回撤/目标位） | 持续 | continuous | auto | src/zephyr/sell_decision/core/take_profit_strategy.py（MOD-SE… | — |
| TDM-X-S1-04 | 破位与情绪退潮信号 | 突破失败了吗、情绪退潮了吗、主力派发了吗 | 持续 | continuous | auto | src/zephyr/sell_decision/core/breakout_failure_detector.py（M… | — |
| TDM-X-S1-05 | 信号融合与紧迫度评分 | 综合卖出意愿多强、多急 | 持续 | continuous | auto | src/zephyr/sell_decision/core/sell_signal_fusion_engine.py（M… | — |
| TDM-X-S1-06🔴 | 强制清仓绕过通道 | 是否触发无条件离场（绕过一切评分） | 持续 | continuous | auto | — | — |
| TDM-X-S2-01 | 执行方式路由 | 这笔卖出怎么执行（一次性/分批/竞价/尾盘） | 盘中 | intraday | paper | src/zephyr/sell_decision/core/sell_execution_planner.py（MOD-… | — |
| TDM-X-S2-02🔴 | T+1与涨跌停约束 | 跌停卖不出怎么办、今日可卖额度多少 | 盘中 | intraday | paper | — | — |
| TDM-X-S2-03🔴 | 执行时段路由 | 现在是什么时段、该走哪条卖出通道 | 盘中 | intraday | auto | — | — |
| TDM-X-S2-04🔴 | 本地条件单管理 | 止损止盈条件单怎么挂才不被仓位冻结卡死 | 持续 | continuous | paper | — | — |
| TDM-X-S2-05 | 分批止盈执行 | 分批怎么切、每批卖多少 | 盘中 | intraday | paper | src/zephyr/sell_decision/core/scaling_out.py（MOD-SELL-017） | — |
| TDM-X-S2-06 | 卖出闭环与退出效率 | 卖对了吗（卖飞率/避损率/捕获率） | 盘后 | postmarket | auto | src/zephyr/sell_decision/core/sell_execution_quality_tracker… | — |

## 挂载清单

**模块锚（MOD）**：MOD-SELL-001 src/zephyr/sell_decision/core/sell_signal_collector.py、MOD-SELL-003 src/zephyr/sell_decision/core/breakout_failure_detector.py、MOD-SELL-004 src/zephyr/sell_decision/core/take_profit_strategy.py、MOD-SELL-005 src/zephyr/sell_decision/core/stop_loss_strategy.py、MOD-SELL-007 src/zephyr/sell_decision/core/sell_signal_fusion_engine.py、MOD-SELL-012 src/zephyr/sell_decision/core/sell_execution_quality_tracker.py、MOD-SELL-017 src/zephyr/sell_decision/core/scaling_out.py、MOD-SELL-019 src/zephyr/sell_decision/core/sell_execution_planner.py
