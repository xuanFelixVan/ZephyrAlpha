---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-24
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-24 模拟盘保活与成交回路

## 1. 定义

D13-12 09:25 拉起后的常驻适配器：交易时段保活、收盘后 15:05 收口撤未成交单、成交持久化在位态。三证：保活至 15:05 收口、exit_code=0、slot started/slots_running=1。🌑-5：尾段成交完整捕获口径无外部规范可依（图不编造出处）。决策问题：保活到收口了吗？退出码与成交落盘对不对？尾段成交归属谁裁？

地图在册态：wiring=wired、build=built、skeleton ✅；gap_refs 挂 table:c1_market.execution_report（消费方在等未产表→D13-G02）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | D13-12 拉起+QMT 模拟通道（XtMiniQmt）；策略槽位运行态 | `src/zephyr/ex_core/live_strategy_adapter.py`（常驻适配器本体）；`scripts/tasks/register/register_paper_session_task.ps1:47` |
| 输出面 | 成交持久化（data/fills/）+ 收口留痕（exit_code）+ execution_report 表（**消费方在等而本链未产**，见 G02） | `data/fills/`；`.runtime/logs/paper_session.log`（收口时刻与退出码留痕 exec_evidence 在案）；`config/trading_day_cycle_map.yaml#D13-24` gap_refs |
| SSOT 真源 | 图13 节点契约（行 1888-1964）+ 归档件 GAP-2 接线自证面 | `config/trading_day_cycle_map.yaml#D13-24`；`src/zephyr/ex_core/live_strategy_adapter.py` CONSUMERS 块（exec_evidence 复跑在案） |
| 代码模块 | 常驻适配器+ex_core 包+deadman 兜底 | `src/zephyr/ex_core/live_strategy_adapter.py`、`src/zephyr/ex_core/__init__.py:42`；`src/zephyr/feedback_loop/resilience/deadman_switch.py:5`（fallback 消费点） |
| 门禁约束 | fallback=D13-42 DeadmanSwitch 陈旧重跑；零下单观察面（模拟通道）；execution_report 桥面空转=三账 L1 基准腿无原料（G02 登记位） | `config/trading_day_cycle_map.yaml#D13-24` fallback/gap_refs；D13-G02 节点（src/zephyr/ex_core/position_reconciler.py、src/zephyr/trading/three_way_reconciliation.py 消费侧） |
| 自动化触发 | mechanism=B_windows_task 常驻（09:25 拉起后至 15:05）；trigger_facts last_run=2026-10-08T09:25:01；schtasks 双证 | `config/trading_day_cycle_map.yaml#D13-24` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 拉起链+模拟通道三态留痕在案 |
| 输出面 | pass | fills 落盘+收口 exit_code=0 在案（成交=0 是无票池的自然结果非断链，G02 分成因①） |
| SSOT 真源 | pass | 节点契约+GAP-2 接线自证双面 |
| 代码模块 | pass | 适配器+兜底器实存实核 |
| 门禁约束 | warn | 尾段成交完整捕获口径无外部规范（🌑-5 在册）+execution_report 桥面空转（G02） |
| 自动化触发 | pass | 常驻+deadman 陈旧重跑双保险 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**D13-G02（成交回报桥面空转，segment=B）挂本格**（edges D13-24→D13-G02、D13-27→D13-G02）：c1_market.execution_report 近 7 日仅 1 行、当日 0 行，生产端仅对模拟桥可选接线，两条独立成因（①模拟盘无票池⇒0 成交 ②回报表自上期后未再被写）图上必须分列。
- gap_refs 在册：table:c1_market.execution_report（图12 消费方在等未产表五态之一落本图环节面者）。
- 建议：①G02 处置先裁「模拟桥接线是否激活」（写入通道与幂等归图 12 让渡三，本段只挂需求）；②尾段成交捕获口径（🌑-5）补一份外部规范或 Owner 注记，收口撤销逻辑才有判据；③无票池若为现行语义，建议在 G02 台账行显式记成因①，防「0 行=断链」误报。
