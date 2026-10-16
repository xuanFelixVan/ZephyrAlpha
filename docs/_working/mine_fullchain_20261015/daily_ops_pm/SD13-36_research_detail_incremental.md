---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-36
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-36 研报明细增量层（全市场逐股长批）

## 1. 定义

夜窗首个长批（APScheduler 槽 research_nightly，单实例上限 1）：东财研报中心全字段含预测期
EPS/PE 逐股增量拉取（历史已回补 14.7 万行，日度仅补增量窗）。图内决策问题："夜窗长批起跑了吗？
增量窗补上几行？"——已知结构事实（簿 09 §3.2）：本格断供 4 交易日而断供哨兵配置不含该表
⇒ 唯一覆盖者是 23:00 巡检行数阈值（检测真空是配置面事实）；且该槽不在补跑宇宙内=错过无人补。
时点漂移：schedule.yaml 注记 2026-10-02 RESOURCE-SCHEDULE 错峰已把起跑 20:30 前移至 20:00，
图面 cadence 仍写 20:30。

## 2. 六向台账

### 2.1 输入面
- 东财研报中心源（全市场逐股）；消费前置无（夜窗批独立窗）。
- 入边：D13-35→D13-36（map edges）；入边 D13-01→本格无（fallback=无，不在补跑宇宙）。

### 2.2 输出面
- 产物：research_report_detail_incremental 表（schedule.yaml:104 description 在册）。
- consumers=count:7（code=3,config=1,doc=3：
  docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md:65、
  docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml:131、
  docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_flow.md:162、
  config/data_supply_chain_map.yaml:394）。
- 下游：边 D13-36→D13-37（夜窗批次链）；下游一致性预期管线依赖同源窗（schedule.yaml:109 注记
  consensus 跑在 20:30 研报增量完成后——现时点漂移后该序注记亦过时）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-36（wiring=partial，build=partial，🔨）。
- 簿 09 §3.2（断供 4 交易日+哨兵配置不含该表）；骨架 §2 D13-36 行。
- 槽契约：src/zephyr/data/config/schedule.yaml:96-104——注释声明 20:00 起跑（2026-10-02 错峰
  改：原 20:30 与 nightly_financial/factory_lane_c 同窗并发内存 10.5GB>10GB 天花板），与图面
  declared 20:30 漂移。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/scheduler.py（实存）；
  槽面=schedule.yaml:100（research_nightly，max_instances=1，executor=default）。

### 2.5 门禁约束
- freshness_severity_zh（一档实测）："断供而唯一覆盖者是 23:00 巡检行数阈值（检测真空是配置面
  事实）"；fallback=无（该槽不在补跑宇宙内=错过无人补）。
- gap_refs：benchmark:A2 两级未接线、A4 夜窗长批应产断言未接线、C4 分级归告警系统还是图侧声明
  （留裁）；task:consensus_daily_build、task:research_report_detail_incremental。
- casebooks=MEM-F13#断供补数。

### 2.6 自动化触发
- 机制=A_apscheduler；slot=research_nightly cron "00 20 * * 0-4"（实读；图面 20:30）；
  machine_facts：effective_task_count=2、calendar_guarded=false、in_catchup_universe=false。
- trigger_facts：task_runs_30d=18（2 任务求和）——与"交易日每日 1 拍"自证的算术差未对账
  （18/2=9 次/任务 < 21 交易日），疑与 10-02 错峰改点/任务注册时点相关，须复扫。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 源与窗口独立，前置关系简单（夜窗链首棒） |
| 输出面 | pass | 表+7 条 consumers+夜窗链出边在册 |
| SSOT 真源 | warn | 图面 cadence 20:30 与 schedule.yaml 现 20:00 漂移（2026-10-02 错峰改点未回灌图）；簿 09 断供证据在案 |
| 代码模块 | pass | scheduler+槽声明实存（schedule.yaml:100 精确） |
| 门禁约束 | fail | fallback=无+不在补跑宇宙+哨兵配置不含该表——断供既无兜底也无告警（A2 两级未接线） |
| 自动化触发 | warn | 槽在册但 30 日窗 18 次/2 任务的算术与"每日 1 拍"未对账 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：本格不在 4 gap/6 no_caller/5 hollow 主清单（wiring=partial），
  但门禁向属 A2 两级未接线实质缺口。
- 建议 1：把本表加入 data_supply_sentinel 配置面（config/data_supply_sentinel.yaml）停更阈值
  名单——检测真空是配置面事实，一行配置可收。
- 建议 2：图面 cadence 回灌（20:30→20:00）随下次机生全量重扫自然校正；consensus 前置序注记
  同步改。
