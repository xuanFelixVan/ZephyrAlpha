---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-40
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-40 另类宏观日频（假日缺价保守游标自愈）

## 1. 定义

工作日 23:35（APScheduler 槽 daily_alt_fx，单实例上限 1）：ECB 参考汇率日频拉取
（alt_fx_ecb/frankfurter.app，发布≈北京 22:15-23:15 之后），假日缺价由保守游标下一班自愈。
本槽是 L1 上架流水线的首个正门槽位（夜班战役台账 §1.5，schedule.yaml:241 注记）。
图内决策问题："23:35 这一拍的游标自愈了吗？它是 L1 上架流水线的首个正门槽位，排班外它归谁？"

## 2. 六向台账

### 2.1 输入面
- ECB 参考汇率源（外部，发布窗 22:15-23:15 后——23:35 槽点由此定）。
- 入边：D13-39→D13-40（夜窗链，map edges）。

### 2.2 输出面
- 产物：alt_fx_ecb 日频表（schedule.yaml:246 description）。
- consumers=count:4（code=2,config=1,doc=1：
  docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_flow.md:598、
  config/data_supply_chain_map.yaml:394、generate_data_supply_chain_map.py:277、
  generate_trading_day_cycle_map.py:1166）。
- 下游：边 D13-40→D13-44（日界交接供料）；L1-S0 宏观供料（骨架 §2.4 上游行）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-40（wired/partial/🔨）。
- 骨架 §2 D13-40 行（槽注释自证 L1 上架流水线首个正门槽位）；
  docs/_working/map_build/fig13_daycycle/09_夜窗与日界贯穿.md。
- 槽契约：src/zephyr/data/config/schedule.yaml:240-246（cron "35 23 * * 0-4"）；
  map 锚 :194 已漂移（现 Wed catchup_guard 注释行，实际槽在 :242）。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/scheduler.py（实存）；
  槽面 schedule.yaml:242（max_instances=1，executor=default）。

### 2.5 门禁约束
- fallback=无（该槽不在补跑宇宙内）——假日缺价靠保守游标自愈（设计内），非假日断供无兜底。
- gap_refs：task:alt_fx_ecb_daily_incremental。
- casebooks=[]（无案例挂靠）。

### 2.6 自动化触发
- 机制=A_apscheduler；slot=daily_alt_fx；machine_facts：effective_task_count=1、
  calendar_guarded=false、in_catchup_universe=false。
- trigger_facts：task_runs_30d=11（1 任务）——对"交易日每日 1 拍"存在算术差
  （11 vs ~21 交易日），疑注册时点/改点所致，须复扫（同 D13-36 族）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 源窗与时点匹配（23:35 在发布窗后） |
| 输出面 | pass | 表+4 条 consumers+日界交接出边在册 |
| SSOT 真源 | warn | 槽契约实存（:242）但 map 锚漂移（:194→现注释行）；L1 首门槽位为注释自证 |
| 代码模块 | pass | scheduler+槽声明实存 |
| 门禁约束 | warn | fallback=无+不在补跑宇宙（假日游标自愈是设计内兜底，断供无第二路） |
| 自动化触发 | warn | 11 次/30 日窗与"每日 1 拍"算术差未对账 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（wired）。
- 建议：同 D13-36/37——断供哨兵配置面纳入该表（当前哨兵不含，缺价超窗只有 23:00 行数阈值
  间接覆盖）；排班外归属问题（L1 首门槽位）宜在 resource_profile_registry 排班三表落座。
