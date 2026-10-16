---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-31
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-31 当日回测跑批（对账 L1 基准腿）

## 1. 定义

16:30（D13-30 日K落库）之后应产的当日回测跑批，产物落回测工件目录，作对账 L1 基准腿。
图内决策问题："当日回测今天有人排班吗？没有的话 L1 基准腿从哪来？"——图判定：在位排班=零
（wiring=unwired_no_caller，build=pending，skeleton_status=⬜），唯一真源=已归档日循环 SOP 的
库级调用与显式落盘约定（archived_ssot_only=true）。本格是本段"6 unwired_no_caller"两格之一
（另一格为 gap 节点 D13-G03），也是骨架 P1 收口导向格。

## 2. 六向台账

### 2.1 输入面
- 入边：D13-30→D13-31（图边在册，语义=日K已落库供料）。
- 实况：无槽无任务无调用方——供料关系只存在于图与归档 SOP，无执行体消费该输入。
- gap_refs：benchmark:A4-应产 1 次日回测而排班侧恒 0（无缺席告警主体）。

### 2.2 输出面
- 名义产物：回测工件目录产物（唯一留痕约定=归档件 docs/_archive/57_daily_cycle_sop.md:12）。
- 实况：无落盘面——无排班即无缺席告警主体；downstream_action=none。
- consumers=count:3（全 doc：candidate_module_registry.yaml:7798、
  docs/02_enterprise_architecture/03_governance_reports/candidate_modules/D_BACKTEST.md:21、
  docs/_archive/57_daily_cycle_sop.md:12）——零代码消费者。
- 出边：D13-31→D13-33（图边在册）、D13-31→D13-G03（恒空差异表 gap 关联）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-31（unwired_no_caller/pending/⬜，archived_ssot_only=true）。
- 唯一真源：docs/_archive/57_daily_cycle_sop.md（已归档日循环 SOP——真源位于归档区=降级真源；
  骨架记 GAP-5 转候选件，编号以归档件为准）。
- 候选件登记：docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml:7798、
  docs/02_enterprise_architecture/03_governance_reports/candidate_modules/D_BACKTEST.md:21。

### 2.4 代码模块
- module_id=null；module_ref=null——无在位执行体可挂（本段唯一 module 双空格）。
- 潜在执行体面（本批旁证，非图挂）：src/zephyr/backtest/ 包实存；scheduler.py:219 附近有
  backtest artifact import（get_artifact/list_artifacts）——工件面有 API，无日批调用者。

### 2.5 门禁约束
- 图 laws 第 6 条"看着≠动手"适用：无排班无产物无告警=三无格，禁以任何文档约定判绿。
- failure_visibility（图注）："无落盘面——无排班即无缺席告警主体（归档件的产物目录约定是唯一
  留痕），对账 L1 基准腿因此缺料"；fallback=无（无排班=无缺席告警）；miss_policy=none。

### 2.6 自动化触发
- 机制=D_unscheduled；slot_source=none；cadence declared="16:30 之后，无槽（在位排班=零）"、
  observed="无"；trigger_facts metric=none（无调度无触发计数面）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | fail | 入边仅图面语义，无执行体消费 D13-30 供料 |
| 输出面 | fail | 零产物落盘面、零代码消费者（3 条全 doc） |
| SSOT 真源 | warn | 真源唯一但已归档（archived_ssot_only），候选件在册——真源存在且可追溯，降级不在册 |
| 代码模块 | fail | module_id/module_ref 双空；backtest 包实存但无日批调用链 |
| 门禁约束 | fail | 无缺席告警主体（miss_policy=none、fallback=none）——缺席完全不可见 |
| 自动化触发 | fail | D_unscheduled，无槽无任务无计数面 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：本格=6 unwired_no_caller 之一（段内 stage 格唯一；另一格为 gap 节点
  D13-G03）。图 13 自报 4 gap/6 no_caller/5 hollow 中，本段占 no_caller×2（D13-31+D13-G03）。
- 建议 1：收口路径走候选件通道——D_BACKTEST.md 候选件立项，把归档 SOP 的库级调用约定转为
  dloop_post 圈一段或独立 16:45 后槽，产物落工件目录并留 no_drift 台账行。
- 建议 2：若裁定不做（L1 基准腿由其他面替代），按宪法 §4 内收判据（零触发零消费→退役）把本格
  从图 13 降格为声明性退役格，消除"应产恒 0"的长期红灯。
