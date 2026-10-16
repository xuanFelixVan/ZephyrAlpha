---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-37
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-37 夜间财务层（财报/十大股东/融资融券）

## 1. 定义

交易日 22:00（APScheduler heavy 槽 nightly_financial，10 任务挂载）：财报/财务指标/十大股东/
融资融券(T+1) 夜间落库——22:00 由因=次日披露口径此时已发布。图内决策问题："22:00 夜窗跑到几个
任务？当夜漏跑名单有多大？"——已知结构事实（簿 09 §3.1）：23:01 巡检"漏跑"名单同时出现本槽
多数任务，与表侧 max 停在数日前同向（两条独立证据互指）=夜窗部分漏跑实证。

## 2. 六向台账

### 2.1 输入面
- 财报/股东/两融外部源（T+1 披露口径）；入边 D13-36→D13-37、D13-01→D13-37（map edges）。
- fallback 入边：D13-01（daily 桶在册，miss_policy=rerun）。

### 2.2 输出面
- 产物：财报/财务指标/十大股东/融资融券表族（schedule.yaml:123 description）。
- consumers=count:10（code=4,config=1,doc=5：src/zephyr/frontend/dashboard/api_server.py:1624、
  architecture_issue_registry.yaml:17236、data_asset_registry.yaml:7687、
  data_acquisition_flow.md:153）。
- 下游：边 D13-37→D13-38（23:00 巡检覆盖面）；图 12-S3 PIT 派生挂点（骨架 §2.4 D13-37 行
  "+图12-S3"）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-37（wiring=wired，build=partial，🔨）。
- 簿 09 §3.1（漏跑名单两证互指）；骨架 §2 D13-37 行。
- 槽契约：src/zephyr/data/config/schedule.yaml:119-123（cron "00 22 * * 0-4"，executor=heavy）；
  map 锚 :113 现 Wed consensus_crosscheck 行=锚漂移（实际槽在 :120）。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/scheduler.py（实存）；
  effective_task_count=10（machine_facts 实扫）。

### 2.5 门禁约束
- freshness_severity_zh（一档实测）："夜窗漏跑名单来自 23:00 巡检，与表侧水位两因不同级"。
- gap_refs：benchmark:A2 两级未接线、C4 分级归告警系统还是图侧声明（留裁）。
- casebooks=MEM-F13#断供补数；heavy 串行（内存天花板错峰约束，schedule.yaml:96-98 同窗先例）。

### 2.6 自动化触发
- 机制=A_apscheduler；slot=nightly_financial；calendar_guarded=true、in_catchup_universe=true。
- trigger_facts：task_runs_30d=118（10 任务求和，≈12 次/任务 vs ~21 交易日）——与漏跑名单
  两证互指同向，节拍面自证"每日 1 拍"偏乐观。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 源+兜底入边（D13-01 rerun）在册 |
| 输出面 | pass | 表族+10 条 consumers+PIT 派生挂点在册 |
| SSOT 真源 | warn | 槽契约实存（:120）但 map 锚漂移；簿 09 漏跑证据与图 wired 判定并存 |
| 代码模块 | pass | scheduler+10 挂载任务实扫 |
| 门禁约束 | warn | A2 两级未接线+漏跑名单在案——有兜底（rerun）但检测分级未接线 |
| 自动化触发 | warn | 118 次/30 日窗÷10 任务≈12 次/任务，与"每日 1 拍"算术差=部分漏跑的量化痕迹 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（wired），但 23:01 漏跑名单实证表明 wired 判定偏乐观。
- 建议：按簿 09 漏跑名单逐任务对表侧 max 分桶，把长期漏跑任务移出或修源——夜窗 heavy 池
  22:00 窗内存天花板（10GB）错峰方案（同 research_nightly 先例）是现成工具。
