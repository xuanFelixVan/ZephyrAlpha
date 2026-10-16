---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-P-P1
flow: position_flow
node_count: 7
session: mine-fullchain-tdm-20261015
---

# S_TDM-P-P1 持仓体检（7 节点）

## 1. 定义

一句话：拿着的票每天体检（PT-06"买入逻辑死了还拿着=给死策略送钱"）——对账/分级/逻辑存活/风险否决/组合级五路并行体检+结论汇总裁决，输出每只持仓的当日动作清单（维持/可做T/可加仓/减仓/转离场）。

展开：编排=position_checkup_orchestrator（MOD-POS-030）串五件+裁决中心（position_adjudication_center，MOD-POS-024），只编排不重造、逐段 fail-open、零下单观察态；任一子项异常=该持仓置"人工确认"默认态。六节点子件：P1-01 对账三步（QMT 桥 Stock.csv↔本地 strategy_book 逐笔核对）、P1-02 分级三档定盯盘频率（WATCH 秒级/MONITOR 5 分钟/HOLD 事件驱动）、P1-03 买入逻辑存活判定（打板查梯队/多因子查暴露漂移/事件仓查衰减）、P1-04 四类风险否决线（生死线-7%/时间止损/事件禁区/板块退潮）、P1-05 组合级三查（集中>20%/漂移>25%/扎堆>3 只）、P1-06 结论汇总。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边：TDM-E-L1-AGG→TDM-P-P1（总闸态）、TDM-E-L4-10→TDM-P-P1-01（订单状态回灌）。
- 对账取数面：P1-01 读 QMT 桥持仓文件（config/qmt_environments.yaml 域）；父节点 algo_note 明文"上游对账取数面未接线前 inputs 缺席=skipped 留痕"——半接线状态地图自报（见 §4）。

### 2.2 输出面（有证）
- 出边 16 条：P1→TDM-P-P2；P1-04→P2-01/P2-04/X-S1（风险否决冻结做T/加仓资格+转离场）；P1-05→P2-04（漂移越带下发减仓指令）；P1-06→P2-01/P3-01/X-S1（动作清单分发三流）。
- 考卷挂接：position_recipe_grid_schema.yaml#M5_thesis_survival 维（2026-10-15 ⑤席新增）=P1-03/comparison/03 解锁件（"考卡 TDM-P-P1-03/comparison/03 解锁件"原文在 grid schema line 12/105-122）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-P-P1（line 3662-3769），7 节点行号连读。
- goal 块 family=F13_持仓流P（挂 TDM-P-FLOW 流根）；casebooks 挂 2 处；考试卡 26 张（position_flow/P1/ 实读，本 flow 最多）。
- P1-02 判级修正留痕（2026-09-18 深度审查：破止损线直判 WATCH，旧码 abs 对称化误判 MONITOR，rpt_e05+note_confirmed）——ALGO-NOTE-SYNC 纪律兑现实例。

### 2.4 代码模块（有证，7/7 ref 实存）
- position/core/：position_checkup_orchestrator.py（编排，MOD-POS-030 见 algo_note）、position_state_machine.py（MOD-POS-002 六态）、position_drift_monitor.py（MOD-POS-003）、position_adjudication_center.py（MOD-POS-024）。
- 跨包件：sell_decision/core/position_triage.py（MOD-SELL-000）、plan_engine/thesis_survival.py（MOD-PLAN-024）、risk/core/ashare_stop_loss_engine.py（MOD-RK-09）。

### 2.5 门禁约束（有证）
- 四门同前（MAP-ALIGNMENT/TDM-MOUNT-COVERAGE/ALGO-NOTE-SYNC/ALGO-FLOW-LINK）。
- P1-03 逻辑存活判定与 grid M5 维联动——考卷展开禁直改共享册（grid schema line 112-118"先炸后筛"病根与 --schema-path 探针册纪律）。

### 2.6 自动化触发（有证）
- dloop 链明文：master switch DEPENDENCIES 含 zephyr.position.core.position_checkup_orchestrator(default_positions_loader/run_position_checkup)，"P1 持仓体检棒（MOD-POS-030，F42 G42-1 接线，盘前段）"；挂 dloop premarket 段（dloop_post 16:45 自动圈，事件驱动无 cron）。
- P1-02/P1-05=continuous（与 s1_scan_orchestrator 共享单扫描循环，D104：调用方用同一节拍喂 triage_levels——s1_scan_orchestrator.py INVARIANTS 实读）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | warn | 入边在册，但对账取数面（QMT 桥→strategy_book 自动对账）地图自报未接线=inputs 缺席 skipped 留痕 |
| 输出面 | pass | 出边 16 条分发 P2/P3/X 三流+grid M5 解锁件 |
| SSOT | pass | 7 节点行+26 张考卡+casebooks+判级修正留痕 |
| 代码模块 | pass | 7/7 ref 实存 |
| 门禁约束 | pass | 四门+探针册纪律 |
| 自动化触发 | pass | dloop 盘前棒 F42 G42-1 接线+共享扫描节拍 |

**总评：warn（5/6）**。

## 4. 缺口与建议

1. 【本环节最大缺口】P1-01 对账取数面未接线：QMT 桥持仓→本地台账自动核对链路未通，当前体检在 inputs 缺席时以 skipped 留痕降级运行——建议立接线工单（依赖图13-D13-27 盘中持仓对账事件入口，骨架 §2.4 行）。
2. P1-03 买入逻辑存活判定的三查（梯队/因子漂移/事件衰减）依赖 L2 板块热度与因子暴露供数，供数边未见显式入边（语义耦合）——建议补数据边或在节点注记声明供数方。
3. 动作清单（P1-06）下游消费方为 P2-01/P3-01/X-S1 三流——"动作过裁决中心+落审计"的审计落点（judgment_ledger.py）未在图上标边，建议补审计边。
