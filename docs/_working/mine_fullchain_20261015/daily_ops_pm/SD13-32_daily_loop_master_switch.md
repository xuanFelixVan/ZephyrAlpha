---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-32
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-32 日循环总扳手（全链多段排班编排）★本图最大节点

## 1. 定义

交易日 16:45（APScheduler 特殊槽 dloop_post，cron "45 16 * * 0-4"），日循环总扳手
（src/zephyr/plan_engine/daily_loop_master_switch.py）以 run_daily_loop(None) 全链编排四相段
（PHASE_STAGES 实扫：盘前族/盘中族/盘后族/夜窗族，段序契约见 dloop_stages 面），观察记录模式
零下单（裁定#305 安全态）。图内决策问题："16:45 这一圈把几段跑完了？哪几段是空转？输入日是
T 还是 T-1？"——三证齐（槽+段序实扫+当日拍板表在产）；总闸实存扫=不存在（开着）。
已知结构事实：缺当日主行情（D13-30 未过门）则整圈在 T-1 上重放且仍记 SUCCESS（fail-closed
唯二腿之一，admission edge D13-30→D13-32）；幂等全命中时两圈耗时差一个量级="跑了≠重算了"。

## 2. 六向台账

### 2.1 输入面
- 就绪门入边：D13-30→D13-32（admission edge，data_readiness 前置）。
- 业务日解析：run_daily_loop(None) 无参自动解析最新业务日（schedule.yaml:291 注记）。
- consumers=count:19（code=6：src/zephyr/pf_alloc/allocation_inputs.py:206、
  src/zephyr/plan_engine/daily_loop_master_switch.py:2、
  src/zephyr/position/core/position_checkup_orchestrator.py:5、
  capability_canonical_file_registry.yaml:42698）。

### 2.2 输出面
- 编排产物：四相段逐段留痕（fail-open 逐段记录；唯二 fail-closed 在段内）+日度判定表供料
  （D13-34 decision 段）。
- 回头驱动回边（feedback_loops 五条）：→D13-21/22/23（盘中族段在 16:45 圈被回头驱动，段界折叠）、
  →D13-20（墙钟窗闸段恒窗外，产出恒 skipped）、→D13-09（盘前族段实跑在 16:45 圈，T+1 预产腿
  溢出，簿 07 E-3）。
- 幂等证据：两圈耗时差一个量级=幂等全命中空转的量化实证（簿 07 §1.6）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-32（wired/built/✅，production）。
- 簿 07：docs/_working/map_build/fig13_daycycle/07_dloop十六段解剖.md（16 段解剖真源）。
- 槽契约：src/zephyr/data/config/schedule.yaml:288-299（原 MANUAL-ONLY 经 Owner 批准解除，
  2026-09-21 st-dloop-20260921；总闸=data/runtime/daily_loop_master.disabled）。
- 运行时证据：data/runtime/daily_loop_master.disabled（不存在=总闸开着，exec_evidence 复跑路径）。

### 2.4 代码模块
- module_id=MOD-PLAN-033；module_ref=src/zephyr/plan_engine/daily_loop_master_switch.py:337/:402
  （实存；本批实读：PHASE_STAGES 实际声明于 :393，锚 337/402 行内容为段内字典行——锚小幅漂移
  但模块与四相结构命中）。
- 段派生面：GRADUATED_PACKAGES 安全态常量 :46（"拍板体写 decision_daily 快照行但
  GRADUATED_PACKAGES 恒空（裁定#305）→ 结构性无实盘行为"，本批实读命中）。

### 2.5 门禁约束
- 零下单安全态（裁定#305）：全链观察记录模式，下单动作归 TDM L4/X-S2（图 boundary 第 1 条）。
- fail-open 逐段留痕、唯二 fail-closed（data_readiness 腿+墙钟窗闸段）；可安全重跑（幂等=
  prediction_log UNIQUE/台账查重/业务日记号，schedule.yaml:292）。
- 周末 cron 排除；法定假日空跑由底层幂等闸+数据就绪门吸收（schedule.yaml:294）。
- casebooks=DCS#队列（low）。

### 2.6 自动化触发
- 机制=A_apscheduler 特殊槽编排型；slot=dloop_post（cron "45 16 * * 0-4"，max_instances=1）；
  machine_facts：effective_task_count=0+special_branch_exists=true（特殊槽不入 tasks.yaml，
  防 R-021 假通道白名单两侧同挂）。
- trigger_facts：task_runs_30d=0（特殊槽不写计数面）——节拍证据靠槽 firing 与段产物复核，
  不靠 task_runs（图 laws 第 4 条判定纪律的又一次应用）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | run_daily_loop(None) 业务日自动解析+就绪门入边在册；invalidation 判据清晰（16:45 前无产物属正常） |
| 输出面 | pass | 五条回头驱动回边+段留痕+日度拍板供料全在图；consumers 19 条 |
| SSOT 真源 | pass | 图节点+簿 07+槽契约（Owner 批注解除 MANUAL-ONLY 在案）+总闸惯例四层齐 |
| 代码模块 | pass | daily_loop_master_switch.py 实存，PHASE_STAGES(:393)/GRADUATED_PACKAGES(:46) 实读命中；锚行小幅漂移 |
| 门禁约束 | pass | 裁定#305 零下单+幂等+fail-open/fail-closed 边界全部在册 |
| 自动化触发 | warn | 特殊槽不写 task_runs（计数面 0）——"在跑"证据须靠段产物表复核，缺自动化节拍证明 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内（wired/built，C 段最大节点）。
- 建议 1：T-1 重放假绿收口——data_readiness 腿是唯二 fail-closed 之一，但"缺料整圈 T-1 重放仍记
  SUCCESS"说明 fail-closed 只挡重算不挡记录；建议圈报告增加 input_trade_date 字段与
  max(kline trade_date) 对账行，T-1 重放在台账显形。
- 建议 2：特殊槽节拍计数——给 dloop_post 圈落一行圈级心跳（圈号/段清单/耗时），既补 task_runs=0
  的计数面空缺，又给幂等空转率（耗时差量级）提供台账。
