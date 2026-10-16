---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-E-L4
flow: entry_flow
node_count: 15
session: mine-fullchain-tdm-20261015
---

# S_TDM-E-L4 买卖点与执行（15 节点）

## 1. 定义

一句话：执行层总枢纽管"什么时候、怎么把单下出去"（PT-04/PT-05：决策没优势不出手、票买得便宜卖得顺）——13 子环节覆盖分批建仓/时序/价格锚定/资金分配/打板专项/执行算法/条件队列/突破降级/硬约束/订单九态/部分成交/预检/容灾对账（+执行成本反馈共 14 子）。

展开：决策定了之后到券商柜台之间的全部工程：置信度定分批比例（A 级 70%/中 50%/低 30%）、时序窗口表（尾盘 14:50-14:57 主窗）、限价锚定（卖一价+1 tick）、打板三式（排板/扫板/打回封）、大单拆分选型（TWAP/VWAP/ICEBERG/IS，>500 万必拆）、五道硬约束、订单九态机（New..Suspended）、发单前五查、三方对账（本地订单簿 vs 券商委托 vs 成交）。骨架总纲写 16 节点、地图实读 15（漂移记录于 §4）。实盘执行出域通道（QMT 指令出域→柜台回执）由本环节与 X-S2 共同承载（骨架 §3 缺口 11：无独立执行链图）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边：L3→L4、L3-10→L4（预检）；TDM-F-C2-01→TDM-E-L4（组合净指令流）；TDM-P-P3-04→TDM-E-L4（加仓执行复用建仓件）；TDM-X-R1-03→TDM-E-L4（护盘白名单加仓）；TDM-X-S2-06→TDM-E-L4-12（卖出质量反馈回预检）。
- 通道面：图13-D13-07 QMT 终端看门狗+D13-20 竞价命中判定（骨架 §2.4 行）为执行通道供血。

### 2.2 输出面（有证）
- 出边 24 条：L4→TDM-E-FLOW（流根）；L4-08→TDM-X-S1（突破失败喂卖出信号）；L4-10→TDM-P-P1-01（订单状态回灌持仓对账）；L4-13→TDM-F-C3-01（容灾对账喂归因）。
- 状态矩阵 6 格挂 TDM-E-L4（六段各格，ignition 格 mounted=daban-sleeve 实读）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-E-L4（line 3065）至 L4-14（line 3616），15 节点行号连读。
- 执行算法登记：algo_refs 值域 EXA-TWAP-001/EXA-VWAP-001/EXA-ICEBERG-001/EXA-IS-001/EXA-POV-001/EXA-ALT-001（EXA 前缀与 DAL 正交，门禁 R13 扩展值域）。
- casebooks 挂 5 处；考试卡 32 张（entry_flow/L4/ 实读）。

### 2.4 代码模块（有证，14/14 子节点 ref 实存）
- ex_core 族：order_splitter.py（MOD-EX-014）、pricing_policy.py、local_order_queue.py、price_cage.py、order_manager.py、fill_handler.py、pre_execution_checker.py（MOD-EX-024）、daban_execution.py（MOD-EX-001）。
- ex_sor 族：algo_execution_selector.py（MOD-XS-011）、services/execution_quality_scorer.py（MOD-XS-018）。
- 协同件：plan_engine/closing_session_decision.py（MOD-PLAN-003，决策侧时序）、signal_fundamental/capital/capital_allocator.py（MOD-L03-001）、sell_decision/core/breakout_failure_detector.py（MOD-SELL-003 双锚节点）、trading/three_way_reconciliation.py（MOD-TRADING-013）。
- 父枢纽 TDM-E-L4 无 ref（结构枢纽，INV-1 允许）。

### 2.5 门禁约束（有证）
- 四门同前；本环节=实盘资金门位高域（risk_tier_registry.yaml REG-RISK-TIER-001：交易核心域=high，production 流转 Owner 保留——ROOR line 926-933 实读）。

### 2.6 自动化触发（有证）
- L4-07 条件队列/L4-09 硬约束/L4-10 订单九态=continuous；L4-01/02/03/05/06/11/12=intraday；L4-14=盘后。
- 模拟/实盘双通道挂图13-B（D13-12 模拟盘拉起、D13-20 竞价窗闸、D13-28 盘后结算）；执行单产出发于拍板体 #305 安全态约束（dloop INVARIANTS：观察/记录模式零下单）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 决策/组合/加仓/护盘/卖出质量五路入边+QMT 通道 |
| 输出面 | pass | 出边 24 条+状态矩阵 6 格 |
| SSOT | pass | 15 节点行+EXA 值域+high 风险域在册 |
| 代码模块 | pass | 14/14 子节点实存（父枢纽 null=设计允许） |
| 门禁约束 | pass | 四门+Owner 资金门位 |
| 自动化触发 | pass | continuous/intraday/盘后分档+双通道挂图13 |

**总评：pass（6/6，附漂移注记）**。

## 4. 缺口与建议

1. 骨架总纲写 L4=16 节点、地图实读 15——随骨架批对齐。
2. 实盘执行出域通道（指令出域→柜台回执）无独立执行链图（骨架 §3 缺口 11 原文在案；REG-EXA-001 监管合规 8 字段在册）——建议立执行链图议题，本环节为挂靠宿主。
3. L4-02 买入时序为决策/执行双件分立（决策侧 closing_session_decision 14:45-15:00、执行侧 batched_position_builder 14:50-14:57 挂单主窗）——执行侧件 batched_position_builder 未挂 module_ref（只在 algo_note 散文），建议补第二锚或声明归属。
