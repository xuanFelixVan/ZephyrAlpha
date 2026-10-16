---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段, gap 节点)
node_id: D13-G03
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-G03 gap：三账差异表恒空且消费方已按恒空设计降级

## 1. 定义

图 13 骨架外 gap 登记位（node_type=gap，wiring=unwired_no_caller，build=pending，⬜）：
reconciliation_differences 差异表自建表以来恒 0 行；写入侧全仓唯一一处 INSERT
（src/zephyr/trading/recon_runner.py:117）其调用链零在位（=D13-29 腿从未产出）；下游判据册已把
"空表不阻断"写死⇒恒空被固化为合规态，"跑过且无差异"与"没跑"不可区分——正是簿 10 表A-A7
点名的 no-drift 留痕缺口。假绿温床另记：门禁/自愈环留痕表（reconcile_execution_log）行数强阳性
而列语义全是提交侧，与资金/持仓/柜台三账零关系（簿 06 假绿专段）。
图内决策问题："差异表 0 行是「今日无差异」还是「核对从未跑成」？下游拿「空表不阻断」当绿灯怎么办？"

## 2. 六向台账

### 2.1 输入面
- 入边：D13-29→D13-G03、D13-31→D13-G03（生产者腿+对账基准腿双入边，map edges）。
- 写入侧：唯一 INSERT 语句 recon_runner.py:117（本批实读命中）——调用链零在位。
- xref：fig12 消费方在等未产表 reconciliation_differences（gap_refs 登记跨图同根）。

### 2.2 输出面
- 产物：恒 0 行表（observed="0 行（自建表以来）"）。
- 消费侧降级设计：回测待办册判据"空表不阻断"（图 12 簿 11 §1-C 消费侧新证）；
  consumers=count:11（code=5,doc=5：src/zephyr/frontend/dashboard/api_server.py:1587、
  src/zephyr/reporting/attribution_result_store.py:38、
  src/zephyr/reporting/prediction_log_writer.py:22、
  src/zephyr/reporting/reconciliation_schema.py:23）。
- fallback=none:恒空即被下游读作"无差异"，无第二条证据路。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-G03（gap/unwired_no_caller/pending/⬜）。
- 表结构真源：src/zephyr/reporting/reconciliation_schema.py:42（CREATE TABLE；
  :23 注释"成交/持仓对账差异（DriftType 5 类+容差口径）"——本批实读命中）。
- 四簿交叉：簿 06（三证）+簿 10（表A-A7 no-drift 缺口）+图 12 簿 11（消费端反查）+骨架 §2
  （骨架外 gap 件）。

### 2.4 代码模块
- module_id=null；module_ref=null（gap 节点无执行体）。
- 关键件：recon_runner.py:117（INSERT，零调用）、reconciliation_schema.py:42（DDL 实存）——
  "有表有语句无调用方"是本 gap 的代码形态。

### 2.5 门禁约束
- 本 gap 是图 laws 第 4 条（槽位挂着≠真在跑）与第 6 条（检出即蒸发不得记为有兜底）的复合判例。
- 下游降级设计使恒空=合规，属"假绿制度化"风险——修复必须同时改生产侧（接线）与消费侧
  （空表语义分级），单侧修复会被另一侧重新吸收为恒空。

### 2.6 自动化触发
- 机制=D_unscheduled；cadence declared="随 D13-29 的 15:40 名义时点（该腿从未产出）"、
  observed="0 行（自建表以来）"；trigger_facts=null；availability=unreachable。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | fail | 双入边均无实流：生产者腿零拍、基准腿（D13-31）零排班 |
| 输出面 | fail | 恒 0 行+下游按恒空降级（空表=绿灯制度化） |
| SSOT 真源 | warn | 表结构与 DriftType 语义在册且实存（schema.py 精确锚），四簿证据链完整——缺的是生产事实非真源 |
| 代码模块 | fail | 唯一 INSERT 零调用方；无任何在位执行体可判活 |
| 门禁约束 | fail | no-drift 留痕缺位（A7）+空表不阻断降级设计=假绿制度化，双 law 复合违例态 |
| 自动化触发 | fail | D_unscheduled、availability=unreachable |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：本格=图 13 自报 4 gap 节点中唯一落在 C/D 段者（G01 在 A 段、
  G02/G04 在 B 段）；同时计入 6 unwired_no_caller。即：图 13"4 gap+11 未接线/空心"共 15 件中
  本段占 3 件=D13-G03（gap+no_caller）、D13-31（no_caller）、D13-29（slot_hollow）。
- 建议 1：双端同改——生产侧接 recon_runner 进 eod_reconciliation 槽（见 SD13-29 建议 1）；
  消费侧把"空表不阻断"改为三态判据（有当日核对心跳行+零差异=pass；无心跳行=unverified 不算
  pass），心跳行即 no-drift 留痕（A7 收口）。
- 建议 2：把 reconcile_execution_log 从本 gap 的假绿证据面除名并在判据册注明
  （列语义=提交侧，与三账无关），防后续挖矿再中招。
- 建议 3：跨图对账：本格与图 12 DSC-15（未接线）+waiting_table_gaps 的
  reconciliation_differences 同根三处登记，收口时三处同批翻转，防单图翻绿。
