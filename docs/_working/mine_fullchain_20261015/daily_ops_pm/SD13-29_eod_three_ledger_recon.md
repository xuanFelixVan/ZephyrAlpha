---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-29
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-29 日终三账核对（柜台/内部/持仓 L1+L2+L3）

## 1. 定义

交易日 15:40（APScheduler 槽 eod_reconciliation），对柜台账/内部账/持仓账做 L1+L2+L3 三账核对，
名义产物=差异表 reconciliation_differences。图内决策问题："15:40 这一拍真跑了三账吗？还是假通道
槽又记了一次 success？"——图硬实查判定：15:40:03 现场捕获"无任务→APScheduler success"；两件三账
实现（MOD-TRADING-013/MOD-L06-003）全仓零调用方；差异表全表 0 行——wiring=unwired_slot_hollow
（本段 11 未接线清单成员）。假绿源已划清：reconcile_execution_log 约 8.8 万行强阳性但列语义全是
提交侧（gate_id/commit_message），与三账零关系，按"有留痕=在跑"判绿即中招。

## 2. 六向台账

### 2.1 输入面
- 入边：D13-28→D13-29（等结算单就绪，map admission 语义由入边承载）。
- 三账原料：柜台账（miniqmt_broker 面 src/zephyr/ex_core/adapters/miniqmt_broker.py:5）、
  内部账、持仓账（D13-27 定周期腿）。
- 实况：15:40 拍时槽内无有效任务（trigger_facts task_runs_30d=0，slot=eod_reconciliation）。

### 2.2 输出面
- 名义产物：c1_market.reconciliation_differences 差异表——自建表以来恒 0 行（环节面见本格，
  恒空问题另立 gap 节点 D13-G03，边 29→G03 在图）。
- failure_visibility（图注）："名义落差异表；实测零行⇒痕迹去向=无（另有同名门禁留痕表强阳性
  而语义不相干）"；downstream_action=none。
- consumers=count:22（code=12：miniqmt_broker.py:5、src/zephyr/reporting/attribution_result_store.py:39、
  src/zephyr/reporting/prediction_log_writer.py:22、src/zephyr/trading/backtest_fills_adapter.py:5）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-29（unwired_slot_hollow/partial/🔨，mining_recheck_status=🌑）。
- 槽声明（现行面）：src/zephyr/data/config/schedule.yaml:248-259——R-015 排班注明"唯一入口=
  src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation（日终核对批，非自愈 reconciler
  环路）"；模块头仍自陈"本模块不挂调度"与已挂 15:40 槽冲突=文档滞后（map evidence 第三条）。
- 簿 06 §D13-29 三证互不依赖（现场捕获+零调用方+零行表）。

### 2.4 代码模块
- module_id=MOD-TRADING-007；module_ref=src/zephyr/trading/recon_runner.py:392
  （def run_daily_reconciliation——锚行精确命中，本批实读确认）。
- 写入侧唯一 INSERT：src/zephyr/trading/recon_runner.py:117（"INSERT INTO reconciliation_differences"，
  本批实读命中；其调用链零在位）。
- 表结构：src/zephyr/reporting/reconciliation_schema.py:42（CREATE TABLE IF NOT EXISTS
  reconciliation_differences）。

### 2.5 门禁约束
- 图 laws 第 4 条"槽位挂着≠真在跑"的本格主判例；false_green_source 在册
  （reconcile_execution_log 强阳性与本环节无关）。
- invalidation：15:40 前该表恒空属预期，非断供证据（须 15:40 后复跑）。
- gap_refs：benchmark:A2/A5/A7 三项缺位+task:eod_reconciliation_daily。
- 宪法 §9.3 事件触发划界：schedule.yaml:250-252 注释自辩"本槽位是定时事实核对，与 L11 同性质"。

### 2.6 自动化触发
- 机制=A_apscheduler；槽=eod_reconciliation cron "40 15 * * 0-4" max_instances=1
  （schedule.yaml:255-259），calendar_guarded=true。
- cadence：declared"交易日 15:40（槽每日 firing）"；observed"名义每日 1 拍；实为 0 拍"
  （trigger_facts task_runs_30d=0）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | fail | 15:40 现场捕获无任务→success；柜台/内部/持仓三账原料无消费发生 |
| 输出面 | fail | reconciliation_differences 恒 0 行；failure_visibility=无 |
| SSOT 真源 | warn | 槽声明与 recon_runner 入口在册（R-015 面），但模块头自陈不挂调度=文档滞后；图判 unwired_slot_hollow |
| 代码模块 | fail | recon_runner.py 实存且锚精确，但两件三账实现全仓零调用方、唯一 INSERT 调用链零在位 |
| 门禁约束 | warn | 假绿源已划清（A2/A5/A7 缺位在册），无兜底（fallback=无 假通道槽） |
| 自动化触发 | fail | 名义每日 firing、30 日窗实跑 0 拍 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：本格=unwired_slot_hollow 五格之一（P0）；其产物恒空衍生 gap 节点
  D13-G03（同段，见 SD13-G03 文档）；与图 12 DSC-15"日终三账对账——未接线"同一根因两图各记
  （裁定#482 正交不并先例）。
- 建议 1：接线动作=把 recon_runner.run_daily_reconciliation 真正挂进 eod_reconciliation 槽任务
  （schedule.yaml 槽面已在，缺的是任务注册/特殊槽编排挂接），并同步修模块头"不挂调度"自陈。
- 建议 2：修复前先把 reconcile_execution_log 从三账判绿证据面除名（防 8.8 万行假阳性继续误导），
  落一条显式 no_drift 留痕（matched/差异计数双零也留行），补 benchmark A7。
- 建议 3：与 D13-G03 联动——差异表新增"核对已跑零差异"心跳行语义，使"跑过且无差异"与
  "没跑"可区分。
