---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-47
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-47 tick 双源一致性比对（QMT 主源 vs TDX 备源）

## 1. 定义

交易日 00:15（跨午夜夜窗；APScheduler 特殊槽 cross_validation，单实例）：CrossSourceValidator
内容级两源一致性校验（价格/成交量/缺失标的），只校验不阻断，结果落 c1_market.cross_validation_log，
fail 经 Alerter 告警。与 L11 integrity_check 分工：L11=行数阈值巡检，本层=内容级两源互查。
图内决策问题："昨交易日 tick 两源对上答案了吗？不一致经谁告警？"——CH 实证（骨架 §7 C 组）：
全表 17,466 行；最近交易日 09-30 全量核对 7,952 行在案（09-28 亦 7,860 行）；10-01..07 国庆假期
无判据（原"10-02 起缺档"系假日误判，2026-10-05 Owner 指正后撤回，10-08 开市复核）。

## 2. 六向台账

### 2.1 输入面
- QMT 主源 tick+TDX 备源 tick（两侧当日已落库为前置，no_ready_gate_reason 承载）。
- 入边：无独立入边（夜窗独立校验层；map edges 无 47 相关边——独立格）。

### 2.2 输出面
- 产物：c1_market.cross_validation_log（17,466 行；逻辑名，表名真源=TableRegistry）。
- fail 路径：经 Alerter 告警（schedule.yaml:186 注记）；downstream_action=detect_only。
- consumers=[]（map 消费者账面为空——同 D13-48 账面缺口）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-47（wiring=partial，build=partial，🔨）。
- 簿 09（假日误判撤回记录+CH 实证）；骨架 §2 D13-47 行。
- 槽契约：src/zephyr/data/config/schedule.yaml:181-191（L11.5，cron "15 0 * * 1-5"，
  2026-10-02 原 23:15 后移 1h 跨午夜错峰）——锚 :187 本批实读精确命中。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/cross_source_validator.py:1（实存，
  "跨源校验器 / cross_source_validator"）。
- 槽面：schedule.yaml:187（cross_validation，max_instances=1）；校验器头注
  CONSUMERS=run_schedule("cross_validation")（schedule.yaml:184 注记）。

### 2.5 门禁约束
- 只校验不阻断（内容级比对边界）；fallback=无（落表即止——fail 腿有 Alerter，pass/零差异无
  no-drift 留痕语义之外的出口）。
- calendar_guarded=true、in_catchup_universe=false（错过无补跑）；假日窗口无判据（误判撤回案例
  在册——判读纪律：假日零行不判缺）。
- casebooks=[]。

### 2.6 自动化触发
- 机制=A_apscheduler 特殊槽；slot=cross_validation cron "15 0 * * 1-5"；machine_facts：
  effective_task_count=0+special_branch_exists=true。
- trigger_facts：task_runs_30d=0（特殊槽无独立计数面）；节拍证据=cross_validation_log 落表面
  （09-30 7,952 行档）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 双源前置+时点错峰在册；假日误判已撤回（判读纪律立） |
| 输出面 | warn | cross_validation_log 有实数据（17,466 行），但 consumers=[] 空账 |
| SSOT 真源 | pass | 图节点+簿 09+槽契约（锚精确）三层齐 |
| 代码模块 | pass | cross_source_validator.py+槽面实存 |
| 门禁约束 | warn | 只校验不阻断+落表即止（fail 有 Alerter，但覆盖语义未分级）；不在补跑宇宙 |
| 自动化触发 | warn | 特殊槽无计数面；节拍靠日志表复核 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（partial，特殊槽编排面正常形态）。
- 建议：consumers 补登（tick 数据治理/数据质量看板侧读取点）；"只校验不阻断"的 fail 告警与
  D13-38 行数告警做去重聚合，防夜窗双通道刷屏。
