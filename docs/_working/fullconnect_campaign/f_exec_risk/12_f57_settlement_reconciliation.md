---
ttl: task_bound
title: "F57 结算对账与三方核对——settlement/three_way/eod/recon_runner 四步对账（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F57 · 结算对账与三方核对（trading 结算域+ex_core eod）

> 上游=F56 桥柜台镜像（供券商侧真源）；下游=F42 持仓体检/F63 仓位对账/F60 NAV。
> 证据基线：m7 01/03 册+本日（09-27）排班与 import 链独立复扫。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | 券商结算记录（broker_settlement_adapter.fills_to_broker_records）、fill_handler.query_fills_by_date、柜台镜像 PositionSnapshot |
| 下游消费 | 对账结论→position_reconciler/持仓体检/DailyAuditor PnLReconciliation；execution_report 侧留痕+告警（schedule.yaml :229 description）|
| 自动化触发 | **15:40 eod_reconciliation 槽（src/zephyr/data/config/schedule.yaml:220-224 本日实锚，cron "40 15 * * 0-4"）——槽位注释自认"唯一入口=src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation"（非自愈 reconciler 环，定时事实核对，宪法 §9.3 合规注记在 yaml 原文）**；run_post_settlement=one-shot CLI（recon→audit→report→exit，register_post_settlement_task.ps1 :18 自注 designed as manual CLI）|
| 真源与注册表 | recon_runner MOD-TRADING-007（settlement_record_aggregate.py:25 自注"回测 vs 模拟盘三层对账编排，场景互补"）；56 号文 §5（15:30 步骤③④）；EodReconciler INVARIANTS（Decimal-only/frozen Result/align_to_broker 默认 False=dry-run/expire 幂等）|
| 门禁与质量尺 | Fail-Closed：对齐须显式开启且输入齐备；alert_sink 异常吞没不阻断；同输入必同输出（clock 注入）|
| 当前运行状态 | **黄**——三层对账机制建成+排班在 yaml；recon_runner 是否被真触发未证（wiring_gap §2.2 L-3 在案：M3 两卷"recon_runner 是否被真触发未证未证"）；eod_reconciliation.py 本体**零 import 命中**（本日 grep from zephyr.ex_core.eod_reconciliation 全仓零命中）|

## 二、子模块三级枚举（本日实扫 wc -l）

- **trading 结算域**：settlement_reconciliation.py 431（SettlementReconciler）｜three_way_reconciliation.py 441（三方核对）｜recon_runner.py（run_daily_reconciliation :392，import settlement_reconciliation :88-89+broker_settlement_adapter :87+ex_core PositionReconciler :78）｜post_settlement_pipeline.py 180（盘后管线真源）｜night_shift_queue.py 161（夜班队列）｜trading_order_aggregate.py/settlement_record_aggregate.py/broker_settlement_adapter.py（聚合与适配）
- **ex_core 对账件**：eod_reconciliation.py 254（EodReconciler :95，run_eod :133，日终 expire_open_orders；**零代码 import 消费方**）｜position_reconciler.py 218（ex_core 侧；**同名双件**：position/position_reconciler.py 在 position 根非 core/——M7-03 B4 未修）
- **脚本面**：scripts/run_post_settlement.py（one-shot：recon→DailyAuditor.audit+VaR 回测→report→exit；延迟 import miniqmt_broker 可降级）｜register_post_settlement_task.ps1（计划任务注册器）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据（本日） |
|---|---|---|
| 15:40 对账槽排班 | 已登记 | schedule.yaml:220-224（cron+唯一入口注记）|
| recon_runner 触发实证 | **未证（在案 L-3）** | 调度器对 eod_reconciliation 槽的解析/执行日志本次未取证（放待裁节）|
| settlement/three_way 消费链 | 已接线（代码面） | recon_runner :87-89 import+run_post_settlement :89 import 双消费方 |
| eod_reconciliation.py 本体 | **码成闸空（零导入）** | grep from zephyr.ex_core.eod_reconciliation 全仓零命中；EodReconciler 功能疑似被 recon_runner 场景互补覆盖（settlement_record_aggregate:25"场景互补"自注）|

### 骨架勘误
总册 F57 行核心模块路径列"settlement_reconciliation.py、three_way_reconciliation.py；ex_core/eod_reconciliation.py"且状态 built——**勘误**：排班真入口=recon_runner.py:392（schedule.yaml 原文），骨架路径漏列 recon_runner.py；eod_reconciliation.py 为零导入的 report/dry-run 语义件（align_to_broker 默认 False），其"built"应注"未被生产 import，场景互补件"。建议骨架本行补 recon_runner.py 锚+eod 件注记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | recon_runner 真触发未证（L-3） | 取调度器 eod 槽执行日志/回执实证；假绿灯交叉尺（C4 收口卷）同批 | P0 |
| 2 | eod_reconciliation.py 零消费 | 处置二选一待裁：①并入 recon_runner 编排（同真源可派生→必并）②头注声明 report 态保留语义 | P1 |
| 3 | position_reconciler 同名双件（ex_core/ vs position/ 根） | 合并或改名+导航注记（0.5 天可施工，M7-03 B4）| P1 |
| 4 | run_post_settlement manual CLI 半接线 | 计划任务注册器在而 schtasks 实态未核（一次性 N/A 任务清理 Owner 门清单相关）| P1 |
| 5 | order_daemon 建成未接线（总册 F82 P0，本环节下游交叉） | 归 M5/SC 车道 | P0（归 F82）|

## 五、自审闸三态
**挖干可施工**（三层对账件全 file:line 实证+排班 yaml 原文锚；缺口 1/2 有明确取证路径与处置选项；eod 零导入为本卷独立新证）。

## 六、复跑命令
```bash
sed -n '213,229p' src/zephyr/data/config/schedule.yaml   # 15:40 槽+唯一入口注记
grep -rn "from zephyr.ex_core.eod_reconciliation" src/zephyr scripts --include="*.py" | grep -v __pycache__   # 零命中=eod 零导入
sed -n '87,89p' src/zephyr/trading/recon_runner.py; sed -n '392,400p' src/zephyr/trading/recon_runner.py
find src/zephyr/position -name "*reconcil*" | grep -v __pycache__   # position 根件（双件之一）
wc -l src/zephyr/trading/settlement_reconciliation.py src/zephyr/trading/three_way_reconciliation.py src/zephyr/ex_core/eod_reconciliation.py
```
