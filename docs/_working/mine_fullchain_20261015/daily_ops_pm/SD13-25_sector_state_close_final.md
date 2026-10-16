---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-25
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-25 板块状态盘后定格（真源态）

## 1. 定义

交易日 15:10（与 D13-26 同分钟），板块状态管线盘后腿把当日板块状态五成分截面以
`stage=close_final` 落库（c1_market.sector_state），作为 T 日板块域"真源态"，供次日盘前
D13-10（sector_pre_open 复制+偏好重映射）消费。图内决策问题："15:10 定格的态是 T 日还是
T-1 日？"——图已改判为结构性"恒 T-1"（15:10 时当日日线未入库，16:30 才产；若 16:30 后复跑
该腿则断言作废）。特殊槽分支（sector 双槽合一），总闸=data/runtime/sector_state_pipeline.disabled。

## 2. 六向台账

### 2.1 输入面
- 图边 D13-19（板块资金流日内五快照）→ D13-25（config/trading_day_cycle_map.yaml#edges）。
- 盘中板块状态累积面：src/zephyr/data/sector_state_pipeline.py（盘后腿=close_final 定格）。
- 证据：map 节点 D13-25 note_zh"特殊槽分支（sector 双槽合一）→ 板块状态管线盘后腿"。

### 2.2 输出面
- 产物：c1_market.sector_state（stage=close_final 行）； consumers=count:4（code=2,config=1,doc=1，
  含 docs/03_modules/_cross_layer/database/business_data_categories.yaml:5534、
  config/data_supply_chain_map.yaml:1131）。
- 下游：D13-28（边 25→28）；次日 D13-10 sector_pre_open 复制（schedule.yaml:309-313）。
- 缺席后果（图注）：fallback=无——缺则 D13-10 次日无源。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-25（wiring=partial，build=partial，skeleton_status=🔨）。
- docs/_working/map_build/fig13_daycycle/00_skeleton.md §2 D13-25（契约行）。
- docs/_working/map_build/fig13_daycycle/06_盘后结算与三账.md（簿 06 §D13-25：恒 T-1 改判）。

### 2.4 代码模块
- module_id=MOD-SIG-026 supplement；module_ref=src/zephyr/data/sector_state_pipeline.py:164
  （文件实存；:164 当前行内容=`return None`，锚行内容对不上=锚漂移）。
- 槽声明：src/zephyr/data/config/schedule.yaml:304 `sector_close_final` cron "10 15 * * 0-4"
  （map 锚 scheduler.py:439 当前行内容为裸括号，弱锚）。

### 2.5 门禁约束
- 特殊槽编排型调用防 R-021 假通道（scheduler._run_special_schedule 硬编码白名单两侧同挂，
  schedule.yaml:269-270 先例注记）；总闸 data/runtime/sector_state_pipeline.disabled（每次触发实查）。
- 图 laws 第 4 条"槽位挂着≠真在跑"适用：task_runs_30d=0（slot=sector_close_final 任务级求和×0，
  data/integrator_progress.db:task_runs）——特殊槽不写该计数面，须以产物表行数判活。
- 图 laws 第 5 条：ready_gate=false 且 no_ready_gate_reason_zh 在册（非就绪门格）。

### 2.6 自动化触发
- 机制=A_apscheduler；槽=sector_close_final（15:10，max_instances=1）；特殊槽分支实存
  （machine_facts.slot_facts.special_branch_exists=true）。
- 节拍：declared"交易日 15:10（与 D13-26 同分钟）"；observed"交易日每日 1 拍"；
  trigger_facts 计数=0（特殊槽无独立计数面）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 入边 19→25 在图；sector_state_pipeline.py 实存 |
| 输出面 | warn | sector_state close_final 态窗内行数只覆盖 2 个交易日、缺 1 日（骨架 §2 证据行）；fallback=无 |
| SSOT 真源 | pass | 图节点+簿 06+骨架三层齐；恒 T-1 已结构改判 |
| 代码模块 | warn | 文件实存但 source_anchors 两处行号内容均对不上（:164=return None、scheduler.py:439=裸括号） |
| 门禁约束 | pass | 特殊槽防假通道+总闸惯例在册；ready_gate 声明完整 |
| 自动化触发 | warn | 槽在册（schedule.yaml:304）但 task_runs 计数面恒 0（特殊槽不计数），节拍只能靠产物表复核 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内（wiring=partial 属一般性部分接线）。
- 建议 1：锚漂移——map source_anchors 的 sector_state_pipeline.py:164 与 scheduler.py:439 行内容
  与当前文件不符（schedule.yaml 整体后移后 scheduler 行号漂移），重扫机生层即可校正。
- 建议 2：close_final 覆盖缺 1 交易日，与"恒 T-1"结论同向，宜在产物表上加交易日覆盖 diff
  （复用 D13-03 日历逐日 diff 机制）。
