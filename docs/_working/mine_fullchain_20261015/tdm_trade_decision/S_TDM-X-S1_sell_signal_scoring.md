---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-X-S1
flow: exit_flow
node_count: 7
session: mine-fullchain-tdm-20261015
---

# S_TDM-X-S1 卖出信号收集评分（7 节点）

## 1. 定义

一句话：接条件轴的扳机（goal 家族 F12）——六桶分类（risk/signal/target/trailing/time/volatility）收集→止损族/止盈族/破位退潮族并行判定→融合评分→强制清仓旁路，产出"卖不卖+多急"（紧迫度 0-1 三档）。

展开：S1-01 信号收集（8 类信号源聚合去重，分类决定确认模式：止损类立即执行不辩论、止盈类等收盘确认）；S1-02 止损五路并行（Chandelier ATR 悬停/固定-7% 生死线/支撑破位/时间止损/分时破位）；S1-03 止盈三式（移动止盈 2×ATR 只升不降/峰值回撤 30% 兑现/目标位了结）；S1-04 破位与情绪退潮（L1 六段进 distribution+情绪票→加权卖出）；S1-05 融合评分（类型权重止损 0.9/破位 0.7/止盈 0.5+多周期共振+0.2；>0.8 立即市价走 S2-01 快速通道）；S1-06 强制清仓绕过通道（KillSwitch/黑天鹅/K≥3 连破/主力弃庄四触发绕过全部评分紧迫度置 1.0，与 R1 分工不重复接线）。

## 2. 六向台账

### 2.1 输入面（有证）
- 外部入边 9 条（本段最多之一）：TDM-E-L1-AGG→X-S1/X-S1-04（情绪退潮供数）、TDM-E-L4-08→X-S1（突破失败）、TDM-E-L9-V1→X-S1（状态快照）、TDM-E-L9-V2→X-S1-04、TDM-P-P1-04→X-S1（风险否决转离场）、TDM-P-P1-06→X-S1（动作清单）、TDM-P-P2→X-S1、TDM-X-R1→X-S1-06（组合级触发绕过）。

### 2.2 输出面（有证）
- 出边 10 条：X-S1→X-S2（sequence）；X-S1-05→X-S2-01（融合紧迫度→执行方式路由）；X-S1-06→X-S2-01（强制清仓走快速通道）。
- goal 块（挂 TDM-X-FLOW 流根）：output_contract="六桶信号集＋紧迫度分＋出场效率读数（回撤保护率/假信号率）"；考试卡 18 张（exit_flow/S1/）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-X-S1（line 4400）+S1-01..06（line 4664/4703/4755/4794/4841/4887）。
- casebooks 挂 2 处（CASEBOOK-005#实盘衰减与归因 族域）；策略挂载经流根 TDM-X-FLOW：STR-VREV-001（proposed，家族替身证据：Sharpe=1.15 DSR=0.5309 run=SCR-C4-20260913-002056）。

### 2.4 代码模块（有证，6/6 子节点 ref 实存）
- sell_decision/core/：sell_signal_collector.py（MOD-SELL-001）、stop_loss_strategy.py（MOD-SELL-005）、take_profit_strategy.py（MOD-SELL-004）、breakout_failure_detector.py（MOD-SELL-003，与 L4-08 双锚共用）、sell_signal_fusion_engine.py（MOD-SELL-007）。
- trading/strategy_abnormal_exit_orchestrator.py（MOD-TRADING-008，强制清仓绕过）。
- 运行宿主（未挂图但有 CONSUMERS 实证）：sell_decision/core/s1_scan_orchestrator.py（MOD-SELL-016）——"TDM-X-S2-01 路由口消费方；57号文日循环 SOP 槽位/事件驱动调用 scan_once"。

### 2.5 门禁约束（有证）
- 四门同前；s1_scan_orchestrator INVARIANTS 自报："18 节点验证态=pending 常量如实披露(不连业务库)；mode 默认 paper 且 live 需 allow_live 显式解锁（G45-1 先 paper 档）；无信号=诚实空跑（empty_run 如实标记不伪造）；S1-06 组合级触发归 X-R1/F47 不重复接线"。

### 2.6 自动化触发（有证）
- 六子节点 activation 全=continuous；扫描宿主=事件/槽位驱动 scan_once 无常驻线程（禁 cron/Timer/sleep-loop，永久系统四要素合规实证）；与 P1-02 position_triage 共享单扫描循环（D104）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 外部入边 9 条全图最密之一，四源（闸/执行/持仓/风控）齐 |
| 输出面 | pass | →S2 双通道（融合+绕过）+output_contract 在册 |
| SSOT | pass | 节点行+18 张考卡+casebooks+STR 替身证据 |
| 代码模块 | warn | 6/6 节点 ref 实存，但扫描宿主 s1_scan_orchestrator（MOD-SELL-016）未挂图 module_ref——运行真锚在册外地 |
| 门禁约束 | warn | 四门在册；"18 节点验证态=pending 常量"为宿主自报未验证态 |
| 自动化触发 | pass | 事件/槽位驱动 scan_once+共享节拍+paper 默认档 |

**总评：warn（4/6）**。

## 4. 缺口与建议

1. 扫描宿主 s1_scan_orchestrator（MOD-SELL-016）是 S1 六节点的实际运行器却未挂图（无节点 module_ref 指向它）——建议给 TDM-X-S1 父节点补 module_ref=该宿主或新增编排子节点，消"运行真锚在册外"。
2. 宿主 INVARIANTS 自报 18 节点验证态=pending——卖出链验证欠账显性在案，建议按 REG-BTB-001 回测对象预注册批（142 对象）优先排 S1 融合评分判别度验证（REG-VALM-001 判定区分度方法）。
3. live 解锁（allow_live）与 §5 Owner 保留面"资金与实盘交易"门位的衔接未见显式引用——建议在 G45-1 解锁流程挂 Owner 门位登记。
