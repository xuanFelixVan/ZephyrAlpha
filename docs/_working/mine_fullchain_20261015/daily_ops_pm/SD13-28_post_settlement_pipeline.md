---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-28
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-28 盘后结算管线（T+1 结算单就绪硬时点）

## 1. 定义

交易日 15:30 硬时点（Windows 计划任务 ZephyrAlpha_PostSettlement，StartWhenAvailable 补火），
盘后结算管线做系统侧核对+日终审计并产出结算单留痕。图内决策问题："15:30 结算单就绪了吗？
QMT 离线时是降级还是伪造券商比对？"——图判定：QMT 离线→显式降级为仅系统侧核对（不伪造）；
柜台侧真实结算单为 🌑-3（模拟账户无经纪商文件），ready_basis=assumed（推定与确认已在字段上分离）。
当日留痕四件同在：trade_date/audit_status=OK/errors 空/exit_code=0（data/runtime/post_settlement_last_run.log）。

## 2. 六向台账

### 2.1 输入面
- 券商/QMT 侧成交回报（外部真源 🌑-4 推定可得）：gap_refs benchmark:A5-ready_basis=assumed。
- 入边：D13-24→28、D13-25→28、D13-26→28、D13-27→28（map edges 四条入边）。
- 降级语义：QMT 离线→仅系统侧核对（fallback 字段在册，不伪造券商比对）。

### 2.2 输出面
- 产物：data/runtime/post_settlement_last_run.log（实存；当日 trade_date、audit_status=OK、
  errors 空、exit_code=0 四件同在）+ 日终审计面。
- consumers=count:30（code=12,doc=16：src/zephyr/trading/boot_hooks.py:232、
  src/zephyr/trading/eod_processor.py:4、src/zephyr/trading/post_settlement_pipeline.py:2、
  docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml:16966）。
- 下游：边 D13-28→D13-29（三账核对等待结算单就绪）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-28（wired/built/✅，production）。
- 簿 06（OK-over-zero 形态登记：空快照最小输入下的 OK 须标注，不得升格为三账证据）。
- 时点契约：scripts/tasks/register/register_post_settlement_task.ps1:14（"15:30 weekday
  wall-clock trigger, cron 30 15 * * *"）；INV-1 撞车面=同硬时点在代码常量另有一处真源
  （gap_refs benchmark:C5，待总包定唯一位）。

### 2.4 代码模块
- module_id=MOD-TRADING-003；module_ref=src/zephyr/trading/post_settlement_pipeline.py:43（实存）。
- 入口脚本：scripts/run_post_settlement.py（实存）；注册器：register_post_settlement_task.ps1
  （:14/:17/:19/:48 命中 15:30+StartWhenAvailable+conhost headless 重定向）。

### 2.5 门禁约束
- casebooks=MEM-F13#结算复活、MEM-F13#计划任务静默。
- 假绿防御：OK-over-zero 形态须标注（空快照 OK 不升格三账证据，簿 06）；
  no_ready_gate_reason 注明前置"券商侧回报可得"为推定（🌑-4）。
- 补火纪律：StartWhenAvailable（机器睡/关机时唤醒后补跑，ps1:19）。

### 2.6 自动化触发
- 机制=B_windows_task；schtasks=ZephyrAlpha_PostSettlement（registered=true+declared=true）。
- trigger_facts：count=1，last_run=2026-10-08T15:30:00（240h 节拍窗）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | warn | 券商侧回报 ready_basis=assumed（外部真源 🌑-4 无确认面）；QMT 离线降级语义已在册 |
| 输出面 | pass | 结算留痕四件同在（log 实存）；consumers 30 条机生在册 |
| SSOT 真源 | warn | 15:30 硬时点两处真源（ps1 触发器+代码常量）未定唯一（INV-1 撞车面在册） |
| 代码模块 | pass | pipeline/run_post_settlement/注册器三件实存，锚行内容命中 |
| 门禁约束 | warn | OK-over-zero 防御依赖人工标注纪律；模拟账户无经纪商文件（🌑-3） |
| 自动化触发 | pass | schtasks 双证+last_run 在窗+补火设置 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内。
- 建议 1：INV-1 撞车面收口——把 15:30 时点收敛为单一真源（注册脚本触发器为准，代码常量改读
  同一常量册），消除双写漂移。
- 建议 2：audit_status=OK 与"系统侧核对完成"的语义分层落字段（ready_basis 已分离，判定面未分离），
  防 OK-over-zero 升格。
