---
ttl: task_bound
completes_when: >-
  排班 v2 §6 端到端验收与 §7 红蓝两轮 0 问题后，本报告作为 P3 期证据归档（内容即终态，无后续维护义务）。
creation_note: P3 收尾报告（CREATE-GUARD token 已随 resource_schedule 前缀批量登记）
---

# P3 AI 第一轮全局重排班·收尾报告（排班 v2 方案 §4-P3）

- 会话：st-govmap-20260915 ｜ 日期：2026-09-17 ｜ 输入：29 条 sched_pool_concurrency block（.runtime/tmp 冲突快照 p3_conflicts_now.json）
- 终态：**block=0，warn=1（co_start 豁免留痕，waived_pair_count=13）**；注册表 79 实体；三角对账（表/真源/schtasks）全一致。

## 1. 错峰腿（apply_resource_plan.py 唯一写回通道，裁定 R-A 工具化）

方案一 `p3_stagger_plan`（5 项，消解 default 池 14 对 block）：

| task_id | 旧窗 | 新窗 | 依据锚点 |
|---|---|---|---|
| data_slot_news_slow | `*/30 * * * *` | `17,47 * * * *` | 移相避开 :0/:5 网格；17/47 不被 3 整除避 event_driven */3 |
| data_slot_daily_crypto | `30 8 * * *` | `41 8 * * *` | 与 pre_market/event_driven 四向同刻解耦 |
| data_slot_pre_market | `30 8 * * 1-5` | `34 8 * * 1-5` | 保 8 点档（9:15 前收工），给 crypto :41 让刻 |
| data_slot_monthly_static | `0 9 1 * *` | `16 9 1 * *` | 避 pattern_mining 09:00 月初同刻 |
| sch_f06_grid | `0 14 * * 6` | `0 23 * * 6` | C-8 旗舰案例：与 sch_c4_exam（周六 14:00+480min=22:00）物理解耦 |

方案二 `p3_stagger_plan2`（1 项）：`sch_pattern_mining` `0 9 * * *` → `1 9 * * *`——
最后一个 default 池 block（event_driven */3 × pattern_mining 9:00 同刻）；9:01 不在 */3
命中集（0,3,…,57），单分钟平移即结构性消解。

落地存档：`.runtime/sessions/p2b-apply-resource-plan/archive/plan_20260916T225952Z`、
`plan_20260916T230659Z`（首落）与 `plan_20260916T234709Z`、`plan_20260916T234723Z`（§4 事故后重放）。
OS 侧联动：`register_f06_grid_task.ps1` / `register_pattern_mining_task.ps1` 改窗后已重注册，
实测 `ZephyrAlpha_F06Grid` Ready（NextRun 2026-09-19 23:00）、`ZephyrAlpha_PatternMining`
Ready（NextRun 2026-09-17 09:01）。

## 2. 声明腿（裁定 R-F：co_start_intent）

realtime 池残余 13 对全部来自盘中行情时钟共生车道（auction_highfreq 9:15-9:25 每分钟触发，
分钟级错峰数学上不可行）。按 R-F：双方均声明 `co_start_intent: true` 才豁免判据①（同刻
开工），判据②内存预算永不豁免（该 13 对实测和 1.5-2.0GB << 10GB ceiling）。6 实体声明：
`data_slot_auction_highfreq / data_slot_intraday_minute / data_slot_intraday_realtime /
data_slot_intraday_sector / sch_paper_session / sch_intraday_fund_flow`，每条 notes_zh 附
[R-F] 理由；生成器配套臂 `co_start_declared_without_notes` 防"只翻开关不写账"，
`_HUMAN_FIELDS` 收编 co_start_intent 保证再生保全。闸侧（d3b6518f47）豁免出 warn Finding
`kind=co_start_intent_waived` + waived_pair_count 计数，审计板可见。

## 3. 两项销项

- **PatternMining 幽灵登记**：ps1 真挂上系统（Ready/每日 09:01），SCHED_TASK_EXEMPTIONS
  条目删除（销项留注释），regen_check 期望集同步。
- **WeeklyRest 建模**（原移交 P3 的 blackout 窗议题）：裁定=ops 一等实体
  `ops_weekly_rest` + 新组标 `machine_blackout`（GROUPS 登记"可见性而非互斥"）+
  `OPS_TASK_ALIASES["ZephyrAlpha_WeeklyRest"]` 收编，豁免条目删除。关机由 OS 强制，
  表侧职责=晨报/周历可见；wt=manual 不入同刻账（避免永久审计噪声）。

## 4. 事故记录：未 claim 编辑被 flush 回滚两次（流程债→纪律修正）

07:25 与 07:40:18 两轮"批量还原+msg 文件删除"（worktree_drift_watchdog 记
`claimed_by=""→grace_suppressed`），根因=编辑期未持 claim，unclaimed dirty 文件被
workspace flush 收编还原。修正：**claim-first**——本批全部落盘文件先
`lock_files.py acquire <f> st-govmap-20260915 --ttl 5400` 再编辑，提交窗口不释放。
P2-c 连坐：`429b68783b` 落地时 capacity_budget.py 的修改恰被 flush 还原，形成
"测试已入库/源码未入库"红灯半批，本会话以 `_normalize_key` 重建补齐（55 passed）。

## 5. 残余（登记不落账原因）

- 4 条实验遗留 OS 任务（C4Exam_Full0916/OneShot0915、FactoryLaneC_Full0916/OneShot0915）
  + NightlySentiment 退役残余：删除=Owner 门位，豁免留痕在册。
- qmt/bdpan 手动-vs-Ready 状态漂移、AltFxECB 外来孤儿：非本臂差集（他线在途，§3.4 不代修）。
